# pages/6_⏱️_Order_Timelines.py - CORRECTED VERSION
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Order Timelines | Olist Dashboard",
    page_icon="⏱️",
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
def get_timeline_analysis(orders_data):
    """Cached timeline analysis - optimized for this page only"""
    
    # Create a copy to avoid modifying original
    timeline_data = orders_data.copy()
    
    # Convert datetime columns if they're strings
    datetime_cols = ['order_purchase_timestamp', 'order_approved_at',
                    'order_delivered_carrier_date', 'order_delivered_customer_date']
    
    for col in datetime_cols:
        if col in timeline_data.columns:
            if timeline_data[col].dtype == 'object':  # If it's a string
                timeline_data[col] = pd.to_datetime(timeline_data[col], errors='coerce')
    
    # Now calculate timeline metrics
    timeline_data['site_hours'] = (
        (timeline_data['order_approved_at'] - timeline_data['order_purchase_timestamp']).dt.total_seconds() / 3600
    ).clip(0, None)  # Remove negative values
    
    timeline_data['seller_hours'] = (
        (timeline_data['order_delivered_carrier_date'] - timeline_data['order_approved_at']).dt.total_seconds() / 3600
    ).clip(0, None)
    
    timeline_data['shipping_hours'] = (
        (timeline_data['order_delivered_customer_date'] - timeline_data['order_delivered_carrier_date']).dt.total_seconds() / 3600
    ).clip(0, None)
    
    timeline_data['total_hours'] = (
        (timeline_data['order_delivered_customer_date'] - timeline_data['order_purchase_timestamp']).dt.total_seconds() / 3600
    ).clip(0, None)
    
    # Calculate percentage breakdown
    timeline_data['site_pct'] = (timeline_data['site_hours'] / timeline_data['total_hours'] * 100).fillna(0)
    timeline_data['seller_pct'] = (timeline_data['seller_hours'] / timeline_data['total_hours'] * 100).fillna(0)
    timeline_data['shipping_pct'] = (timeline_data['shipping_hours'] / timeline_data['total_hours'] * 100).fillna(0)
    
    # Filter for delivered orders with complete timeline
    delivered_timeline = timeline_data[
        (timeline_data['Net_State'] == 'Delivered') &
        (timeline_data['total_hours'] > 0) &
        (timeline_data['total_hours'].notna())
    ].copy()
    
    return {
        'timeline_data': timeline_data,
        'delivered_timeline': delivered_timeline,
        'orders_data': timeline_data  # Return the processed data
    }

# ======================= HELPER FUNCTIONS =======================

def create_timeline_stage_chart(timeline_data, stage='site_hours'):
    """Create distribution chart for a specific timeline stage"""
    
    stage_names = {
        'site_hours': 'Site Processing',
        'seller_hours': 'Seller Preparation', 
        'shipping_hours': 'Shipping',
        'total_hours': 'Total Delivery'
    }
    
    stage_colors = {
        'site_hours': '#2C7D8B',
        'seller_hours': '#2A927A',
        'shipping_hours': '#C9D2BA',
        'total_hours': '#8B4513'
    }
    
    # Filter for delivered orders and remove outliers
    data = timeline_data[timeline_data['Net_State'] == 'Delivered'][stage].dropna()
    
    if len(data) == 0:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': f'No Data for {stage_names.get(stage, stage)}',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=300
        )
        return fig
    
    # Remove extreme outliers for better visualization
    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1
    filtered_data = data[(data >= q1 - 1.5*iqr) & (data <= q3 + 1.5*iqr)]
    
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=filtered_data,
        nbinsx=30,
        marker_color=stage_colors.get(stage, '#2C7D8B'),
        opacity=0.7,
        name=stage_names.get(stage, stage),
        hovertemplate='Hours: %{x:.1f}<br>Count: %{y}<extra></extra>'
    ))
    
    # Add vertical line for median
    median_val = data.median()
    fig.add_vline(
        x=median_val,
        line_width=2,
        line_dash="dash",
        line_color=stage_colors.get(stage, '#2C7D8B'),
        annotation_text=f"Median: {median_val:.1f}h",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title={
            'text': f'{stage_names.get(stage, stage)} Time Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 14, 'color': '#333333'}
        },
        xaxis_title='Hours',
        yaxis_title='Number of Orders',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=300,
        showlegend=False,
        bargap=0.1
    )
    
    return fig

def create_timeline_breakdown_chart(delivered_timeline):
    """Create stacked bar chart showing timeline breakdown"""
    
    if len(delivered_timeline) == 0:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'No Delivered Orders with Complete Timeline',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400
        )
        return fig
    
    # Sample data for performance
    sample_size = min(100, len(delivered_timeline))
    sample_data = delivered_timeline.sample(sample_size, random_state=42).sort_values('total_hours')
    
    fig = go.Figure()
    
    # Add traces for each stage
    stages = [
        ('site_hours', 'Site Processing', '#2C7D8B'),
        ('seller_hours', 'Seller Preparation', '#2A927A'),
        ('shipping_hours', 'Shipping', '#C9D2BA')
    ]
    
    for stage_col, stage_name, color in stages:
        fig.add_trace(go.Bar(
            y=sample_data['total_hours'],
            x=[stage_name] * len(sample_data),
            base=sample_data[stage_col].cumsum() - sample_data[stage_col] if stage_col != 'site_hours' else 0,
            marker_color=color,
            name=stage_name,
            hoverinfo='skip',
            showlegend=True
        ))
    
    fig.update_layout(
        title={
            'text': f'Order Timeline Breakdown (Sample of {sample_size} Orders)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Processing Stage',
        yaxis_title='Total Hours',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        barmode='stack',
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

def create_cumulative_timeline_chart(delivered_timeline):
    """Create cumulative distribution of delivery times"""
    
    if len(delivered_timeline) == 0:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'No Timeline Data Available',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400
        )
        return fig
    
    # Sort by total hours and calculate cumulative percentage
    sorted_times = delivered_timeline['total_hours'].sort_values().reset_index(drop=True)
    cumulative_pct = (sorted_times.index + 1) / len(sorted_times) * 100
    
    fig = go.Figure()
    
    # Cumulative distribution line
    fig.add_trace(go.Scatter(
        x=sorted_times,
        y=cumulative_pct,
        mode='lines',
        line=dict(color='#2C7D8B', width=3),
        name='Cumulative %',
        hovertemplate='Hours: %{x:.1f}<br>% of Orders: %{y:.1f}%<extra></extra>'
    ))
    
    # Add key percentile markers
    percentiles = [50, 75, 90, 95]
    for p in percentiles:
        hours_at_p = sorted_times.quantile(p/100)
        fig.add_vline(
            x=hours_at_p,
            line_width=1,
            line_dash="dot",
            line_color="#C9D2BA",
            annotation_text=f"{p}%: {hours_at_p:.1f}h",
            annotation_position="top right",
            annotation_font_size=10
        )
    
    fig.update_layout(
        title={
            'text': 'Cumulative Distribution of Total Delivery Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Total Delivery Time (Hours)',
        yaxis_title='Cumulative Percentage of Orders',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        showlegend=False,
        hovermode='x unified'
    )
    
    return fig

def create_daily_trend_chart(orders_data, metric='orders', window=7):
    """Create daily trend chart for orders"""
    
    # Ensure date column is datetime
    orders = orders_data.copy()
    if 'order_purchase_timestamp' in orders.columns:
        if orders['order_purchase_timestamp'].dtype == 'object':
            orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'], errors='coerce')
        
        orders['date'] = orders['order_purchase_timestamp'].dt.date
        
        # Group by date
        daily = orders.groupby('date').agg(
            orders=('order_id', 'nunique')
        ).reset_index().sort_values('date')
        
        # Calculate rolling average
        daily[f'{metric}_roll'] = daily['orders'].rolling(window, min_periods=1).mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily['date'],
            y=daily[f'{metric}_roll'],
            mode='lines',
            line=dict(color='#2C7D8B', width=2),
            name='Order Trend',
            hovertemplate='Date: %{x|%Y-%m-%d}<br>' +
                         f'{metric.title()} ({window}-day avg): %{{y:,.0f}}' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'Daily {metric.title()} Trend ({window}-day rolling average)',
            xaxis_title='Date',
            yaxis_title=f'{metric.title()} ({window}-day avg)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333333'),
            height=400,
            showlegend=False
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
    """Initialize the order timelines page"""
    
    # Check if data is loaded
    if not st.session_state.get('data_loaded', False):
        st.error("⚠️ Data not loaded. Please go to the Home page and click 'Load All Data'.")
        st.stop()
    
    if st.session_state.orders is None:
        st.error("❌ Orders data not available. Please reload data from Home page.")
        st.stop()
    
    # Initialize timeline analysis with caching
    if 'timeline_analysis' not in st.session_state:
        with st.spinner("⏱️ Analyzing order timelines..."):
            results = get_timeline_analysis(st.session_state.orders)
            st.session_state.timeline_analysis = results
    
    return st.session_state.timeline_analysis

# ======================= MAIN PAGE CONTENT =======================

def main():
    """Main content for Order Timelines page"""
    
    # Page header
    st.markdown("""
    <h1 class="main-text">⏱️ Order Timelines</h1>
    <p class="sub-text">Analysis of order processing stages, delivery times, and timeline efficiency</p>
    """, unsafe_allow_html=True)
    
    # Quick navigation
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <p style="color: var(--dark-text-secondary); margin: 0;">
            🔍 <b>Related Analysis:</b> 
            <a href="/🚨_Delay_Analysis" style="color: var(--dark-text-cool);">Delay Analysis</a> • 
            <a href="/📊_Delivery_Performance" style="color: var(--dark-text-cool);">Delivery Performance</a> • 
            <a href="/🚚_Freight_Analysis" style="color: var(--dark-text-cool);">Freight Analysis</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize data
    analysis_data = initialize_page()
    timeline_data = analysis_data['timeline_data']
    delivered_timeline = analysis_data['delivered_timeline']
    orders_data = analysis_data['orders_data']
    
    # ======================= TIMELINE OVERVIEW =======================
    
    st.markdown('<h2 class="main-text">📊 Timeline Overview</h2>', unsafe_allow_html=True)
    
    # Check if we have timeline data
    if len(delivered_timeline) == 0:
        st.warning("""
        ⚠️ **No Complete Timeline Data**
        
        This analysis requires delivered orders with complete timeline data.
        No delivered orders with complete timestamp information were found.
        
        Basic order trends are still available below.
        """)
    
    # Timeline metrics
    if len(delivered_timeline) > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            median_total = delivered_timeline['total_hours'].median() / 24
            st.metric(
                label="Median Delivery Time",
                value=f"{median_total:.1f} days",
                delta=None
            )
        
        with col2:
            median_site = delivered_timeline['site_hours'].median()
            st.metric(
                label="Median Site Processing",
                value=f"{median_site:.1f} hours",
                delta=None
            )
        
        with col3:
            median_seller = delivered_timeline['seller_hours'].median()
            st.metric(
                label="Median Seller Prep",
                value=f"{median_seller:.1f} hours",
                delta=None
            )
        
        with col4:
            median_shipping = delivered_timeline['shipping_hours'].median()
            st.metric(
                label="Median Shipping",
                value=f"{median_shipping:.1f} hours",
                delta=None
            )
        
        # Stage percentage breakdown
        st.markdown("### 🎯 Stage Contribution to Total Time")
        
        avg_site_pct = delivered_timeline['site_pct'].mean()
        avg_seller_pct = delivered_timeline['seller_pct'].mean()
        avg_shipping_pct = delivered_timeline['shipping_pct'].mean()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="color: #2C7D8B; font-size: 1.8rem; font-weight: 600;">
                    {avg_site_pct:.1f}%
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                    Site Processing
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="color: #2A927A; font-size: 1.8rem; font-weight: 600;">
                    {avg_seller_pct:.1f}%
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                    Seller Preparation
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="color: #C9D2BA; font-size: 1.8rem; font-weight: 600;">
                    {avg_shipping_pct:.1f}%
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                    Shipping
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= TIMELINE DISTRIBUTIONS =======================
    
    st.markdown('<h2 class="main-text">📈 Timeline Distributions</h2>', unsafe_allow_html=True)
    
    if len(delivered_timeline) > 0:
        # Stage selection
        stage = st.selectbox(
            "Select Processing Stage to Analyze",
            ["Site Processing", "Seller Preparation", "Shipping", "Total Delivery"],
            help="Choose which timeline stage to view distribution for"
        )
        
        stage_map = {
            "Site Processing": "site_hours",
            "Seller Preparation": "seller_hours",
            "Shipping": "shipping_hours",
            "Total Delivery": "total_hours"
        }
        
        selected_stage = stage_map[stage]
        
        # Create distribution chart
        fig_dist = create_timeline_stage_chart(timeline_data, selected_stage)
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Statistical summary
        if selected_stage in delivered_timeline.columns:
            stage_data = delivered_timeline[selected_stage]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                            border-radius: 6px; padding: 0.8rem; text-align: center;">
                    <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">Mean</div>
                    <div style="color: var(--dark-text-primary); font-size: 1.2rem; font-weight: 600;">
                        {stage_data.mean():.1f}h
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                            border-radius: 6px; padding: 0.8rem; text-align: center;">
                    <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">Median</div>
                    <div style="color: var(--dark-text-primary); font-size: 1.2rem; font-weight: 600;">
                        {stage_data.median():.1f}h
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                            border-radius: 6px; padding: 0.8rem; text-align: center;">
                    <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">Std Dev</div>
                    <div style="color: var(--dark-text-primary); font-size: 1.2rem; font-weight: 600;">
                        {stage_data.std():.1f}h
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                            border-radius: 6px; padding: 0.8rem; text-align: center;">
                    <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">90th %ile</div>
                    <div style="color: var(--dark-text-primary); font-size: 1.2rem; font-weight: 600;">
                        {stage_data.quantile(0.9):.1f}h
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= TIMELINE VISUALIZATIONS =======================
    
    st.markdown('<h2 class="main-text">📊 Timeline Visualizations</h2>', unsafe_allow_html=True)
    
    if len(delivered_timeline) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Timeline breakdown chart
            fig_breakdown = create_timeline_breakdown_chart(delivered_timeline)
            st.plotly_chart(fig_breakdown, use_container_width=True)
        
        with col2:
            # Cumulative distribution chart
            fig_cumulative = create_cumulative_timeline_chart(delivered_timeline)
            st.plotly_chart(fig_cumulative, use_container_width=True)
    
    # ======================= DAILY TRENDS =======================
    
    st.markdown('<h2 class="main-text">📅 Daily Order Trends</h2>', unsafe_allow_html=True)
    
    # Trend controls
    col1, col2 = st.columns(2)
    
    with col1:
        trend_metric = st.selectbox(
            "Trend Metric",
            ["orders", "delivery_time"],
            help="Select what to analyze in daily trends"
        )
    
    with col2:
        smoothing_window = st.slider(
            "Smoothing Window (days)",
            min_value=1,
            max_value=30,
            value=7,
            help="Rolling average window for smoothing trends"
        )
    
    # Create daily trend chart
    if trend_metric == "delivery_time" and len(delivered_timeline) > 0:
        # Need to create a custom delivery time trend chart
        delivered_timeline['purchase_date'] = pd.to_datetime(
            delivered_timeline['order_purchase_timestamp']
        ).dt.date
        
        daily_delivery = delivered_timeline.groupby('purchase_date').agg(
            avg_delivery_time=('total_hours', 'mean'),
            order_count=('total_hours', 'count')
        ).reset_index().sort_values('purchase_date')
        
        daily_delivery['avg_delivery_roll'] = daily_delivery['avg_delivery_time'].rolling(
            smoothing_window, min_periods=1
        ).mean()
        
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=daily_delivery['purchase_date'],
            y=daily_delivery['avg_delivery_roll'],
            mode='lines',
            line=dict(color='#2C7D8B', width=2),
            name='Avg Delivery Time',
            hovertemplate='Date: %{x|%Y-%m-%d}<br>' +
                         'Avg Delivery: %{y:.1f} hours<br>' +
                         'Orders: %{customdata}<br>' +
                         '<extra></extra>',
            customdata=daily_delivery['order_count']
        ))
        
        fig_trend.update_layout(
            title=f'Average Delivery Time Trend ({smoothing_window}-day average)',
            xaxis_title='Purchase Date',
            yaxis_title='Average Delivery Time (hours)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333333'),
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        # Use existing function for order count trend
        fig_trend = create_daily_trend_chart(
            orders_data, 
            metric='orders', 
            window=smoothing_window
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    st.markdown("---")
    
    # ======================= TIMELINE OPTIMIZATION =======================
    
    st.markdown('<h2 class="main-text">💡 Timeline Optimization Insights</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">🚀 Process Improvements</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Automate site approval processes to reduce processing time</li>
                <li>Optimize seller dispatch workflows</li>
                <li>Improve shipping partner coordination</li>
                <li>Implement real-time tracking and alerts</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">📊 Performance Monitoring</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Set stage-specific SLAs and monitor compliance</li>
                <li>Track timeline trends for seasonality patterns</li>
                <li>Benchmark against industry delivery standards</li>
                <li>Identify bottlenecks in the fulfillment process</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ======================= DATA EXPLORER =======================
    
    with st.expander("🔍 Explore Timeline Data", expanded=False):
        if len(delivered_timeline) > 0:
            st.markdown("### 📊 Timeline Data Sample")
            
            sample_data = delivered_timeline.head(10)[[
                'order_purchase_timestamp', 'total_hours', 
                'site_hours', 'seller_hours', 'shipping_hours'
            ]].copy()
            
            # Format for display
            sample_data['total_hours'] = sample_data['total_hours'].apply(lambda x: f"{x:.1f}h")
            sample_data['site_hours'] = sample_data['site_hours'].apply(lambda x: f"{x:.1f}h")
            sample_data['seller_hours'] = sample_data['seller_hours'].apply(lambda x: f"{x:.1f}h")
            sample_data['shipping_hours'] = sample_data['shipping_hours'].apply(lambda x: f"{x:.1f}h")
            
            st.dataframe(sample_data, use_container_width=True, hide_index=True)
        else:
            st.info("No complete timeline data available for display.")
    
    # ======================= PAGE FOOTER =======================
    
    st.markdown("---")
    
    if len(delivered_timeline) > 0:
        total_analyzed = len(delivered_timeline)
        median_days = delivered_timeline['total_hours'].median() / 24
        fastest_stage = min(
            ('Site', delivered_timeline['site_hours'].median()),
            ('Seller', delivered_timeline['seller_hours'].median()),
            ('Shipping', delivered_timeline['shipping_hours'].median()),
            key=lambda x: x[1]
        )
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
            <p>
                <b>Order Timelines Analysis</b> • {total_analyzed:,} orders analyzed • 
                Median delivery: {median_days:.1f} days • 
                Fastest stage: {fastest_stage[0]} ({fastest_stage[1]:.1f}h)
            </p>
            <p style="margin-top: 0.5rem;">
                Use stage breakdowns and cumulative distributions to identify timeline optimization opportunities.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
            <p>
                <b>Order Timelines Analysis</b> • No complete timeline data available
            </p>
            <p style="margin-top: 0.5rem;">
                To enable timeline analysis, ensure delivered orders have complete timestamp data.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ======================= CUSTOM CSS =======================

st.markdown("""
<style>
/* Timeline page styling */
.timeline-site { color: #2C7D8B; }
.timeline-seller { color: #2A927A; }
.timeline-shipping { color: #C9D2BA; }

/* Chart optimizations */
.js-plotly-plot .histogram .trace {
    will-change: transform;
}

/* Metric card enhancements */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    transition: all 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(212, 180, 131, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()