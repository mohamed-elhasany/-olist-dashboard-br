# pages/9_📊_Delivery_Performance.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Delivery Performance | Olist Dashboard",
    page_icon="📊",
    layout="wide"
)

# Apply theme
try:
    import theme
    theme.inject()
except:
    st.warning("Theme module not found. Using default styling.")

# ======================= PERFORMANCE OPTIMIZATIONS =======================

@st.cache_data(ttl=3600)
def get_delivery_performance_analysis(orders_data):
    """Cached delivery performance analysis - optimized for this page only"""
    
    # Create a copy to avoid modifying original
    perf_data = orders_data.copy()
    
    # Convert datetime columns if they're strings
    datetime_cols = ['order_purchase_timestamp', 'order_delivered_customer_date',
                    'order_estimated_delivery_date']
    
    for col in datetime_cols:
        if col in perf_data.columns:
            if perf_data[col].dtype == 'object':  # If it's a string
                perf_data[col] = pd.to_datetime(perf_data[col], errors='coerce')
    
    # Calculate delivery metrics
    perf_data['Delay'] = perf_data['order_estimated_delivery_date'] - perf_data['order_delivered_customer_date']
    
    # Simplified delivery status
    if 'order_status' in perf_data.columns:
        perf_data['Net_State'] = perf_data['order_status'].apply(
            lambda x: 'Delivered' if x == 'delivered' else 'Not_Delivered'
        )
    else:
        perf_data['Net_State'] = 'Delivered'  # Default if status not available
    
    # Categorize orders
    delivered_orders = perf_data[perf_data['Net_State'] == 'Delivered'].copy()
    not_delivered_orders = perf_data[perf_data['Net_State'] == 'Not_Delivered'].copy()
    
    # Calculate performance metrics for delivered orders
    if len(delivered_orders) > 0:
        delivered_orders['is_delayed'] = delivered_orders['Delay'] < pd.Timedelta(0)
        delivered_orders['is_early'] = delivered_orders['Delay'] > pd.Timedelta(0)
        delivered_orders['is_on_time'] = delivered_orders['Delay'] == pd.Timedelta(0)
        
        # Convert delay to days for analysis
        delivered_orders['delay_days'] = delivered_orders['Delay'].dt.total_seconds() / (24 * 3600)
        
        # Calculate key metrics
        total_delivered = len(delivered_orders)
        on_time_delivered = delivered_orders['is_on_time'].sum()
        early_delivered = delivered_orders['is_early'].sum()
        delayed_delivered = delivered_orders['is_delayed'].sum()
        
        performance_metrics = {
            'total_orders': len(perf_data),
            'total_delivered': total_delivered,
            'total_not_delivered': len(not_delivered_orders),
            'delivery_rate': (total_delivered / len(perf_data) * 100) if len(perf_data) > 0 else 0,
            'on_time_delivered': on_time_delivered,
            'early_delivered': early_delivered,
            'delayed_delivered': delayed_delivered,
            'on_time_rate': (on_time_delivered / total_delivered * 100) if total_delivered > 0 else 0,
            'early_rate': (early_delivered / total_delivered * 100) if total_delivered > 0 else 0,
            'delay_rate': (delayed_delivered / total_delivered * 100) if total_delivered > 0 else 0,
            'avg_delay_days': abs(delivered_orders['delay_days'].mean()) if delayed_delivered > 0 else 0,
            'median_delay_days': abs(delivered_orders['delay_days'].median()) if delayed_delivered > 0 else 0
        }
        
        # Calculate SLA compliance
        if 'delay_days' in delivered_orders.columns:
            # Define SLA tiers
            sla_tiers = {
                'Within 1 day': (delivered_orders['delay_days'] >= -1) & (delivered_orders['delay_days'] <= 0),
                '1-3 days late': (delivered_orders['delay_days'] < -1) & (delivered_orders['delay_days'] >= -3),
                '3-7 days late': (delivered_orders['delay_days'] < -3) & (delivered_orders['delay_days'] >= -7),
                'More than 7 days late': delivered_orders['delay_days'] < -7,
                'Early delivery': delivered_orders['delay_days'] > 0
            }
            
            sla_compliance = {}
            for tier_name, condition in sla_tiers.items():
                count = condition.sum()
                sla_compliance[tier_name] = {
                    'count': count,
                    'percentage': (count / total_delivered * 100) if total_delivered > 0 else 0
                }
        else:
            sla_compliance = {}
    else:
        performance_metrics = {
            'total_orders': len(perf_data),
            'total_delivered': 0,
            'total_not_delivered': len(not_delivered_orders),
            'delivery_rate': 0,
            'on_time_delivered': 0,
            'early_delivered': 0,
            'delayed_delivered': 0,
            'on_time_rate': 0,
            'early_rate': 0,
            'delay_rate': 0,
            'avg_delay_days': 0,
            'median_delay_days': 0
        }
        sla_compliance = {}
    
    return {
        'perf_data': perf_data,
        'delivered_orders': delivered_orders if 'delivered_orders' in locals() else pd.DataFrame(),
        'not_delivered_orders': not_delivered_orders,
        'performance_metrics': performance_metrics,
        'sla_compliance': sla_compliance,
        'orders_data': perf_data
    }

# ======================= HELPER FUNCTIONS =======================

def create_delivery_status_chart(performance_metrics):
    """Create donut chart for delivery status"""
    
    labels = ['Delivered', 'Not Delivered']
    values = [performance_metrics['total_delivered'], performance_metrics['total_not_delivered']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=['#2A927A', '#8B4513'],
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>' +
                     'Count: %{value:,}<br>' +
                     'Percentage: %{percent}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Delivery Status Overview',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def create_delivery_timeliness_chart(performance_metrics):
    """Create stacked bar chart for delivery timeliness"""
    
    if performance_metrics['total_delivered'] == 0:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'No Delivered Orders',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400
        )
        return fig
    
    categories = ['On Time', 'Early', 'Delayed']
    counts = [
        performance_metrics['on_time_delivered'],
        performance_metrics['early_delivered'],
        performance_metrics['delayed_delivered']
    ]
    percentages = [
        performance_metrics['on_time_rate'],
        performance_metrics['early_rate'],
        performance_metrics['delay_rate']
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=counts,
        marker_color=['#2A927A', '#2C7D8B', '#8B4513'],
        text=[f'{p:.1f}%' for p in percentages],
        textposition='auto',
        textfont=dict(color='white', size=12),
        hovertemplate='<b>%{x}</b><br>' +
                     'Count: %{y:,}<br>' +
                     'Percentage: %{text}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Delivery Timeliness Performance',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Timeliness Category',
        yaxis_title='Number of Orders',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        showlegend=False
    )
    
    return fig

def create_sla_compliance_chart(sla_compliance):
    """Create horizontal bar chart for SLA compliance"""
    
    if not sla_compliance:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'No SLA Compliance Data',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400
        )
        return fig
    
    # Prepare data for chart
    tiers = list(sla_compliance.keys())
    percentages = [sla_compliance[tier]['percentage'] for tier in tiers]
    counts = [sla_compliance[tier]['count'] for tier in tiers]
    
    # Color mapping based on tier
    tier_colors = {
        'Within 1 day': '#2A927A',
        '1-3 days late': '#C9D2BA',
        '3-7 days late': '#8B4513',
        'More than 7 days late': '#8B0000',
        'Early delivery': '#2C7D8B'
    }
    
    colors = [tier_colors.get(tier, '#2C7D8B') for tier in tiers]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=percentages,
        y=tiers,
        orientation='h',
        marker_color=colors,
        text=[f'{p:.1f}% ({c:,})' for p, c in zip(percentages, counts)],
        textposition='auto',
        textfont=dict(color='white', size=10),
        hovertemplate='<b>%{y}</b><br>' +
                     'Percentage: %{x:.1f}%<br>' +
                     'Count: %{customdata:,}<br>' +
                     '<extra></extra>',
        customdata=counts
    ))
    
    fig.update_layout(
        title={
            'text': 'SLA Compliance Analysis',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Percentage of Delivered Orders',
        yaxis_title='SLA Tier',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        margin=dict(l=150, r=50, t=80, b=50),
        yaxis=dict(
            categoryorder='total ascending',
            tickfont=dict(size=11)
        )
    )
    
    return fig

def create_performance_trend_chart(perf_data, metric='delivery_rate', window=7):
    """Create trend chart for performance metrics over time"""
    
    if len(perf_data) == 0:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'No Data Available',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400
        )
        return fig
    
    # Ensure date column is datetime
    if 'order_purchase_timestamp' in perf_data.columns:
        if perf_data['order_purchase_timestamp'].dtype == 'object':
            perf_data['order_purchase_timestamp'] = pd.to_datetime(
                perf_data['order_purchase_timestamp'], errors='coerce'
            )
        
        perf_data['purchase_date'] = perf_data['order_purchase_timestamp'].dt.date
        
        # Calculate daily metrics
        daily_stats = perf_data.groupby('purchase_date').agg(
            total_orders=('order_id', 'nunique'),
            delivered_orders=('Net_State', lambda x: (x == 'Delivered').sum())
        ).reset_index().sort_values('purchase_date')
        
        # Calculate rates
        daily_stats['delivery_rate'] = (daily_stats['delivered_orders'] / daily_stats['total_orders'] * 100).fillna(0)
        
        # For delay rate, need delivered orders with delay data
        if 'Delay' in perf_data.columns:
            delivered_daily = perf_data[perf_data['Net_State'] == 'Delivered'].groupby('purchase_date').agg(
                delayed_orders=('Delay', lambda x: (x < pd.Timedelta(0)).sum() if hasattr(x, 'dtype') and x.dtype != 'object' else 0)
            ).reset_index()
            
            daily_stats = daily_stats.merge(delivered_daily, on='purchase_date', how='left')
            daily_stats['delay_rate'] = (daily_stats['delayed_orders'] / daily_stats['delivered_orders'] * 100).fillna(0)
        else:
            daily_stats['delay_rate'] = 0
        
        # Calculate rolling average
        if metric in daily_stats.columns:
            daily_stats[f'{metric}_roll'] = daily_stats[metric].rolling(window, min_periods=1).mean()
            
            # Metric labels
            metric_labels = {
                'delivery_rate': 'Delivery Rate',
                'delay_rate': 'Delay Rate'
            }
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_stats['purchase_date'],
                y=daily_stats[f'{metric}_roll'],
                mode='lines',
                line=dict(
                    color='#2C7D8B' if metric == 'delivery_rate' else '#8B4513',
                    width=3
                ),
                name=metric_labels.get(metric, metric),
                hovertemplate='Date: %{x|%Y-%m-%d}<br>' +
                             f'{metric_labels.get(metric, metric)}: %{{y:.1f}}%<br>' +
                             'Total Orders: %{customdata[0]:,}<br>' +
                             'Delivered Orders: %{customdata[1]:,}<br>' +
                             '<extra></extra>',
                customdata=daily_stats[['total_orders', 'delivered_orders']].values
            ))
            
            fig.update_layout(
                title=f'{metric_labels.get(metric, metric)} Trend ({window}-day average)',
                xaxis_title='Date',
                yaxis_title=f'{metric_labels.get(metric, metric)} (%)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333333'),
                height=400,
                showlegend=False,
                hovermode='x unified'
            )
            
            return fig
    
    # Return empty figure if no date data
    fig = go.Figure()
    fig.update_layout(
        title={
            'text': 'No Date Data Available',
            'x': 0.5,
            'xanchor': 'center'
        },
        height=400
    )
    return fig

# ======================= PAGE INITIALIZATION =======================

def initialize_page():
    """Initialize the delivery performance page"""
    
    # Check if data is loaded
    if not st.session_state.get('data_loaded', False):
        st.error("⚠️ Data not loaded. Please go to the Home page and click 'Load All Data'.")
        st.stop()
    
    if st.session_state.orders is None:
        st.error("❌ Orders data not available. Please reload data from Home page.")
        st.stop()
    
    # Initialize delivery performance analysis with caching
    if 'delivery_performance' not in st.session_state:
        with st.spinner("📊 Analyzing delivery performance..."):
            results = get_delivery_performance_analysis(st.session_state.orders)
            st.session_state.delivery_performance = results
    
    return st.session_state.delivery_performance

# ======================= MAIN PAGE CONTENT =======================

def main():
    """Main content for Delivery Performance page"""
    
    # Page header
    st.markdown("""
    <h1 class="main-text">📊 Delivery Performance</h1>
    <p class="sub-text">Comprehensive analysis of delivery success, timeliness, and SLA compliance</p>
    """, unsafe_allow_html=True)
    
    # Quick navigation
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <p style="color: var(--dark-text-secondary); margin: 0;">
            🔍 <b>Related Analysis:</b> 
            <a href="/⏱️_Order_Timelines" style="color: var(--dark-text-cool);">Order Timelines</a> • 
            <a href="/🚨_Delay_Analysis" style="color: var(--dark-text-cool);">Delay Analysis</a> • 
            <a href="/📍_Geographic_Analysis" style="color: var(--dark-text-cool);">Geographic Analysis</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize data
    analysis_data = initialize_page()
    performance_metrics = analysis_data['performance_metrics']
    sla_compliance = analysis_data['sla_compliance']
    perf_data = analysis_data['perf_data']
    
    # ======================= PERFORMANCE OVERVIEW =======================
    
    st.markdown('<h2 class="main-text">📊 Performance Overview</h2>', unsafe_allow_html=True)
    
    # Check if we have delivery data
    if performance_metrics['total_delivered'] == 0:
        st.warning("""
        ⚠️ **No Delivered Orders Found**
        
        This analysis requires delivered orders to calculate performance metrics.
        No delivered orders were found in the dataset.
        
        Basic order statistics are still available below.
        """)
    
    # Key performance metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Orders",
            value=f"{performance_metrics['total_orders']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Delivery Rate",
            value=f"{performance_metrics['delivery_rate']:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            label="On-Time Rate",
            value=f"{performance_metrics['on_time_rate']:.1f}%",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Delay Rate",
            value=f"{performance_metrics['delay_rate']:.1f}%",
            delta=None
        )
    
    with col5:
        avg_delay = performance_metrics['avg_delay_days']
        st.metric(
            label="Avg Delay",
            value=f"{avg_delay:.1f} days" if avg_delay > 0 else "N/A",
            delta=None
        )
    
    # Performance summary
    st.markdown("### 🎯 Performance Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        delivered_color = "#2A927A" if performance_metrics['delivery_rate'] >= 90 else \
                         "#C9D2BA" if performance_metrics['delivery_rate'] >= 80 else "#8B4513"
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 2px solid {delivered_color}; 
                    border-radius: 8px; padding: 1.5rem; text-align: center;">
            <div style="font-size: 2rem; color: {delivered_color}; font-weight: 600;">
                {performance_metrics['delivery_rate']:.1f}%
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 1rem;">
                Delivery Success Rate
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                {performance_metrics['total_delivered']:,} of {performance_metrics['total_orders']:,} orders
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        on_time_color = "#2A927A" if performance_metrics['on_time_rate'] >= 80 else \
                       "#C9D2BA" if performance_metrics['on_time_rate'] >= 70 else "#8B4513"
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 2px solid {on_time_color}; 
                    border-radius: 8px; padding: 1.5rem; text-align: center;">
            <div style="font-size: 2rem; color: {on_time_color}; font-weight: 600;">
                {performance_metrics['on_time_rate']:.1f}%
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 1rem;">
                On-Time Delivery Rate
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                {performance_metrics['on_time_delivered']:,} of {performance_metrics['total_delivered']:,} delivered
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        sla_score = 100 - performance_metrics['delay_rate']
        sla_color = "#2A927A" if sla_score >= 90 else \
                   "#C9D2BA" if sla_score >= 80 else "#8B4513"
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 2px solid {sla_color}; 
                    border-radius: 8px; padding: 1.5rem; text-align: center;">
            <div style="font-size: 2rem; color: {sla_color}; font-weight: 600;">
                {sla_score:.1f}%
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 1rem;">
                SLA Compliance Score
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                Based on delivery timeliness
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= DELIVERY VISUALIZATIONS =======================
    
    st.markdown('<h2 class="main-text">📈 Delivery Performance Visualizations</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Delivery status chart
        fig_status = create_delivery_status_chart(performance_metrics)
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Delivery timeliness chart
        fig_timeliness = create_delivery_timeliness_chart(performance_metrics)
        st.plotly_chart(fig_timeliness, use_container_width=True)
    
    # SLA Compliance chart
    if sla_compliance:
        st.markdown("### ⏱️ SLA Compliance Analysis")
        
        fig_sla = create_sla_compliance_chart(sla_compliance)
        st.plotly_chart(fig_sla, use_container_width=True)
        
        # SLA insights
        within_1_day = sla_compliance.get('Within 1 day', {'percentage': 0})
        early_delivery = sla_compliance.get('Early delivery', {'percentage': 0})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Within SLA (±1 day)</div>
                <div style="color: #2A927A; font-size: 1.5rem; font-weight: 600;">
                    {within_1_day['percentage']:.1f}%
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">
                    {within_1_day['count']:,} orders
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Early Deliveries</div>
                <div style="color: #2C7D8B; font-size: 1.5rem; font-weight: 600;">
                    {early_delivery['percentage']:.1f}%
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">
                    {early_delivery['count']:,} orders
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            severe_delay = sla_compliance.get('More than 7 days late', {'percentage': 0})
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Severe Delays (>7 days)</div>
                <div style="color: #8B0000; font-size: 1.5rem; font-weight: 600;">
                    {severe_delay['percentage']:.1f}%
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">
                    {severe_delay['count']:,} orders
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= PERFORMANCE TRENDS =======================
    
    st.markdown('<h2 class="main-text">📅 Performance Trends</h2>', unsafe_allow_html=True)
    
    # Trend controls
    col1, col2 = st.columns(2)
    
    with col1:
        trend_metric = st.selectbox(
            "Performance Metric to Track",
            ["delivery_rate", "delay_rate"],
            help="Select which performance metric to analyze over time"
        )
    
    with col2:
        smoothing_window = st.slider(
            "Trend Smoothing (days)",
            min_value=1,
            max_value=30,
            value=14,
            help="Rolling average window for smoothing trends"
        )
    
    # Create performance trend chart
    fig_trend = create_performance_trend_chart(
        perf_data, 
        metric=trend_metric,
        window=smoothing_window
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Trend insights
    metric_name = "Delivery Rate" if trend_metric == "delivery_rate" else "Delay Rate"
    target_value = 95 if trend_metric == "delivery_rate" else 5
    
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1.5rem; margin: 1rem 0;">
        <h4 class="warm-text" style="margin-top: 0;">🎯 {metric_name} Insights</h4>
        <ul style="color: var(--dark-text-secondary); margin: 0.5rem 0; padding-left: 1.2rem;">
            <li><b>Current Performance:</b> {performance_metrics[trend_metric]:.1f}%</li>
            <li><b>Target Benchmark:</b> {target_value}% {'or higher' if trend_metric == 'delivery_rate' else 'or lower'}</li>
            <li><b>Performance Gap:</b> {abs(performance_metrics[trend_metric] - target_value):.1f}% {'above' if trend_metric == 'delivery_rate' and performance_metrics[trend_metric] > target_value else 'below'} target</li>
        </ul>
        <p style="color: var(--dark-text-secondary); margin: 0; font-size: 0.9rem;">
            Monitor the {smoothing_window}-day rolling average for trend analysis and seasonality patterns.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= PERFORMANCE IMPROVEMENT =======================
    
    st.markdown('<h2 class="main-text">💡 Performance Improvement Strategies</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">🚀 For Delivery Rate Improvement</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Improve inventory accuracy and availability</li>
                <li>Enhance order fulfillment processes</li>
                <li>Optimize logistics partner selection</li>
                <li>Implement better order tracking and communication</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">⏱️ For Timeliness Improvement</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Set realistic delivery time estimates</li>
                <li>Optimize last-mile delivery operations</li>
                <li>Implement proactive delay notifications</li>
                <li>Develop contingency plans for common delay scenarios</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Performance benchmarks
    st.markdown("### 🏆 Performance Benchmarks")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1rem; text-align: center;">
            <div style="color: #2A927A; font-size: 1.2rem; font-weight: 600;">Industry Standard</div>
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                Delivery Rate: 95%<br>
                On-Time Rate: 85%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1rem; text-align: center;">
            <div style="color: #2C7D8B; font-size: 1.2rem; font-weight: 600;">Best Practice</div>
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                Delivery Rate: 98%<br>
                On-Time Rate: 90%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        current_gap = 95 - performance_metrics['delivery_rate']
        gap_color = "#2A927A" if current_gap <= 0 else "#8B4513" if current_gap > 5 else "#C9D2BA"
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid {gap_color}; 
                    border-radius: 8px; padding: 1rem; text-align: center;">
            <div style="color: {gap_color}; font-size: 1.2rem; font-weight: 600;">Your Gap</div>
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                Delivery Rate: {current_gap:.1f}% {'above' if current_gap < 0 else 'below'} industry<br>
                {'Exceeding' if current_gap < 0 else 'Meeting' if current_gap <= 5 else 'Below'} standards
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ======================= DATA EXPLORER =======================
    
    with st.expander("🔍 Explore Performance Data", expanded=False):
        st.markdown("### 📊 Performance Metrics Summary")
        
        # Create metrics table
        # Create metrics table
        metrics_df = pd.DataFrame([
            {"Metric": "Total Orders", "Value": f"{performance_metrics['total_orders']:,}"},
            {"Metric": "Delivered Orders", "Value": f"{performance_metrics['total_delivered']:,}"},
            {"Metric": "Not Delivered Orders", "Value": f"{performance_metrics['total_not_delivered']:,}"},
            {"Metric": "Delivery Rate", "Value": f"{performance_metrics['delivery_rate']:.1f}%"},
            {"Metric": "On-Time Delivered", "Value": f"{performance_metrics['on_time_delivered']:,}"},
            {"Metric": "Early Delivered", "Value": f"{performance_metrics['early_delivered']:,}"},
            {"Metric": "Delayed Delivered", "Value": f"{performance_metrics['delayed_delivered']:,}"},
            {"Metric": "On-Time Rate", "Value": f"{performance_metrics['on_time_rate']:.1f}%"},
            {"Metric": "Early Rate", "Value": f"{performance_metrics['early_rate']:.1f}%"},
            {"Metric": "Delay Rate", "Value": f"{performance_metrics['delay_rate']:.1f}%"},
            {"Metric": "Average Delay (days)", "Value": f"{performance_metrics['avg_delay_days']:.1f}" if performance_metrics['avg_delay_days'] > 0 else "N/A"},
            {"Metric": "Median Delay (days)", "Value": f"{performance_metrics['median_delay_days']:.1f}" if performance_metrics['median_delay_days'] > 0 else "N/A"}
        ])
        
        st.dataframe(
            metrics_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Show detailed data if available
        if not analysis_data['delivered_orders'].empty:
            st.markdown("### 📋 Delivered Orders Sample")
            
            sample_data = analysis_data['delivered_orders'][[
                'order_id', 'order_purchase_timestamp', 
                'order_delivered_customer_date', 'order_estimated_delivery_date',
                'Delay', 'is_delayed', 'is_early', 'is_on_time', 'delay_days'
            ]].head(100).copy()
            
            # Format the columns for display
            if 'order_purchase_timestamp' in sample_data.columns:
                sample_data['order_purchase_timestamp'] = sample_data['order_purchase_timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            if 'order_delivered_customer_date' in sample_data.columns:
                sample_data['order_delivered_customer_date'] = sample_data['order_delivered_customer_date'].dt.strftime('%Y-%m-%d %H:%M')
            if 'order_estimated_delivery_date' in sample_data.columns:
                sample_data['order_estimated_delivery_date'] = sample_data['order_estimated_delivery_date'].dt.strftime('%Y-%m-%d %H:%M')
            if 'Delay' in sample_data.columns:
                sample_data['Delay'] = sample_data['Delay'].astype(str)
            if 'delay_days' in sample_data.columns:
                sample_data['delay_days'] = sample_data['delay_days'].apply(lambda x: f"{x:.1f}" if not pd.isna(x) else "N/A")
            
            st.dataframe(
                sample_data,
                use_container_width=True,
                column_config={
                    "order_id": "Order ID",
                    "order_purchase_timestamp": "Purchase Time",
                    "order_delivered_customer_date": "Actual Delivery",
                    "order_estimated_delivery_date": "Estimated Delivery",
                    "Delay": "Delay Duration",
                    "is_delayed": "Is Delayed",
                    "is_early": "Is Early",
                    "is_on_time": "Is On Time",
                    "delay_days": "Delay Days"
                }
            )
            
            # Export options
            csv = analysis_data['delivered_orders'].to_csv(index=False)
            st.download_button(
                label="📥 Download Delivered Orders Data (CSV)",
                data=csv,
                file_name="olist_delivered_orders.csv",
                mime="text/csv",
                type="secondary"
            )
        
        # SLA Compliance details
        if sla_compliance:
            st.markdown("### ⏱️ SLA Compliance Details")
            
            sla_df = pd.DataFrame([
                {
                    "SLA Tier": tier,
                    "Order Count": data['count'],
                    "Percentage": f"{data['percentage']:.1f}%"
                }
                for tier, data in sla_compliance.items()
            ])
            
            st.dataframe(
                sla_df,
                use_container_width=True,
                hide_index=True
            )
    
    # ======================= PAGE FOOTER =======================
    
    st.markdown("---")
    
    if performance_metrics['total_delivered'] > 0:
        delivery_rate = performance_metrics['delivery_rate']
        on_time_rate = performance_metrics['on_time_rate']
        avg_delay = performance_metrics['avg_delay_days']
        
        performance_summary = "Excellent" if delivery_rate >= 95 and on_time_rate >= 85 else \
                              "Good" if delivery_rate >= 90 and on_time_rate >= 80 else \
                              "Needs Improvement" if delivery_rate >= 80 and on_time_rate >= 70 else \
                              "Critical Attention Needed"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
            <p>
                <b>Delivery Performance Summary</b> • {performance_summary} • 
                Delivery Rate: {delivery_rate:.1f}% • 
                On-Time Rate: {on_time_rate:.1f}% • 
                Avg Delay: {avg_delay:.1f} days
            </p>
            <p style="margin-top: 0.5rem;">
                Monitor delivery performance regularly to maintain customer satisfaction and optimize logistics operations.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
            <p>
                <b>Delivery Performance Analysis</b> • No delivered orders found in dataset
            </p>
            <p style="margin-top: 0.5rem;">
                To enable delivery performance analysis, ensure orders data includes delivery status and date information.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ======================= CUSTOM CSS =======================

st.markdown("""
<style>
/* Delivery performance specific styling */
.performance-excellent { color: #2A927A; }
.performance-good { color: #C9D2BA; }
.performance-fair { color: #D4B483; }
.performance-poor { color: #8B4513; }

/* Metric card enhancements for delivery page */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    transition: all 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(42, 146, 122, 0.3) !important;
    box-shadow: 0 5px 15px rgba(42, 146, 122, 0.2);
}

/* Performance summary cards */
.performance-card {
    transition: all 0.3s ease;
}

.performance-card:hover {
    transform: translateY(-5px);
    border-color: rgba(212, 180, 131, 0.3) !important;
}

/* Trend line optimizations */
.js-plotly-plot .scatter .trace {
    will-change: transform;
}

/* Donut chart optimization */
.js-plotly-plot .pie .trace {
    transition: opacity 0.3s ease;
}

.js-plotly-plot .pie .trace:hover {
    opacity: 0.9;
}

/* SLA compliance bars */
.js-plotly-plot .barlayer .trace .point {
    transition: transform 0.3s ease;
}

.js-plotly-plot .barlayer .trace .point:hover {
    transform: scaleY(1.1);
    transform-origin: bottom;
}

/* Responsive adjustments for delivery metrics */
@media (max-width: 768px) {
    div[data-testid="stMetric"] {
        margin-bottom: 1rem;
    }
}

/* Print-friendly styles */
@media print {
    .stPlotlyChart {
        page-break-inside: avoid;
    }
    
    .performance-card {
        border: 1px solid #ccc !important;
    }
}

/* Performance animations */
@keyframes performancePulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

.performance-animated {
    animation: performancePulse 2s ease-in-out infinite;
}

/* Delivery status indicators */
.delivery-status-indicator {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 8px;
}

.delivery-status-delivered {
    background-color: #2A927A;
}

.delivery-status-not-delivered {
    background-color: #8B4513;
}

.delivery-status-early {
    background-color: #2C7D8B;
}

.delivery-status-delayed {
    background-color: #8B0000;
}

/* Performance gauge styling */
.performance-gauge {
    position: relative;
    width: 100%;
    height: 20px;
    background: linear-gradient(90deg, #8B4513 0%, #C9D2BA 50%, #2A927A 100%);
    border-radius: 10px;
    overflow: hidden;
}

.performance-gauge-fill {
    position: absolute;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.2);
    transition: width 1s ease-in-out;
}

/* Enhanced tooltips */
[data-testid="stTooltip"] {
    background-color: var(--dark-card) !important;
    border: 1px solid var(--dark-card-border) !important;
    color: var(--dark-text-primary) !important;
    font-size: 0.9rem !important;
    padding: 0.5rem !important;
    border-radius: 4px !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
}

/* Performance comparison badges */
.performance-badge {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
    margin-left: 0.5rem;
}

.badge-excellent {
    background-color: rgba(42, 146, 122, 0.2);
    color: #2A927A;
    border: 1px solid rgba(42, 146, 122, 0.3);
}

.badge-good {
    background-color: rgba(201, 210, 186, 0.2);
    color: #C9D2BA;
    border: 1px solid rgba(201, 210, 186, 0.3);
}

.badge-fair {
    background-color: rgba(212, 180, 131, 0.2);
    color: #D4B483;
    border: 1px solid rgba(212, 180, 131, 0.3);
}

.badge-poor {
    background-color: rgba(139, 69, 19, 0.2);
    color: #8B4513;
    border: 1px solid rgba(139, 69, 19, 0.3);
}

/* Progress indicators */
.progress-container {
    margin: 1rem 0;
}

.progress-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    color: var(--dark-text-secondary);
    font-size: 0.9rem;
}

.progress-bar {
    height: 8px;
    background-color: var(--dark-card-border);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease-in-out;
}

/* Delivery timeline visualization */
.delivery-timeline {
    position: relative;
    padding-left: 2rem;
    margin: 1rem 0;
}

.timeline-item {
    position: relative;
    margin-bottom: 1.5rem;
    padding-left: 1rem;
}

.timeline-item:before {
    content: '';
    position: absolute;
    left: -8px;
    top: 0;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background-color: var(--dark-text-warm);
}

.timeline-item:after {
    content: '';
    position: absolute;
    left: -1px;
    top: 16px;
    bottom: -1.5rem;
    width: 2px;
    background-color: var(--dark-card-border);
}

.timeline-item:last-child:after {
    display: none;
}

.timeline-date {
    font-weight: 500;
    color: var(--dark-text-primary);
    margin-bottom: 0.25rem;
}

.timeline-content {
    color: var(--dark-text-secondary);
    font-size: 0.9rem;
}

/* Performance scorecards */
.scorecard {
    background: var(--dark-card);
    border: 1px solid var(--dark-card-border);
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1rem 0;
    transition: all 0.3s ease;
}

.scorecard:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.scorecard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.scorecard-title {
    color: var(--dark-text-primary);
    font-weight: 500;
    font-size: 1.1rem;
}

.scorecard-value {
    font-size: 2rem;
    font-weight: 600;
    text-align: center;
    margin: 1rem 0;
}

.scorecard-change {
    text-align: center;
    font-size: 0.9rem;
    color: var(--dark-text-secondary);
}

.change-positive {
    color: #2A927A;
}

.change-negative {
    color: #8B4513;
}

/* Responsive performance grids */
.performance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

/* Delivery status summary */
.status-summary {
    display: flex;
    justify-content: space-around;
    margin: 1.5rem 0;
    padding: 1rem;
    background: var(--dark-card);
    border: 1px solid var(--dark-card-border);
    border-radius: 8px;
}

.status-item {
    text-align: center;
}

.status-count {
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.status-label {
    font-size: 0.9rem;
    color: var(--dark-text-secondary);
}
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()