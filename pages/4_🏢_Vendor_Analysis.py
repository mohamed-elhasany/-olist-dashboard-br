# pages/4_🏢_Vendor_Analysis.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from analysis.revenue_analysis import (
    RevenueAnalyzer,
    create_vendor_revenue_chart
)

# Page configuration
st.set_page_config(
    page_title="Vendor Analysis | Olist Dashboard",
    page_icon="🏢",
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
def get_vendor_analysis(order_items, products):
    """Cached vendor analysis - optimized for this page only"""
    analyzer = RevenueAnalyzer(order_items, products)
    analyzer.prepare_data()
    
    # Get ONLY vendor data we need
    vendor_all = analyzer._analyze_by_vendor('Total')
    vendor_price = analyzer._analyze_by_vendor('price')
    vendor_freight = analyzer._analyze_by_vendor('freight_value')
    
    # Calculate vendor performance metrics
    total_vendors = len(vendor_all)
    top_vendor = vendor_all.iloc[0] if total_vendors > 0 else None
    
    # Calculate vendor segments
    total_revenue = vendor_all['Total'].sum()
    vendor_all['revenue_pct'] = (vendor_all['Total'] / total_revenue * 100) if total_revenue > 0 else 0
    
    # Segment vendors by revenue contribution
    vendor_all['segment'] = pd.cut(
        vendor_all['revenue_pct'],
        bins=[0, 0.1, 1, 5, 100],
        labels=['Micro (<0.1%)', 'Small (0.1-1%)', 'Medium (1-5%)', 'Large (>5%)']
    )
    
    segment_summary = vendor_all.groupby('segment').agg(
        vendor_count=('seller_id', 'count'),
        total_revenue=('Total', 'sum'),
        avg_revenue=('Total', 'mean')
    ).reset_index()
    
    return {
        'vendor_all': vendor_all,
        'vendor_price': vendor_price,
        'vendor_freight': vendor_freight,
        'segment_summary': segment_summary,
        'total_vendors': total_vendors,
        'total_revenue': total_revenue,
        'top_vendor': top_vendor,
        'analyzer': analyzer
    }

# ======================= HELPER FUNCTIONS =======================

def create_vendor_segmentation_chart(segment_summary):
    """Create pie chart for vendor segmentation"""
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=segment_summary['segment'],
        values=segment_summary['vendor_count'],
        hole=0.4,
        marker_colors=['#2C7D8B', '#2A927A', '#C9D2BA', '#8B4513'],
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>' +
                     'Vendors: %{value:,}<br>' +
                     'Percentage: %{percent}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Vendor Segmentation by Revenue Contribution',
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

def create_vendor_concentration_chart(vendor_all):
    """Create Lorenz curve for vendor concentration"""
    sorted_vendors = vendor_all.sort_values('Total', ascending=False).copy()
    sorted_vendors['cumulative_pct'] = (sorted_vendors['Total'].cumsum() / 
                                       sorted_vendors['Total'].sum() * 100)
    
    # Perfect equality line
    perfect_equality = np.linspace(0, 100, len(sorted_vendors))
    
    fig = go.Figure()
    
    # Lorenz curve
    fig.add_trace(go.Scatter(
        x=list(range(1, len(sorted_vendors) + 1)),
        y=sorted_vendors['cumulative_pct'],
        mode='lines',
        line=dict(color='#2C7D8B', width=3),
        fill='tozeroy',
        fillcolor='rgba(44, 125, 139, 0.2)',
        name='Actual Distribution'
    ))
    
    # Perfect equality line
    fig.add_trace(go.Scatter(
        x=list(range(1, len(sorted_vendors) + 1)),
        y=perfect_equality,
        mode='lines',
        line=dict(color='#C9D2BA', width=2, dash='dash'),
        name='Perfect Equality'
    ))
    
    # Calculate Gini coefficient (approximation)
    lorenz_area = np.trapezoid(sorted_vendors['cumulative_pct'], dx=1)
    perfect_area = np.trapezoid(perfect_equality, dx=1)
    gini_coefficient = (perfect_area - lorenz_area) / perfect_area if perfect_area > 0 else 0
    
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"Gini Coefficient: {gini_coefficient:.3f}",
        showarrow=False,
        font=dict(size=12, color='#333333'),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="#cccccc",
        borderwidth=1,
        borderpad=4
    )
    
    fig.update_layout(
        title={
            'text': 'Vendor Concentration (Lorenz Curve)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title="Vendors (sorted by revenue)",
        yaxis_title="Cumulative Revenue %",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig, gini_coefficient

# ======================= PAGE INITIALIZATION =======================

def initialize_page():
    """Initialize the vendor analysis page"""
    
    # Check if data is loaded
    if not st.session_state.get('data_loaded', False):
        st.error("⚠️ Data not loaded. Please go to the Home page and click 'Load All Data'.")
        st.stop()
    
    if st.session_state.order_items is None or st.session_state.products is None:
        st.error("❌ Required data not available. Please reload data from Home page.")
        st.stop()
    
    # Initialize vendor analysis with caching
    if 'vendor_analysis' not in st.session_state:
        with st.spinner("🏢 Analyzing vendor performance..."):
            results = get_vendor_analysis(
                st.session_state.order_items, 
                st.session_state.products
            )
            st.session_state.vendor_analysis = results
    
    return st.session_state.vendor_analysis

# ======================= MAIN PAGE CONTENT =======================

def main():
    """Main content for Vendor Analysis page"""
    
    # Page header
    st.markdown("""
    <h1 class="main-text">🏢 Vendor Analysis</h1>
    <p class="sub-text">Comprehensive analysis of vendor performance, concentration, and segmentation</p>
    """, unsafe_allow_html=True)
    
    # Quick navigation
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <p style="color: var(--dark-text-secondary); margin: 0;">
            🔍 <b>Related Analysis:</b> 
            <a href="/💰_Revenue_Overview" style="color: var(--dark-text-cool);">Revenue Overview</a> • 
            <a href="/📦_Product_Category_Analysis" style="color: var(--dark-text-cool);">Category Analysis</a> • 
            <a href="/🚚_Freight_Analysis" style="color: var(--dark-text-cool);">Freight Analysis</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize data
    analysis_data = initialize_page()
    
    # ======================= VENDOR OVERVIEW =======================
    
    st.markdown('<h2 class="main-text">📊 Vendor Overview</h2>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Vendors",
            value=f"{analysis_data['total_vendors']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Vendor Revenue",
            value=f"R${analysis_data['total_revenue']:,.0f}",
            delta=None
        )
    
    with col3:
        avg_rev = analysis_data['vendor_all']['Total'].mean()
        st.metric(
            label="Avg Revenue per Vendor",
            value=f"R${avg_rev:,.0f}",
            delta=None
        )
    
    with col4:
        if analysis_data['top_vendor'] is not None:
            top_vendor_id = str(analysis_data['top_vendor']['seller_id'])[:15]
            st.metric(
                label="Top Vendor ID",
                value=top_vendor_id,
                delta=None
            )
    
    # Vendor segmentation metrics
    st.markdown("### 🎯 Vendor Segmentation")
    
    segment_cols = st.columns(len(analysis_data['segment_summary']))
    
    for idx, (col, row) in enumerate(zip(segment_cols, analysis_data['segment_summary'].itertuples())):
        with col:
            segment_pct = (row.total_revenue / analysis_data['total_revenue'] * 100) if analysis_data['total_revenue'] > 0 else 0
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.8rem; color: var(--dark-text-warm); font-weight: 600;">
                    {row.vendor_count:,}
                </div>
                <div style="color: var(--dark-text-primary); font-size: 0.9rem; font-weight: 500;">
                    {row.segment}
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.8rem; margin-top: 0.5rem;">
                    {segment_pct:.1f}% of revenue<br>
                    R${row.avg_revenue:,.0f} avg
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= CONCENTRATION ANALYSIS =======================
    
    st.markdown('<h2 class="main-text">📈 Vendor Concentration Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Vendor segmentation pie chart
        fig_segmentation = create_vendor_segmentation_chart(analysis_data['segment_summary'])
        st.plotly_chart(fig_segmentation, use_container_width=True)
    
    with col2:
        # Lorenz curve for concentration
        fig_concentration, gini_coefficient = create_vendor_concentration_chart(analysis_data['vendor_all'])
        st.plotly_chart(fig_concentration, use_container_width=True)
    
    # Concentration insights
    top_10_pct = (analysis_data['vendor_all'].head(10)['Total'].sum() / 
                 analysis_data['total_revenue'] * 100) if analysis_data['total_revenue'] > 0 else 0
    
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1.5rem; margin: 1rem 0;">
        <h3 class="warm-text" style="margin-top: 0;">📊 Concentration Metrics</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Top 10 Vendors</div>
                <div style="color: var(--dark-text-primary); font-size: 1.5rem; font-weight: 600;">
                    {top_10_pct:.1f}%
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">of total revenue</div>
            </div>
            <div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Gini Coefficient</div>
                <div style="color: var(--dark-text-primary); font-size: 1.5rem; font-weight: 600;">
                    {gini_coefficient:.3f}
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">
                    {('High inequality' if gini_coefficient > 0.5 else 
                      'Moderate inequality' if gini_coefficient > 0.3 else 
                      'Low inequality')}
                </div>
            </div>
            <div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Revenue CV</div>
                <div style="color: var(--dark-text-primary); font-size: 1.5rem; font-weight: 600;">
                    {analysis_data['vendor_all']['Total'].std() / analysis_data['vendor_all']['Total'].mean():.1f}
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">Coefficient of variation</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= INTERACTIVE VENDOR ANALYSIS =======================
    
    st.markdown('<h2 class="main-text">📊 Interactive Vendor Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vendors_to_show = st.slider(
            "Number of Vendors to Display",
            min_value=10,
            max_value=100,
            value=30,
            help="Adjust how many vendors to show in the chart"
        )
    
    with col2:
        chart_height = st.slider(
            "Chart Height",
            min_value=500,
            max_value=1000,
            value=600,
            step=50,
            help="Adjust chart height for better visibility"
        )
    
    with col3:
        revenue_component = st.selectbox(
            "Revenue Component",
            ["Total Revenue", "Product Revenue", "Freight Revenue"],
            help="Select which revenue component to analyze"
        )
    
    # Select appropriate dataset
    if revenue_component == "Total Revenue":
        vendor_data = analysis_data['vendor_all']
        title_suffix = "Total Revenue"
    elif revenue_component == "Product Revenue":
        vendor_data = analysis_data['vendor_price']
        title_suffix = "Product Revenue"
    else:  # Freight Revenue
        vendor_data = analysis_data['vendor_freight']
        title_suffix = "Freight Revenue"
    
    # ======================= MAIN VENDOR CHART =======================
    
    fig_vendors = create_vendor_revenue_chart(
        vendor_data, 
        top_n=vendors_to_show
    )
    
    # Update title and height
    fig_vendors.update_layout(
        height=chart_height,
        title={
            'text': f'Top {vendors_to_show} Vendors by {title_suffix}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        }
    )
    
    st.plotly_chart(fig_vendors, use_container_width=True)
    
    st.markdown("---")
    
    # ======================= VENDOR PERFORMANCE RANKING =======================
    
    with st.expander("🏆 Vendor Performance Ranking", expanded=False):
        st.markdown(f"### 📊 {title_suffix} Ranking")
        
        # Calculate rankings and statistics
        ranked_vendors = vendor_data.copy()
        ranked_vendors['rank'] = range(1, len(ranked_vendors) + 1)
        ranked_vendors['revenue_pct'] = (ranked_vendors['Total'] / ranked_vendors['Total'].sum() * 100)
        ranked_vendors['cumulative_pct'] = ranked_vendors['revenue_pct'].cumsum()
        
        # Add segment information if available
        if 'segment' in ranked_vendors.columns:
            segment_display = ranked_vendors['segment']
        else:
            # Create segments based on revenue percentage
            ranked_vendors['segment'] = pd.cut(
                ranked_vendors['revenue_pct'],
                bins=[0, 0.1, 1, 5, 100],
                labels=['Micro', 'Small', 'Medium', 'Large']
            )
            segment_display = ranked_vendors['segment']
        
        # Format for display
        display_df = pd.DataFrame({
            'Rank': ranked_vendors['rank'].head(vendors_to_show),
            'Vendor ID': ranked_vendors['seller_id'].head(vendors_to_show).astype(str),
            'Segment': segment_display.head(vendors_to_show),
            'Revenue': ranked_vendors['Total'].head(vendors_to_show).apply(lambda x: f"R${x:,.0f}"),
            'Share': ranked_vendors['revenue_pct'].head(vendors_to_show).apply(lambda x: f"{x:.2f}%"),
            'Cumulative': ranked_vendors['cumulative_pct'].head(vendors_to_show).apply(lambda x: f"{x:.1f}%")
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Export option
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Vendor Rankings (CSV)",
            data=csv,
            file_name=f"olist_vendor_rankings_{title_suffix.replace(' ', '_').lower()}.csv",
            mime="text/csv",
            type="secondary"
        )
    
    # ======================= VENDOR HEALTH CHECK =======================
    
    st.markdown("---")
    
    st.markdown('<h2 class="main-text">🏥 Vendor Health Check</h2>', unsafe_allow_html=True)
    
    # Calculate health metrics
    total_vendors = len(analysis_data['vendor_all'])
    active_vendors = total_vendors  # All vendors in dataset are active
    
    # Revenue thresholds
    high_performers = len(analysis_data['vendor_all'][analysis_data['vendor_all']['Total'] > 
                                                      analysis_data['vendor_all']['Total'].quantile(0.75)])
    low_performers = len(analysis_data['vendor_all'][analysis_data['vendor_all']['Total'] < 
                                                     analysis_data['vendor_all']['Total'].quantile(0.25)])
    
    # Dependence risk (top 5 vendors contribute more than 50% of revenue)
    top_5_revenue = analysis_data['vendor_all'].head(5)['Total'].sum()
    dependence_risk = top_5_revenue / analysis_data['total_revenue'] > 0.5 if analysis_data['total_revenue'] > 0 else False
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1rem; text-align: center;">
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">High Performers</div>
            <div style="color: #2A927A; font-size: 1.8rem; font-weight: 600;">
                {high_performers:,}
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">
                Top 25% by revenue
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1rem; text-align: center;">
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Low Performers</div>
            <div style="color: #8B4513; font-size: 1.8rem; font-weight: 600;">
                {low_performers:,}
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">
                Bottom 25% by revenue
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        risk_color = "#8B4513" if dependence_risk else "#2A927A"
        risk_text = "⚠️ High Risk" if dependence_risk else "✅ Low Risk"
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1rem; text-align: center;">
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Dependence Risk</div>
            <div style="color: {risk_color}; font-size: 1.5rem; font-weight: 600;">
                {risk_text}
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">
                Top 5: {(top_5_revenue/analysis_data['total_revenue']*100):.1f}% of revenue
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        median_revenue = analysis_data['vendor_all']['Total'].median()
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1rem; text-align: center;">
            <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Median Revenue</div>
            <div style="color: var(--dark-text-warm); font-size: 1.8rem; font-weight: 600;">
                R${median_revenue:,.0f}
            </div>
            <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">
                Middle performer benchmark
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ======================= RECOMMENDATIONS =======================
    
    st.markdown("---")
    
    st.markdown('<h2 class="main-text">💡 Vendor Management Recommendations</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">🎯 For Top Performers</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Strengthen relationships with key vendors</li>
                <li>Negotiate better terms for mutual growth</li>
                <li>Develop exclusive partnerships</li>
                <li>Monitor for overdependence risks</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">📈 For Growth Opportunities</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Identify and develop mid-tier vendors</li>
                <li>Provide support to low-performing vendors</li>
                <li>Diversify vendor base to reduce risk</li>
                <li>Implement vendor development programs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ======================= PAGE FOOTER =======================
    
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
        <p>
            <b>Vendor Analysis</b> • {:,} vendors analyzed • 
            Total revenue: R${:,.0f} • Gini coefficient: {:.3f}
        </p>
        <p style="margin-top: 0.5rem;">
            Use segmentation and concentration metrics to optimize vendor portfolio and manage risks.
        </p>
    </div>
    """.format(
        analysis_data['total_vendors'],
        analysis_data['total_revenue'],
        gini_coefficient
    ), unsafe_allow_html=True)

# ======================= CUSTOM CSS =======================

st.markdown("""
<style>
/* Custom vendor page styling */
.vendor-segment-micro { color: #2C7D8B; }
.vendor-segment-small { color: #2A927A; }
.vendor-segment-medium { color: #C9D2BA; }
.vendor-segment-large { color: #8B4513; }

/* Enhanced table styling */
div[data-testid="stDataFrame"] table {
    font-size: 0.9rem;
}

div[data-testid="stDataFrame"] th {
    background: rgba(255, 255, 255, 0.1) !important;
    color: var(--dark-text-warm) !important;
}

/* Metric card hover effects */
div[data-testid="stMetric"] {
    transition: all 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()