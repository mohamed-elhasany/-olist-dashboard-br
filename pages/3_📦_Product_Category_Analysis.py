# pages/3_📦_Product_Category_Analysis.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from analysis.revenue_analysis import (
    RevenueAnalyzer,
    create_category_revenue_chart,
    get_revenue_metrics_display
)

# Page configuration
st.set_page_config(
    page_title="Product Category Analysis | Olist Dashboard",
    page_icon="📦",
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
def get_category_analysis(order_items, products):
    """Cached category analysis - optimized for this page only"""
    analyzer = RevenueAnalyzer(order_items, products)
    analyzer.prepare_data()
    
    # Get ONLY category data we need (not full analysis)
    category_all = analyzer._analyze_by_category('Total')
    category_price = analyzer._analyze_by_category('price')
    category_freight = analyzer._analyze_by_category('freight_value')
    
    # Calculate category statistics
    total_revenue = category_all['Total'].sum()
    top_category = category_all.iloc[0] if len(category_all) > 0 else None
    
    return {
        'category_all': category_all,
        'category_price': category_price,
        'category_freight': category_freight,
        'total_revenue': total_revenue,
        'top_category': top_category,
        'analyzer': analyzer
    }

# ======================= PAGE INITIALIZATION =======================

def initialize_page():
    """Initialize the product category analysis page"""
    
    # Check if data is loaded
    if not st.session_state.get('data_loaded', False):
        st.error("⚠️ Data not loaded. Please go to the Home page and click 'Load All Data'.")
        st.stop()
    
    if st.session_state.order_items is None or st.session_state.products is None:
        st.error("❌ Required data not available. Please reload data from Home page.")
        st.stop()
    
    # Initialize category analysis with caching
    if 'category_analysis' not in st.session_state:
        with st.spinner("📊 Analyzing product categories..."):
            results = get_category_analysis(
                st.session_state.order_items, 
                st.session_state.products
            )
            st.session_state.category_analysis = results
    
    return st.session_state.category_analysis

# ======================= MAIN PAGE CONTENT =======================

def main():
    """Main content for Product Category Analysis page"""
    
    # Page header
    st.markdown("""
    <h1 class="main-text">📦 Product Category Analysis</h1>
    <p class="sub-text">Deep dive into revenue performance across product categories</p>
    """, unsafe_allow_html=True)
    
    # Quick navigation
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <p style="color: var(--dark-text-secondary); margin: 0;">
            🔍 <b>Related Analysis:</b> 
            <a href="/💰_Revenue_Overview" style="color: var(--dark-text-cool);">Revenue Overview</a> • 
            <a href="/🏢_Vendor_Analysis" style="color: var(--dark-text-cool);">Vendor Analysis</a> • 
            <a href="/🚚_Freight_Analysis" style="color: var(--dark-text-cool);">Freight Analysis</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize data
    analysis_data = initialize_page()
    
    # ======================= CATEGORY OVERVIEW =======================
    
    st.markdown('<h2 class="main-text">📊 Category Overview</h2>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Categories",
            value=f"{len(analysis_data['category_all']):,}",
            delta=None
        )
    
    with col2:
        total_rev = analysis_data['category_all']['Total'].sum()
        st.metric(
            label="Total Category Revenue",
            value=f"R${total_rev:,.0f}",
            delta=None
        )
    
    with col3:
        avg_rev = analysis_data['category_all']['Total'].mean()
        st.metric(
            label="Avg Revenue per Category",
            value=f"R${avg_rev:,.0f}",
            delta=None
        )
    
    with col4:
        if analysis_data['top_category'] is not None:
            top_cat_name = analysis_data['top_category']['product_category_name'][:20]
            st.metric(
                label="Top Category",
                value=top_cat_name,
                delta=None
            )
    
    # Concentration analysis
    st.markdown("### 🎯 Revenue Concentration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Top 5 categories percentage
        top_5_sum = analysis_data['category_all'].head(5)['Total'].sum()
        top_5_pct = (top_5_sum / total_rev * 100) if total_rev > 0 else 0
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1rem; text-align: center;">
            <div style="font-size: 2rem; color: var(--dark-text-warm); font-weight: 600;">
                {top_5_pct:.1f}%
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                Top 5 Categories<br>Revenue Share
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Top 10 categories percentage
        top_10_sum = analysis_data['category_all'].head(10)['Total'].sum()
        top_10_pct = (top_10_sum / total_rev * 100) if total_rev > 0 else 0
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1rem; text-align: center;">
            <div style="font-size: 2rem; color: var(--dark-text-warm); font-weight: 600;">
                {top_10_pct:.1f}%
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                Top 10 Categories<br>Revenue Share
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Revenue distribution Gini-like measure
        sorted_rev = analysis_data['category_all']['Total'].sort_values(ascending=False).values
        cumulative_pct = sorted_rev.cumsum() / sorted_rev.sum() * 100 if sorted_rev.sum() > 0 else 0
        half_categories = len(sorted_rev) // 2
        if len(cumulative_pct) > half_categories:
            half_pct = cumulative_pct[half_categories]
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="font-size: 2rem; color: var(--dark-text-warm); font-weight: 600;">
                    {half_pct:.1f}%
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                    Top 50% Categories<br>Revenue Share
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= INTERACTIVE CONTROLS =======================
    
    st.markdown('<h2 class="main-text">📈 Interactive Category Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories_to_show = st.slider(
            "Number of Categories to Display",
            min_value=5,
            max_value=50,
            value=20,
            help="Adjust how many categories to show in charts"
        )
    
    with col2:
        chart_height = st.slider(
            "Chart Height",
            min_value=400,
            max_value=800,
            value=500,
            step=50,
            help="Adjust chart height for better visibility"
        )
    
    with col3:
        revenue_type = st.selectbox(
            "Revenue Breakdown",
            ["Total Revenue", "Product Revenue", "Freight Revenue"],
            help="Select which revenue component to analyze"
        )
    
    # Select appropriate dataset based on revenue type
    if revenue_type == "Total Revenue":
        category_data = analysis_data['category_all']
        title_suffix = "Total Revenue"
    elif revenue_type == "Product Revenue":
        category_data = analysis_data['category_price']
        title_suffix = "Product Revenue"
    else:  # Freight Revenue
        category_data = analysis_data['category_freight']
        title_suffix = "Freight Revenue"
    
    # ======================= MAIN CATEGORY CHART =======================
    
    fig = create_category_revenue_chart(
        category_data, 
        top_n=categories_to_show
    )
    
    # Update title to reflect selection
    fig.update_layout(
        height=chart_height,
        title={
            'text': f'Top {categories_to_show} Categories by {title_suffix}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ======================= CATEGORY COMPARISON =======================
    
    st.markdown('<h2 class="main-text">📊 Category Comparison</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue distribution chart
        st.markdown("### 📈 Revenue Distribution")
        
        # Calculate deciles
        category_data_sorted = category_data.sort_values('Total', ascending=False).copy()
        category_data_sorted['cumulative_pct'] = (category_data_sorted['Total'].cumsum() / 
                                                 category_data_sorted['Total'].sum() * 100)
        
        fig_dist = go.Figure()
        
        fig_dist.add_trace(go.Scatter(
            x=list(range(1, len(category_data_sorted) + 1)),
            y=category_data_sorted['cumulative_pct'],
            mode='lines',
            line=dict(color='#2C7D8B', width=3),
            fill='tozeroy',
            fillcolor='rgba(44, 125, 139, 0.2)',
            name='Cumulative %'
        ))
        
        fig_dist.update_layout(
            height=300,
            title="Revenue Concentration (Lorenz Curve)",
            xaxis_title="Categories (sorted by revenue)",
            yaxis_title="Cumulative Revenue %",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333333'),
            showlegend=False
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Top vs Bottom comparison
        st.markdown("### ⚖️ Top vs Bottom Comparison")
        
        top_n = min(10, len(category_data))
        top_categories = category_data.head(top_n)
        bottom_categories = category_data.tail(top_n)
        
        top_avg = top_categories['Total'].mean()
        bottom_avg = bottom_categories['Total'].mean()
        ratio = top_avg / bottom_avg if bottom_avg > 0 else 0
        
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem; margin: 0.5rem 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                <div>
                    <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Top {top_n} Avg</div>
                    <div style="color: var(--dark-text-warm); font-size: 1.5rem; font-weight: 600;">
                        R${top_avg:,.0f}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Bottom {top_n} Avg</div>
                    <div style="color: var(--dark-text-cool); font-size: 1.5rem; font-weight: 600;">
                        R${bottom_avg:,.0f}
                    </div>
                </div>
            </div>
            <div style="text-align: center; padding-top: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Performance Ratio</div>
                <div style="color: var(--dark-text-primary); font-size: 1.8rem; font-weight: 700;">
                    {ratio:.1f}x
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">
                    Top categories earn {ratio:.1f} times more than bottom categories
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= CATEGORY DETAILS TABLE =======================
    
    with st.expander("📋 Detailed Category Data", expanded=False):
        st.markdown(f"### 📊 {revenue_type} by Category")
        
        # Create enhanced dataframe
        detailed_df = category_data.copy()
        
        # Calculate percentages
        total_rev = detailed_df['Total'].sum()
        detailed_df['Revenue %'] = (detailed_df['Total'] / total_rev * 100) if total_rev > 0 else 0
        detailed_df['Cumulative %'] = detailed_df['Revenue %'].cumsum()
        
        # Format columns
        detailed_df['Total'] = detailed_df['Total'].apply(lambda x: f"R${x:,.0f}")
        detailed_df['Revenue %'] = detailed_df['Revenue %'].apply(lambda x: f"{x:.1f}%")
        detailed_df['Cumulative %'] = detailed_df['Cumulative %'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(
            detailed_df.head(categories_to_show),
            use_container_width=True,
            column_config={
                "product_category_name": st.column_config.TextColumn("Category", width="large"),
                "Total": st.column_config.TextColumn("Revenue"),
                "Revenue %": st.column_config.TextColumn("Share"),
                "Cumulative %": st.column_config.TextColumn("Cumulative Share")
            },
            hide_index=True
        )
        
        # Export option
        csv = detailed_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Category Data (CSV)",
            data=csv,
            file_name=f"olist_category_analysis_{revenue_type.replace(' ', '_').lower()}.csv",
            mime="text/csv",
            type="secondary"
        )
    
    # ======================= INSIGHTS & RECOMMENDATIONS =======================
    
    st.markdown("---")
    
    st.markdown('<h2 class="main-text">💡 Category Insights</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">🎯 Focus Areas</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Identify high-performing categories for inventory optimization</li>
                <li>Monitor category concentration risks</li>
                <li>Analyze seasonal trends in top categories</li>
                <li>Compare category performance vs. industry benchmarks</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">📈 Growth Opportunities</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Expand selection in high-margin categories</li>
                <li>Improve visibility for underperforming categories</li>
                <li>Bundle complementary categories</li>
                <li>Optimize pricing strategies by category</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ======================= PAGE FOOTER =======================
    
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
        <p>
            <b>Product Category Analysis</b> • {:,} categories analyzed • 
            Total revenue: R${:,.0f}
        </p>
        <p style="margin-top: 0.5rem;">
            Use the interactive controls to explore different revenue components and category performance.
        </p>
    </div>
    """.format(len(analysis_data['category_all']), total_rev), unsafe_allow_html=True)

# ======================= CUSTOM CSS =======================

st.markdown("""
<style>
/* Performance optimizations for this page */
.stPlotlyChart {
    will-change: transform;
    contain: layout;
}

/* Custom scrollbar for data tables */
div[data-testid="stDataFrame"]::-webkit-scrollbar {
    height: 8px;
}

div[data-testid="stDataFrame"]::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
}

div[data-testid="stDataFrame"]::-webkit-scrollbar-thumb {
    background: rgba(212, 180, 131, 0.3);
    border-radius: 4px;
}

/* Smooth hover effects */
div[data-testid="stMetric"] {
    transition: transform 0.2s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()