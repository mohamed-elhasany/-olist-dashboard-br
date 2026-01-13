# pages/5_🚚_Freight_Analysis.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from analysis.revenue_analysis import (
    RevenueAnalyzer,
    create_freight_weight_scatter,
    create_freight_volume_scatter,
    create_freight_price_scatter,
    create_price_weight_volume_scatter
)

# Page configuration
st.set_page_config(
    page_title="Freight Analysis | Olist Dashboard",
    page_icon="🚚",
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
def get_freight_analysis(order_items, products):
    """Cached freight analysis - optimized for this page only"""
    analyzer = RevenueAnalyzer(order_items, products)
    analyzer.prepare_data()
    
    # Get volume analysis data (already has dimensions calculated)
    volume_data = analyzer.order_items_detailed.copy()
    
    # Filter for products with dimensional data
    dimensional_columns = ['product_weight_g', 'product_length_cm', 
                          'product_height_cm', 'product_width_cm']
    
    volume_analysis_data = volume_data.dropna(subset=dimensional_columns).copy()
    
    if len(volume_analysis_data) > 0:
        # Calculate volume if not already calculated
        if 'Volume_cm' not in volume_analysis_data.columns:
            volume_analysis_data['Volume_cm'] = (
                volume_analysis_data['product_width_cm'] * 
                volume_analysis_data['product_height_cm'] * 
                volume_analysis_data['product_length_cm']
            )
    
    # Calculate freight metrics
    total_freight = volume_data['freight_value'].sum() if len(volume_data) > 0 else 0
    total_price = volume_data['price'].sum() if len(volume_data) > 0 else 0
    freight_ratio = (total_freight / total_price * 100) if total_price > 0 else 0
    
    # Calculate freight efficiency metrics
    if len(volume_analysis_data) > 0:
        volume_analysis_data['freight_per_kg'] = (
            volume_analysis_data['freight_value'] / 
            (volume_analysis_data['product_weight_g'] / 1000)
        ).replace([np.inf, -np.inf], np.nan)
        
        volume_analysis_data['freight_per_m3'] = (
            volume_analysis_data['freight_value'] / 
            (volume_analysis_data['Volume_cm'] / 1_000_000)
        ).replace([np.inf, -np.inf], np.nan)
        
        volume_analysis_data['price_to_freight_ratio'] = (
            volume_analysis_data['price'] / 
            volume_analysis_data['freight_value']
        ).replace([np.inf, -np.inf], np.nan)
    
    return {
        'volume_analysis_data': volume_analysis_data,
        'total_freight': total_freight,
        'total_price': total_price,
        'freight_ratio': freight_ratio,
        'original_data': volume_data,
        'dimensional_columns': dimensional_columns,
        'missing_dimensional': volume_data[dimensional_columns].isna().sum(),
        'analyzer': analyzer
    }

# ======================= HELPER FUNCTIONS =======================

def create_freight_distribution_chart(volume_data):
    """Create distribution chart of freight costs"""
    fig = go.Figure()
    
    # Filter out extreme outliers for better visualization
    freight_data = volume_data['freight_value'].dropna()
    if len(freight_data) > 0:
        q1 = freight_data.quantile(0.25)
        q3 = freight_data.quantile(0.75)
        iqr = q3 - q1
        filtered_data = freight_data[(freight_data >= q1 - 1.5*iqr) & 
                                    (freight_data <= q3 + 1.5*iqr)]
    
    fig.add_trace(go.Histogram(
        x=filtered_data if 'filtered_data' in locals() else freight_data,
        nbinsx=50,
        marker_color='#2C7D8B',
        opacity=0.7,
        name='Freight Distribution',
        hovertemplate='Freight: R$%{x:.2f}<br>Count: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Distribution of Freight Costs',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Freight Value (R$)',
        yaxis_title='Number of Orders',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        showlegend=False
    )
    
    return fig

def create_freight_efficiency_chart(volume_data, metric='freight_per_kg'):
    """Create chart for freight efficiency metrics"""
    
    if metric not in volume_data.columns or volume_data[metric].isna().all():
        # Return empty figure
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'Insufficient Data for Efficiency Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#333333'}
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        return fig
    
    # Filter out extreme outliers
    efficiency_data = volume_data[metric].dropna()
    if len(efficiency_data) > 0:
        q1 = efficiency_data.quantile(0.25)
        q3 = efficiency_data.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5*iqr
        upper_bound = q3 + 1.5*iqr
        filtered_data = efficiency_data[(efficiency_data >= lower_bound) & 
                                       (efficiency_data <= upper_bound)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Box(
        y=filtered_data if 'filtered_data' in locals() else efficiency_data,
        name=metric.replace('_', ' ').title(),
        boxpoints='outliers',
        marker_color='#2A927A',
        line_color='#2A927A'
    ))
    
    metric_labels = {
        'freight_per_kg': 'Freight per kg (R$/kg)',
        'freight_per_m3': 'Freight per m³ (R$/m³)',
        'price_to_freight_ratio': 'Price to Freight Ratio'
    }
    
    fig.update_layout(
        title={
            'text': f'Freight Efficiency: {metric_labels.get(metric, metric)}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        yaxis_title=metric_labels.get(metric, metric),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        showlegend=False
    )
    
    return fig

def create_freight_by_category_chart(volume_data):
    """Create chart showing average freight by product category"""
    
    # Group by category and calculate average freight
    if 'product_category_name' in volume_data.columns:
        category_freight = volume_data.groupby('product_category_name').agg(
            avg_freight=('freight_value', 'mean'),
            count=('freight_value', 'count')
        ).reset_index()
        
        # Get top 20 categories by count
        top_categories = category_freight.nlargest(20, 'count')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=top_categories['avg_freight'],
            y=top_categories['product_category_name'],
            orientation='h',
            marker_color='#C9D2BA',
            text=[f'R${val:.2f}' for val in top_categories['avg_freight']],
            textposition='auto',
            textfont=dict(size=10, color='#202020'),
            hovertemplate='<b>%{y}</b><br>' +
                         'Avg Freight: R$%{x:.2f}<br>' +
                         'Orders: %{customdata}<br>' +
                         '<extra></extra>',
            customdata=top_categories['count']
        ))
        
        fig.update_layout(
            title={
                'text': 'Average Freight by Product Category (Top 20)',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#333333'}
            },
            xaxis_title='Average Freight Value (R$)',
            yaxis_title='Product Category',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333333'),
            height=500,
            margin=dict(l=200, r=50, t=80, b=50),
            yaxis=dict(
                categoryorder='total ascending',
                tickfont=dict(size=11)
            )
        )
        
        return fig
    
    # Return empty figure if no category data
    fig = go.Figure()
    fig.update_layout(
        title={
            'text': 'No Category Data Available',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    return fig

# ======================= PAGE INITIALIZATION =======================

def initialize_page():
    """Initialize the freight analysis page"""
    
    # Check if data is loaded
    if not st.session_state.get('data_loaded', False):
        st.error("⚠️ Data not loaded. Please go to the Home page and click 'Load All Data'.")
        st.stop()
    
    if st.session_state.order_items is None or st.session_state.products is None:
        st.error("❌ Required data not available. Please reload data from Home page.")
        st.stop()
    
    # Initialize freight analysis with caching
    if 'freight_analysis' not in st.session_state:
        with st.spinner("🚚 Analyzing freight data..."):
            results = get_freight_analysis(
                st.session_state.order_items, 
                st.session_state.products
            )
            st.session_state.freight_analysis = results
    
    return st.session_state.freight_analysis

# ======================= MAIN PAGE CONTENT =======================

def main():
    """Main content for Freight Analysis page"""
    
    # Page header
    st.markdown("""
    <h1 class="main-text">🚚 Freight Analysis</h1>
    <p class="sub-text">Shipping cost analysis by product dimensions, weight, and pricing</p>
    """, unsafe_allow_html=True)
    
    # Quick navigation
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <p style="color: var(--dark-text-secondary); margin: 0;">
            🔍 <b>Related Analysis:</b> 
            <a href="/💰_Revenue_Overview" style="color: var(--dark-text-cool);">Revenue Overview</a> • 
            <a href="/📦_Product_Category_Analysis" style="color: var(--dark-text-cool);">Category Analysis</a> • 
            <a href="/🏢_Vendor_Analysis" style="color: var(--dark-text-cool);">Vendor Analysis</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize data
    analysis_data = initialize_page()
    
    # ======================= FREIGHT OVERVIEW =======================
    
    st.markdown('<h2 class="main-text">📊 Freight Overview</h2>', unsafe_allow_html=True)
    
    # Data availability warning
    if len(analysis_data['volume_analysis_data']) == 0:
        st.error("""
        ⚠️ **No Dimensional Data Available**
        
        This analysis requires product dimensional data (weight, length, height, width).
        No products with complete dimensional information were found in the dataset.
        
        Basic freight statistics are still available below.
        """)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Freight Revenue",
            value=f"R${analysis_data['total_freight']:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Freight % of Total",
            value=f"{analysis_data['freight_ratio']:.1f}%",
            delta=None
        )
    
    with col3:
        if len(analysis_data['volume_analysis_data']) > 0:
            avg_freight = analysis_data['volume_analysis_data']['freight_value'].mean()
            st.metric(
                label="Avg Freight per Order",
                value=f"R${avg_freight:.2f}",
                delta=None
            )
        else:
            st.metric(
                label="Orders with Dimensions",
                value="0",
                delta=None
            )
    
    with col4:
        if len(analysis_data['volume_analysis_data']) > 0:
            dimensional_orders = len(analysis_data['volume_analysis_data'])
            total_orders = len(analysis_data['original_data'])
            coverage_pct = (dimensional_orders / total_orders * 100) if total_orders > 0 else 0
            st.metric(
                label="Data Coverage",
                value=f"{coverage_pct:.1f}%",
                delta=None
            )
        else:
            missing_total = analysis_data['missing_dimensional'].sum()
            st.metric(
                label="Missing Dimensions",
                value=f"{missing_total:,}",
                delta=None
            )
    
    # Data coverage details
    if len(analysis_data['volume_analysis_data']) > 0:
        dimensional_orders = len(analysis_data['volume_analysis_data'])
        total_orders = len(analysis_data['original_data'])
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1rem; margin: 1rem 0;">
            <p style="color: var(--dark-text-secondary); margin: 0;">
                📊 <b>Data Coverage:</b> {dimensional_orders:,} of {total_orders:,} orders have complete dimensional data ({dimensional_orders/total_orders*100:.1f}%)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= FREIGHT DISTRIBUTION =======================
    
    st.markdown('<h2 class="main-text">📈 Freight Distribution Analysis</h2>', unsafe_allow_html=True)
    
    if len(analysis_data['original_data']) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Freight distribution histogram
            fig_dist = create_freight_distribution_chart(analysis_data['original_data'])
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col2:
            # Freight by category
            fig_category = create_freight_by_category_chart(analysis_data['original_data'])
            st.plotly_chart(fig_category, use_container_width=True)
    
    st.markdown("---")
    
    # ======================= DIMENSIONAL ANALYSIS =======================
    
    st.markdown('<h2 class="main-text">📏 Dimensional Analysis</h2>', unsafe_allow_html=True)
    
    if len(analysis_data['volume_analysis_data']) > 0:
        
        # Interactive controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            chart_type = st.selectbox(
                "Analysis Type",
                ["Weight vs Freight", "Volume vs Freight", "Price vs Freight", "3D Analysis"],
                help="Select which dimensional relationship to analyze"
            )
        
        with col2:
            sample_size = st.slider(
                "Sample Size",
                min_value=100,
                max_value=5000,
                value=1000,
                step=100,
                help="Number of data points to display (for performance)"
            )
        
        with col3:
            opacity = st.slider(
                "Point Opacity",
                min_value=0.1,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Adjust transparency of scatter points"
            )
        
        # Sample data for better performance
        if len(analysis_data['volume_analysis_data']) > sample_size:
            sample_data = analysis_data['volume_analysis_data'].sample(sample_size, random_state=42)
        else:
            sample_data = analysis_data['volume_analysis_data']
        
        # Display selected chart
        if chart_type == "Weight vs Freight":
            fig = create_freight_weight_scatter(sample_data)
            fig.update_traces(marker=dict(opacity=opacity))
            st.plotly_chart(fig, use_container_width=True)
            
            # Correlation analysis
            correlation = sample_data[['product_weight_g', 'freight_value']].corr().iloc[0,1]
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <p style="color: var(--dark-text-secondary); margin: 0;">
                    📊 <b>Correlation Analysis:</b> Weight vs Freight correlation: {correlation:.3f}
                    {"(Strong positive)" if correlation > 0.7 else 
                     "(Moderate positive)" if correlation > 0.3 else 
                     "(Weak positive)" if correlation > 0 else 
                     "(Weak negative)" if correlation > -0.3 else 
                     "(Moderate negative)" if correlation > -0.7 else 
                     "(Strong negative)"}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        elif chart_type == "Volume vs Freight":
            fig = create_freight_volume_scatter(sample_data)
            fig.update_traces(marker=dict(opacity=opacity))
            st.plotly_chart(fig, use_container_width=True)
            
            # Correlation analysis
            correlation = sample_data[['Volume_cm', 'freight_value']].corr().iloc[0,1]
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <p style="color: var(--dark-text-secondary); margin: 0;">
                    📊 <b>Correlation Analysis:</b> Volume vs Freight correlation: {correlation:.3f}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        elif chart_type == "Price vs Freight":
            fig = create_freight_price_scatter(sample_data)
            fig.update_traces(marker=dict(opacity=opacity))
            st.plotly_chart(fig, use_container_width=True)
            
            # Correlation analysis
            correlation = sample_data[['price', 'freight_value']].corr().iloc[0,1]
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <p style="color: var(--dark-text-secondary); margin: 0;">
                    📊 <b>Correlation Analysis:</b> Price vs Freight correlation: {correlation:.3f}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        else:  # 3D Analysis
            fig = create_price_weight_volume_scatter(sample_data)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <p style="color: var(--dark-text-secondary); margin: 0;">
                    💡 <b>3D Analysis:</b> Bubble size represents product volume. 
                    Hover over points to see weight, price, and volume details.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ======================= FREIGHT EFFICIENCY =======================
        
        st.markdown('<h2 class="main-text">⚡ Freight Efficiency Metrics</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            efficiency_metric = st.selectbox(
                "Efficiency Metric",
                ["Freight per kg (R$/kg)", "Freight per m³ (R$/m³)", "Price to Freight Ratio"],
                help="Select which efficiency metric to analyze"
            )
        
        with col2:
            show_outliers = st.checkbox(
                "Show Statistical Summary",
                value=True,
                help="Display statistical summary of efficiency metrics"
            )
        
        # Map selection to actual column names
        metric_map = {
            "Freight per kg (R$/kg)": "freight_per_kg",
            "Freight per m³ (R$/m³)": "freight_per_m3",
            "Price to Freight Ratio": "price_to_freight_ratio"
        }
        
        selected_metric = metric_map[efficiency_metric]
        
        # Create efficiency chart
        fig_efficiency = create_freight_efficiency_chart(sample_data, selected_metric)
        st.plotly_chart(fig_efficiency, use_container_width=True)
        
        # Statistical summary
        if show_outliers and selected_metric in sample_data.columns:
            metric_data = sample_data[selected_metric].dropna()
            if len(metric_data) > 0:
                stats = {
                    'mean': metric_data.mean(),
                    'median': metric_data.median(),
                    'std': metric_data.std(),
                    'min': metric_data.min(),
                    'max': metric_data.max(),
                    'q1': metric_data.quantile(0.25),
                    'q3': metric_data.quantile(0.75)
                }
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                                border-radius: 8px; padding: 0.8rem; text-align: center;">
                        <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">Mean</div>
                        <div style="color: var(--dark-text-primary); font-size: 1.2rem; font-weight: 600;">
                            {stats['mean']:.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                                border-radius: 8px; padding: 0.8rem; text-align: center;">
                        <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">Median</div>
                        <div style="color: var(--dark-text-primary); font-size: 1.2rem; font-weight: 600;">
                            {stats['median']:.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                                border-radius: 8px; padding: 0.8rem; text-align: center;">
                        <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">Std Dev</div>
                        <div style="color: var(--dark-text-primary); font-size: 1.2rem; font-weight: 600;">
                            {stats['std']:.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                                border-radius: 8px; padding: 0.8rem; text-align: center;">
                        <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">IQR</div>
                        <div style="color: var(--dark-text-primary); font-size: 1.2rem; font-weight: 600;">
                            {stats['q3'] - stats['q1']:.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    else:
        # Show missing data message
        st.warning("""
        ⚠️ **Dimensional Analysis Unavailable**
        
        To view dimensional analysis charts, products with complete dimensional data are required:
        - Product Weight (grams)
        - Product Length (cm)
        - Product Height (cm)
        - Product Width (cm)
        
        Currently, no products in the dataset have all these dimensions recorded.
        """)
        
        # Show what dimensions are missing
        if analysis_data['missing_dimensional'].sum() > 0:
            st.markdown("### 📋 Missing Data Summary")
            missing_df = pd.DataFrame({
                'Dimension': analysis_data['dimensional_columns'],
                'Missing Count': analysis_data['missing_dimensional'].values,
                'Missing %': (analysis_data['missing_dimensional'].values / 
                             len(analysis_data['original_data']) * 100)
            })
            st.dataframe(missing_df, use_container_width=True)
    
    st.markdown("---")
    
    # ======================= OPTIMIZATION INSIGHTS =======================
    
    st.markdown('<h2 class="main-text">💡 Freight Optimization Insights</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">🚀 Cost Reduction</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Negotiate better freight rates for high-volume categories</li>
                <li>Optimize packaging to reduce dimensional weight</li>
                <li>Bundle shipments to achieve economies of scale</li>
                <li>Implement weight-based pricing tiers</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">📊 Pricing Strategy</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Adjust product pricing based on freight costs</li>
                <li>Implement free shipping thresholds strategically</li>
                <li>Consider regional shipping cost variations</li>
                <li>Monitor freight as percentage of total revenue</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ======================= DATA EXPLORER =======================
    
    with st.expander("🔍 Explore Freight Data", expanded=False):
        st.markdown("### 📊 Raw Data Sample")
        
        if len(analysis_data['volume_analysis_data']) > 0:
            sample_size = min(100, len(analysis_data['volume_analysis_data']))
            sample_data = analysis_data['volume_analysis_data'].head(sample_size)
            
            # Select columns to display
            display_cols = ['product_id', 'product_category_name', 'price', 'freight_value']
            if 'Volume_cm' in sample_data.columns:
                display_cols.append('Volume_cm')
            if 'product_weight_g' in sample_data.columns:
                display_cols.append('product_weight_g')
            
            display_data = sample_data[display_cols].copy()
            display_data['price'] = display_data['price'].apply(lambda x: f"R${x:.2f}")
            display_data['freight_value'] = display_data['freight_value'].apply(lambda x: f"R${x:.2f}")
            
            if 'Volume_cm' in display_data.columns:
                display_data['Volume_cm'] = display_data['Volume_cm'].apply(lambda x: f"{x:,.0f} cm³")
            if 'product_weight_g' in display_data.columns:
                display_data['product_weight_g'] = display_data['product_weight_g'].apply(lambda x: f"{x:,.0f} g")
            
            st.dataframe(display_data, use_container_width=True)
        else:
            st.info("No dimensional data available to display.")
    
    # ======================= PAGE FOOTER =======================
    
    st.markdown("---")
    
    total_freight = analysis_data['total_freight']
    freight_ratio = analysis_data['freight_ratio']
    data_coverage = len(analysis_data['volume_analysis_data'])
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
        <p>
            <b>Freight Analysis</b> • Total freight: R${total_freight:,.0f} • 
            Freight ratio: {freight_ratio:.1f}% • 
            Orders with dimensions: {data_coverage:,}
        </p>
        <p style="margin-top: 0.5rem;">
            Use dimensional analysis to optimize shipping costs and improve pricing strategies.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ======================= CUSTOM CSS =======================

st.markdown("""
<style>
/* Custom freight page styling */
.freight-high { color: #8B4513; }
.freight-medium { color: #C9D2BA; }
.freight-low { color: #2A927A; }

/* Scatter plot optimization */
.js-plotly-plot .scatterlayer .trace {
    will-change: transform;
}

/* Metric card animations */
div[data-testid="stMetric"] {
    transition: all 0.3s ease;
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(212, 180, 131, 0.3) !important;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()