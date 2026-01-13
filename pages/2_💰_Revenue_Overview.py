# pages/2_💰_Revenue_Overview.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from analysis.revenue_analysis import (
    RevenueAnalyzer,
    create_category_revenue_chart,
    create_vendor_revenue_chart,
    get_revenue_metrics_display
)

# Page configuration
st.set_page_config(
    page_title="Revenue Overview | Olist Dashboard",
    page_icon="💰",
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
def get_analyzer_and_results(order_items, products):
    """Cached analyzer initialization - ONLY ONCE per session"""
    analyzer = RevenueAnalyzer(order_items, products)
    analysis_results = analyzer.run_comprehensive_analysis()
    return analyzer, analysis_results

# ======================= PAGE INITIALIZATION =======================

def initialize_page():
    """Initialize the revenue overview page"""
    
    # Check if data is loaded
    if not st.session_state.get('data_loaded', False):
        st.error("⚠️ Data not loaded. Please go to the Home page and click 'Load All Data'.")
        st.stop()
    
    if st.session_state.order_items is None or st.session_state.products is None:
        st.error("❌ Required data not available. Please reload data from Home page.")
        st.stop()
    
    # Initialize analyzer with caching
    if 'revenue_analyzer' not in st.session_state:
        with st.spinner("🔍 Analyzing revenue data..."):
            analyzer, results = get_analyzer_and_results(
                st.session_state.order_items, 
                st.session_state.products
            )
            st.session_state.revenue_analyzer = analyzer
            st.session_state.revenue_analysis = results
    
    return st.session_state.revenue_analyzer, st.session_state.revenue_analysis

# ======================= MAIN PAGE CONTENT =======================

def main():
    """Main content for Revenue Overview page"""
    
    # Page header
    st.markdown("""
    <h1 class="main-text">💰 Revenue Overview</h1>
    <p class="sub-text">Key metrics, top performers, and high-level revenue insights</p>
    """, unsafe_allow_html=True)
    
    # Quick navigation
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <p style="color: var(--dark-text-secondary); margin: 0;">
            🔍 <b>Explore deeper:</b> 
            <a href="/📦_Product_Category_Analysis" style="color: var(--dark-text-cool);">Category Analysis</a> • 
            <a href="/🏢_Vendor_Analysis" style="color: var(--dark-text-cool);">Vendor Analysis</a> • 
            <a href="/🚚_Freight_Analysis" style="color: var(--dark-text-cool);">Freight Analysis</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize data
    analyzer, analysis_results = initialize_page()
    
    # ======================= KEY METRICS DASHBOARD =======================
    
    st.markdown('<h2 class="main-text">📊 Revenue Dashboard</h2>', unsafe_allow_html=True)
    
    # Create metrics columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Revenue",
            value=f"R${analysis_results['total_revenue']:,.0f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Avg Order Value",
            value=f"R${analysis_results['average_order_value']:,.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Total Orders",
            value=f"{analysis_results['total_orders']:,}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Products Sold",
            value=f"{analysis_results['total_products']:,}",
            delta=None
        )
    
    with col5:
        st.metric(
            label="Items per Order",
            value=f"{analysis_results['avg_items_per_order']:.2f}",
            delta=None
        )
    # ADD THIS note AFTER THE METRICS SECTION:
    orders_discrepancy = len(st.session_state.orders) - analysis_results['total_orders']
    st.markdown(f"""
    <div style="background:rgb(109, 75, 74); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <p style="color:rgb(0, 0, 0); margin: 0;">
            📝 <b>Note:</b> Revenue analysis includes only orders with items. 
            This excludes {orders_discrepancy:,} orders without items in the system.
        </p>
    </div>
    """, unsafe_allow_html=True)
    # Summary statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem; margin-top: 1rem;">
            <h3 class="cool-text" style="margin-top: 0;">📈 Revenue Composition</h3>
            <p style="color: var(--dark-text-secondary);">
                <b>Product Revenue:</b> R${:,.0f}<br>
                <b>Freight Revenue:</b> R${:,.0f}<br>
                <b>Freight % of Total:</b> {:.1f}%
            </p>
        </div>
        """.format(
            analysis_results['category_revenue_price']['Total'].sum(),
            analysis_results['category_revenue_freight']['Total'].sum(),
            (analysis_results['category_revenue_freight']['Total'].sum() / 
             analysis_results['total_revenue'] * 100) if analysis_results['total_revenue'] > 0 else 0
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem; margin-top: 1rem;">
            <h3 class="cool-text" style="margin-top: 0;">📊 Distribution</h3>
            <p style="color: var(--dark-text-secondary);">
                <b>Categories:</b> {:,}<br>
                <b>Active Vendors:</b> {:,}<br>
                <b>Avg Revenue per Vendor:</b> R${:,.0f}
            </p>
        </div>
        """.format(
            len(analysis_results['category_revenue_all']),
            len(analysis_results['vendor_revenue_all']),
            analysis_results['vendor_revenue_all']['Total'].mean() if len(analysis_results['vendor_revenue_all']) > 0 else 0
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= TOP PERFORMERS QUICK VIEW =======================
    
    st.markdown('<h2 class="main-text">🏆 Top Performers</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 Categories
        st.markdown('<h3 class="warm-text">📦 Top 5 Product Categories</h3>', unsafe_allow_html=True)
        
        top_5_categories = analysis_results['category_revenue_all'].head(5)
        
        for idx, row in top_5_categories.iterrows():
            revenue_pct = (row['Total'] / analysis_results['total_revenue'] * 100) if analysis_results['total_revenue'] > 0 else 0
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 6px; padding: 0.8rem; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: var(--dark-text-primary); font-weight: 500;">{row['product_category_name']}</span>
                    <span style="color: var(--dark-text-warm); font-weight: 600;">R${row['Total']:,.0f}</span>
                </div>
                <div style="margin-top: 0.3rem;">
                    <div style="background: rgba(255, 255, 255, 0.1); height: 4px; border-radius: 2px; overflow: hidden;">
                        <div style="background: var(--dark-text-warm); height: 100%; width: {min(revenue_pct, 100)}%;"></div>
                    </div>
                    <small style="color: var(--dark-text-secondary);">{revenue_pct:.1f}% of total revenue</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Top 5 Vendors
        st.markdown('<h3 class="warm-text">🏢 Top 5 Vendors</h3>', unsafe_allow_html=True)
        
        top_5_vendors = analysis_results['vendor_revenue_all'].head(5)
        
        for idx, row in top_5_vendors.iterrows():
            revenue_pct = (row['Total'] / analysis_results['total_revenue'] * 100) if analysis_results['total_revenue'] > 0 else 0
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 6px; padding: 0.8rem; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: var(--dark-text-primary); font-weight: 500;">Vendor {row['seller_id']}</span>
                    <span style="color: var(--dark-text-warm); font-weight: 600;">R${row['Total']:,.0f}</span>
                </div>
                <div style="margin-top: 0.3rem;">
                    <div style="background: rgba(255, 255, 255, 0.1); height: 4px; border-radius: 2px; overflow: hidden;">
                        <div style="background: var(--dark-text-warm); height: 100%; width: {min(revenue_pct, 100)}%;"></div>
                    </div>
                    <small style="color: var(--dark-text-secondary);">{revenue_pct:.1f}% of total revenue</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= QUICK CHARTS PREVIEW =======================
    
    st.markdown('<h2 class="main-text">📈 Quick Charts Preview</h2>', unsafe_allow_html=True)
    
    # Simple controls
    col1, col2 = st.columns(2)
    
    with col1:
        chart_type = st.selectbox(
            "Preview Chart Type",
            ["Top Categories", "Top Vendors"],
            help="Select which chart to preview"
        )
    
    with col2:
        items_to_show = st.slider(
            "Items to Show",
            min_value=5,
            max_value=15,
            value=10,
            help="Number of items to display in the preview chart"
        )
    
    # Single chart preview (not multiple)
    if chart_type == "Top Categories":
        fig = create_category_revenue_chart(
            analysis_results['category_revenue_all'], 
            top_n=items_to_show
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = create_vendor_revenue_chart(
            analysis_results['vendor_revenue_all'], 
            top_n=items_to_show
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div style="text-align: center; margin: 1rem 0; padding: 1rem; 
                background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
        <p style="color: var(--dark-text-secondary); margin: 0;">
            💡 <b>Need deeper analysis?</b> 
            Click the links above to explore detailed category, vendor, or freight analysis pages.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= DATA SUMMARY =======================
    
    with st.expander("📊 Detailed Metrics Summary", expanded=False):
        st.markdown(get_revenue_metrics_display(analyzer.get_metrics_summary()))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📦 Category Distribution")
            top_categories_sum = analysis_results['category_revenue_all'].head(10)['Total'].sum()
            total_categories_rev = analysis_results['category_revenue_all']['Total'].sum()
            top_categories_pct = (top_categories_sum / total_categories_rev * 100) if total_categories_rev > 0 else 0
            
            st.markdown(f"""
            - **Top 10 Categories:** {top_categories_pct:.1f}% of category revenue
            - **Total Categories:** {len(analysis_results['category_revenue_all']):,}
            - **Category Concentration:** {analysis_results['category_revenue_all']['Total'].std():,.0f} std dev
            """)
        
        with col2:
            st.markdown("### 🏢 Vendor Distribution")
            top_vendors_sum = analysis_results['vendor_revenue_all'].head(10)['Total'].sum()
            total_vendors_rev = analysis_results['vendor_revenue_all']['Total'].sum()
            top_vendors_pct = (top_vendors_sum / total_vendors_rev * 100) if total_vendors_rev > 0 else 0
            
            st.markdown(f"""
            - **Top 10 Vendors:** {top_vendors_pct:.1f}% of vendor revenue
            - **Total Vendors:** {len(analysis_results['vendor_revenue_all']):,}
            - **Vendor Concentration:** {analysis_results['vendor_revenue_all']['Total'].std():,.0f} std dev
            """)
    
    # ======================= PAGE FOOTER =======================
    
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
        <p>
            <b>Revenue Overview</b> • Quick metrics and top performers • 
            For detailed analysis, visit the specialized pages linked above.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ======================= CUSTOM CSS =======================

st.markdown("""
<style>
/* Performance optimizations */
.js-plotly-plot .plotly, .plotly-graph-div {
    will-change: transform;
}

/* Simple hover effects */
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    transition: transform 0.2s ease;
}

/* Optimized animations */
* {
    animation-duration: 0.3s !important;
}
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()