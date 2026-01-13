# pages/7_🚨_Delay_Analysis.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from analysis.orders_analysis import (
    create_delay_heatmap
)

# Page configuration
st.set_page_config(
    page_title="Delay Analysis | Olist Dashboard",
    page_icon="🚨",
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
def get_delay_analysis(orders_data):
    """Cached delay analysis - optimized for this page only"""
    
    # Create a copy to avoid modifying original
    delay_data = orders_data.copy()
    
    # Convert datetime columns if they're strings
    datetime_cols = ['order_purchase_timestamp', 'order_approved_at',
                    'order_delivered_carrier_date', 'order_delivered_customer_date',
                    'order_estimated_delivery_date']
    
    for col in datetime_cols:
        if col in delay_data.columns:
            if delay_data[col].dtype == 'object':  # If it's a string
                delay_data[col] = pd.to_datetime(delay_data[col], errors='coerce')
    
    # Calculate delay metrics
    delay_data['Delay'] = delay_data['order_estimated_delivery_date'] - delay_data['order_delivered_customer_date']
    delay_data['Real_Time'] = delay_data['order_delivered_customer_date'] - delay_data['order_purchase_timestamp']
    
    # Calculate percentage breakdown of timeline
    delay_data['Site_Real_PCT'] = (
        (delay_data['order_approved_at'] - delay_data['order_purchase_timestamp']) / 
        delay_data['Real_Time'] * 100
    ).fillna(0)
    
    delay_data['Seller_Real_PCT'] = (
        (delay_data['order_delivered_carrier_date'] - delay_data['order_approved_at']) / 
        delay_data['Real_Time'] * 100
    ).fillna(0)
    
    delay_data['Shipping_Real_PCT'] = (
        (delay_data['order_delivered_customer_date'] - delay_data['order_delivered_carrier_date']) / 
        delay_data['Real_Time'] * 100
    ).fillna(0)
    
    # Simplified delivery status
    if 'order_status' in delay_data.columns:
        delay_data['Net_State'] = delay_data['order_status'].apply(
            lambda x: 'Delivered' if x == 'delivered' else 'Not_Delivered'
        )
    else:
        delay_data['Net_State'] = 'Delivered'  # Default if status not available
    
    # Filter out rows with missing delay data
    delay_data_clean = delay_data.dropna(
        subset=['Delay', 'Site_Real_PCT', 'Seller_Real_PCT', 'Shipping_Real_PCT']
    )
    
    # Calculate delay statistics
    delayed_orders = delay_data_clean[delay_data_clean['Delay'] < pd.Timedelta(0)]
    
    if len(delayed_orders) > 0:
        delayed_orders['delay_days'] = delayed_orders['Delay'].dt.total_seconds() / (24 * 3600)
        
        delay_stats = {
            'total_delayed': len(delayed_orders),
            'avg_delay_days': delayed_orders['delay_days'].mean(),
            'median_delay_days': delayed_orders['delay_days'].median(),
            'max_delay_days': delayed_orders['delay_days'].min(),  # Most negative = longest delay
            'delayed_delivered': len(delayed_orders[delayed_orders['Net_State'] == 'Delivered']),
            'delayed_not_delivered': len(delayed_orders[delayed_orders['Net_State'] == 'Not_Delivered'])
        }
    else:
        delay_stats = {
            'total_delayed': 0,
            'avg_delay_days': 0,
            'median_delay_days': 0,
            'max_delay_days': 0,
            'delayed_delivered': 0,
            'delayed_not_delivered': 0
        }
    
    return {
        'delay_data': delay_data,
        'delay_data_clean': delay_data_clean,
        'delayed_orders': delayed_orders if 'delayed_orders' in locals() else pd.DataFrame(),
        'delay_stats': delay_stats,
        'orders_data': delay_data
    }

# ======================= HELPER FUNCTIONS =======================

def create_delay_distribution_chart(delayed_orders):
    """Create distribution chart of delay days"""
    
    if len(delayed_orders) == 0:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'No Delayed Orders Found',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#333333'}
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        return fig
    
    # Create histogram of delay days
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=delayed_orders['delay_days'],
        nbinsx=30,
        marker_color='#8B4513',
        opacity=0.7,
        name='Delay Distribution',
        hovertemplate='Delay: %{x:.1f} days<br>Count: %{y}<extra></extra>'
    ))
    
    # Add vertical line at average delay
    avg_delay = delayed_orders['delay_days'].mean()
    fig.add_vline(
        x=avg_delay,
        line_width=2,
        line_dash="dash",
        line_color="#C9D2BA",
        annotation_text=f"Avg: {avg_delay:.1f} days",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title={
            'text': 'Distribution of Delivery Delays',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Delay (Days) - Negative = Early, Positive = Late',
        yaxis_title='Number of Orders',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        showlegend=False,
        bargap=0.1
    )
    
    return fig

def create_delay_by_stage_chart(delayed_orders):
    """Create box plot showing delay by processing stage percentage"""
    
    if len(delayed_orders) == 0:
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
    
    fig = go.Figure()
    
    # Add box plots for each stage percentage
    stages = [
        ('Site_Real_PCT', 'Site Processing', '#2C7D8B'),
        ('Seller_Real_PCT', 'Seller Preparation', '#2A927A'),
        ('Shipping_Real_PCT', 'Shipping', '#C9D2BA')
    ]
    
    for stage_col, stage_name, color in stages:
        if stage_col in delayed_orders.columns:
            # Filter outliers for better visualization
            stage_data = delayed_orders[stage_col].dropna()
            q1 = stage_data.quantile(0.25)
            q3 = stage_data.quantile(0.75)
            iqr = q3 - q1
            filtered_data = stage_data[(stage_data >= q1 - 1.5*iqr) & (stage_data <= q3 + 1.5*iqr)]
            
            fig.add_trace(go.Box(
                y=filtered_data,
                name=stage_name,
                boxpoints='outliers',
                marker_color=color,
                line_color=color
            ))
    
    fig.update_layout(
        title={
            'text': 'Delay Analysis by Processing Stage Percentage',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        yaxis_title='Percentage of Total Time (%)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        showlegend=True,
        boxmode='group'
    )
    
    return fig

def create_delay_severity_chart(delayed_orders):
    """Create chart showing delay severity categories"""
    
    if len(delayed_orders) == 0:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'No Delayed Orders',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400
        )
        return fig
    
    # Categorize delays by severity
    delayed_orders['delay_severity'] = pd.cut(
        delayed_orders['delay_days'],
        bins=[-float('inf'), -20, -10, -5, -2, 0],
        labels=['Very Severe (>20 days)', 'Severe (10-20 days)', 
                'Moderate (5-10 days)', 'Mild (2-5 days)', 'Minor (<2 days)']
    )
    
    severity_counts = delayed_orders['delay_severity'].value_counts().sort_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=severity_counts.index,
        y=severity_counts.values,
        marker_color=['#8B4513', '#C9D2BA', '#2A927A', '#2C7D8B', '#7fb4ca'],
        text=[f'{v:,}' for v in severity_counts.values],
        textposition='auto',
        textfont=dict(color='white', size=11),
        hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<br><extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Delay Severity Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Delay Severity',
        yaxis_title='Number of Orders',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        showlegend=False,
        xaxis_tickangle=-45
    )
    
    return fig

def create_delay_trend_chart(delay_data):
    """Create trend chart of delay rates over time"""
    
    if len(delay_data) == 0:
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
    if 'order_purchase_timestamp' in delay_data.columns:
        if delay_data['order_purchase_timestamp'].dtype == 'object':
            delay_data['order_purchase_timestamp'] = pd.to_datetime(
                delay_data['order_purchase_timestamp'], errors='coerce'
            )
        
        delay_data['purchase_date'] = delay_data['order_purchase_timestamp'].dt.date
        
        # Calculate daily delay rate
        daily_stats = delay_data.groupby('purchase_date').agg(
            total_orders=('order_id', 'nunique'),
            delayed_orders=('Delay', lambda x: (x < pd.Timedelta(0)).sum() if x.dtype != 'object' else 0)
        ).reset_index().sort_values('purchase_date')
        
        daily_stats['delay_rate'] = (daily_stats['delayed_orders'] / daily_stats['total_orders'] * 100).fillna(0)
        daily_stats['delay_rate_roll'] = daily_stats['delay_rate'].rolling(7, min_periods=1).mean()
        
        fig = go.Figure()
        
        # Add delay rate line
        fig.add_trace(go.Scatter(
            x=daily_stats['purchase_date'],
            y=daily_stats['delay_rate_roll'],
            mode='lines',
            line=dict(color='#8B4513', width=3),
            name='Delay Rate',
            hovertemplate='Date: %{x|%Y-%m-%d}<br>' +
                         'Delay Rate: %{y:.1f}%<br>' +
                         'Total Orders: %{customdata[0]:,}<br>' +
                         'Delayed Orders: %{customdata[1]:,}<br>' +
                         '<extra></extra>',
            customdata=daily_stats[['total_orders', 'delayed_orders']].values
        ))
        
        # Add total orders as secondary axis (scaled)
        max_delay_rate = daily_stats['delay_rate_roll'].max()
        max_orders = daily_stats['total_orders'].max()
        scale_factor = max_delay_rate / max_orders if max_orders > 0 else 1
        
        fig.add_trace(go.Scatter(
            x=daily_stats['purchase_date'],
            y=daily_stats['total_orders'] * scale_factor,
            mode='lines',
            line=dict(color='#2C7D8B', width=1, dash='dot'),
            name='Total Orders (scaled)',
            yaxis='y2',
            hovertemplate='Date: %{x|%Y-%m-%d}<br>' +
                         'Total Orders: %{customdata:,}<br>' +
                         '<extra></extra>',
            customdata=daily_stats['total_orders'].values
        ))
        
        fig.update_layout(
            title={
                'text': 'Daily Delay Rate Trend (7-day average)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#333333'}
            },
            xaxis_title='Date',
            yaxis=dict(
                title='Delay Rate (%)',
                side='left',
                color='#8B4513'
            ),
            yaxis2=dict(
                title='Total Orders',
                side='right',
                overlaying='y',
                color='#2C7D8B',
                showgrid=False
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333333'),
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
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
    """Initialize the delay analysis page"""
    
    # Check if data is loaded
    if not st.session_state.get('data_loaded', False):
        st.error("⚠️ Data not loaded. Please go to the Home page and click 'Load All Data'.")
        st.stop()
    
    if st.session_state.orders is None:
        st.error("❌ Orders data not available. Please reload data from Home page.")
        st.stop()
    
    # Initialize delay analysis with caching
    if 'delay_analysis' not in st.session_state:
        with st.spinner("🚨 Analyzing delivery delays..."):
            results = get_delay_analysis(st.session_state.orders)
            st.session_state.delay_analysis = results
    
    return st.session_state.delay_analysis

# ======================= MAIN PAGE CONTENT =======================

def main():
    """Main content for Delay Analysis page"""
    
    # Page header
    st.markdown("""
    <h1 class="main-text">🚨 Delay Analysis</h1>
    <p class="sub-text">Deep dive into delivery delays, patterns, and impact analysis</p>
    """, unsafe_allow_html=True)
    
    # Quick navigation
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <p style="color: var(--dark-text-secondary); margin: 0;">
            🔍 <b>Related Analysis:</b> 
            <a href="/⏱️_Order_Timelines" style="color: var(--dark-text-cool);">Order Timelines</a> • 
            <a href="/📊_Delivery_Performance" style="color: var(--dark-text-cool);">Delivery Performance</a> • 
            <a href="/📍_Geographic_Analysis" style="color: var(--dark-text-cool);">Geographic Analysis</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize data
    analysis_data = initialize_page()
    delay_data = analysis_data['delay_data']
    delay_data_clean = analysis_data['delay_data_clean']
    delayed_orders = analysis_data['delayed_orders']
    delay_stats = analysis_data['delay_stats']
    
    # ======================= DELAY OVERVIEW =======================
    
    st.markdown('<h2 class="main-text">📊 Delay Overview</h2>', unsafe_allow_html=True)
    
    # Check if we have delay data
    if delay_stats['total_delayed'] == 0:
        st.success("""
        🎉 **Excellent News! No Delayed Orders Found**
        
        Based on the current dataset, there are no orders with delivery delays.
        All orders were either delivered on time or early.
        
        You can still explore delay patterns and trends below.
        """)
    
    # Delay metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Delayed Orders",
            value=f"{delay_stats['total_delayed']:,}",
            delta=None
        )
    
    with col2:
        total_orders = len(delay_data_clean)
        delay_rate = (delay_stats['total_delayed'] / total_orders * 100) if total_orders > 0 else 0
        st.metric(
            label="Delay Rate",
            value=f"{delay_rate:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Avg Delay",
            value=f"{abs(delay_stats['avg_delay_days']):.1f} days",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Longest Delay",
            value=f"{abs(delay_stats['max_delay_days']):.1f} days",
            delta=None
        )
    
    with col5:
        delayed_delivered_rate = (
            delay_stats['delayed_delivered'] / delay_stats['total_delayed'] * 100
        ) if delay_stats['total_delayed'] > 0 else 0
        st.metric(
            label="Delayed & Delivered",
            value=f"{delayed_delivered_rate:.1f}%",
            delta=None
        )
    
    # Delay impact summary
    if delay_stats['total_delayed'] > 0:
        st.markdown("### 🎯 Delay Impact Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.8rem; color: #8B4513; font-weight: 600;">
                    {delay_stats['delayed_delivered']:,}
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                    Delayed but Delivered<br>
                    {delayed_delivered_rate:.1f}% of delayed orders
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            delayed_not_delivered_rate = (
                delay_stats['delayed_not_delivered'] / delay_stats['total_delayed'] * 100
            ) if delay_stats['total_delayed'] > 0 else 0
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.8rem; color: #8B4513; font-weight: 600;">
                    {delay_stats['delayed_not_delivered']:,}
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                    Delayed & Not Delivered<br>
                    {delayed_not_delivered_rate:.1f}% of delayed orders
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_lost_days = abs(delay_stats['total_delayed'] * delay_stats['avg_delay_days'])
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.8rem; color: #8B4513; font-weight: 600;">
                    {total_lost_days:,.0f}
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                    Total Lost Days<br>
                    Across all delayed orders
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= DELAY DISTRIBUTION ANALYSIS =======================
    
    st.markdown('<h2 class="main-text">📈 Delay Distribution Analysis</h2>', unsafe_allow_html=True)
    
    if len(delayed_orders) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Delay distribution histogram
            fig_dist = create_delay_distribution_chart(delayed_orders)
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            # Delay severity chart
            fig_severity = create_delay_severity_chart(delayed_orders)
            st.plotly_chart(fig_severity, use_container_width=True)
        
        # Delay by stage analysis
        st.markdown("### ⚙️ Delay by Processing Stage")
        
        fig_stage = create_delay_by_stage_chart(delayed_orders)
        st.plotly_chart(fig_stage, use_container_width=True)
        
        # Stage delay insights
        stage_insights = []
        for stage_col, stage_name, _ in [('Site_Real_PCT', 'Site Processing', '#2C7D8B'),
                                         ('Seller_Real_PCT', 'Seller Preparation', '#2A927A'),
                                         ('Shipping_Real_PCT', 'Shipping', '#C9D2BA')]:
            if stage_col in delayed_orders.columns:
                stage_data = delayed_orders[stage_col].dropna()
                if len(stage_data) > 0:
                    stage_insights.append({
                        'stage': stage_name,
                        'mean': stage_data.mean(),
                        'median': stage_data.median(),
                        'std': stage_data.std()
                    })
        
        if stage_insights:
            cols = st.columns(len(stage_insights))
            for idx, insight in enumerate(stage_insights):
                with cols[idx]:
                    color = '#2C7D8B' if idx == 0 else '#2A927A' if idx == 1 else '#C9D2BA'
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                                border-radius: 8px; padding: 1rem; text-align: center;">
                        <div style="color: {color}; font-size: 1.2rem; font-weight: 600;">
                            {insight['stage']}
                        </div>
                        <div style="color: var(--dark-text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                            Mean: {insight['mean']:.1f}%<br>
                            Median: {insight['median']:.1f}%<br>
                            Std Dev: {insight['std']:.1f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= DELAY TREND ANALYSIS =======================
    
    st.markdown('<h2 class="main-text">📅 Delay Trend Analysis</h2>', unsafe_allow_html=True)
    
    # Create delay trend chart
    fig_trend = create_delay_trend_chart(delay_data)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    st.markdown("---")
    
    # ======================= DELAY HEATMAP ANALYSIS =======================
    
    st.markdown('<h2 class="main-text">🔥 Delay Heatmap Analysis</h2>', unsafe_allow_html=True)
    
    # Interactive controls for heatmap
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pct_column = st.selectbox(
            "Processing Stage for Analysis",
            ["Site_Real_PCT", "Seller_Real_PCT", "Shipping_Real_PCT"],
            help="Select which processing stage to analyze for delays"
        )
    
    with col2:
        delivery_status = st.selectbox(
            "Filter by Delivery Status",
            ["Delivered", "Not_Delivered", "All"],
            help="Filter delayed orders by delivery status"
        )
    
    with col3:
        color_scale = st.selectbox(
            "Heatmap Color Scale",
            ["YlOrRd", "RdBu", "Viridis", "Plasma", "Blues"],
            help="Select color scale for heatmap visualization"
        )
    
    # Create heatmap if we have delayed orders
    if len(delayed_orders) > 0:
        # Filter by delivery status if needed
        if delivery_status != 'All':
            filtered_delayed = delayed_orders[delayed_orders['Net_State'] == delivery_status].copy()
        else:
            filtered_delayed = delayed_orders.copy()
        
        if len(filtered_delayed) > 0:
            # Create heatmap
            stage_name = pct_column.replace('_', ' ').replace('PCT', '%')
            title = f"Delayed Orders Analysis: {stage_name} - {delivery_status}"
            
            fig_heatmap = create_delay_heatmap(
                delayed_orders=filtered_delayed,
                pct_col=pct_column,
                color_scale=color_scale,
                title=title
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Heatmap interpretation
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1.5rem; margin: 1rem 0;">
                <h4 class="warm-text" style="margin-top: 0;">🎯 Heatmap Interpretation Guide</h4>
                <ul style="color: var(--dark-text-secondary); margin: 0.5rem 0; padding-left: 1.2rem;">
                    <li><b>X-axis:</b> Percentage of total delivery time spent in the selected stage</li>
                    <li><b>Y-axis:</b> Severity of delay (more negative = longer delay)</li>
                    <li><b>Cell color:</b> Number of orders in each delay-percentage combination</li>
                    <li><b>Darker cells:</b> Higher concentration of delayed orders</li>
                </ul>
                <p style="color: var(--dark-text-secondary); margin: 0; font-size: 0.9rem;">
                    Look for patterns: Do delays cluster around specific percentage ranges? Are certain delay severities associated with particular stage durations?
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(f"No delayed orders found for {delivery_status} status.")
    else:
        st.info("No delayed orders available for heatmap analysis.")
    
    st.markdown("---")
    
    # ======================= DELAY MITIGATION STRATEGIES =======================
    
    st.markdown('<h2 class="main-text">💡 Delay Mitigation Strategies</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">🚀 Preventive Measures</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Improve demand forecasting for better inventory planning</li>
                <li>Optimize shipping routes and carrier selection</li>
                <li>Implement buffer times in delivery estimates</li>
                <li>Enhance communication with logistics partners</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">🔄 Reactive Solutions</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Establish rapid response teams for delayed orders</li>
                <li>Implement proactive customer communication protocols</li>
                <li>Create compensation policies for significant delays</li>
                <li>Develop escalation procedures for chronic delays</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ======================= DATA EXPLORER =======================
    
    with st.expander("🔍 Explore Delay Data", expanded=False):
        if len(delayed_orders) > 0:
            st.markdown("### 📊 Delayed Orders Sample")
            
            sample_data = delayed_orders.head(10)[[
                'order_purchase_timestamp', 'Net_State', 'delay_days',
                'Site_Real_PCT', 'Seller_Real_PCT', 'Shipping_Real_PCT'
            ]].copy()
            
            # Format for display
            sample_data['delay_days'] = sample_data['delay_days'].apply(lambda x: f"{x:.1f} days")
            sample_data['Site_Real_PCT'] = sample_data['Site_Real_PCT'].apply(lambda x: f"{x:.1f}%")
            sample_data['Seller_Real_PCT'] = sample_data['Seller_Real_PCT'].apply(lambda x: f"{x:.1f}%")
            sample_data['Shipping_Real_PCT'] = sample_data['Shipping_Real_PCT'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(sample_data, use_container_width=True, hide_index=True)
            
            # Export option
            csv = delayed_orders[[
                'order_id', 'Net_State', 'delay_days',
                'Site_Real_PCT', 'Seller_Real_PCT', 'Shipping_Real_PCT'
            ]].to_csv(index=False)
            
            st.download_button(
                label="📥 Download Delay Data (CSV)",
                data=csv,
                file_name="olist_delay_analysis.csv",
                mime="text/csv",
                type="secondary"
            )
        else:
            st.info("No delayed orders available for display.")
    
    # ======================= PAGE FOOTER =======================
    
    st.markdown("---")
    
    total_delayed = delay_stats['total_delayed']
    delay_rate_val = (total_delayed / len(delay_data_clean) * 100) if len(delay_data_clean) > 0 else 0
    avg_delay = abs(delay_stats['avg_delay_days'])
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
        <p>
            <b>Delay Analysis</b> • {total_delayed:,} delayed orders • 
            Delay rate: {delay_rate_val:.1f}% • 
            Average delay: {avg_delay:.1f} days
        </p>
        <p style="margin-top: 0.5rem;">
            Use heatmaps and trend analysis to identify delay patterns and implement targeted mitigation strategies.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ======================= CUSTOM CSS =======================

st.markdown("""
<style>
/* Delay analysis styling */
.delay-severe { color: #8B4513; }
.delay-moderate { color: #C9D2BA; }
.delay-minor { color: #2A927A; }

/* Heatmap optimizations */
.js-plotly-plot .heatmaplayer .trace {
    will-change: transform;
}

/* Metric card styling for delay page */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    transition: all 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(139, 69, 19, 0.3) !important;
    box-shadow: 0 5px 15px rgba(139, 69, 19, 0.2);
}

/* Warning styling for delay metrics */
.delay-warning {
    background: rgba(139, 69, 19, 0.1) !important;
    border-color: rgba(139, 69, 19, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()