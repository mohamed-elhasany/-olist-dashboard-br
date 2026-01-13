# Home.py - Main entry point for the Olist Dashboard
import streamlit as st
import pandas as pd

# Import theme
import theme

# Page configuration
st.set_page_config(
    page_title="Olist Dashboard - Revenue & Delivery Insights",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply theme
theme.inject()

# ======================= DATA LOADING FUNCTIONS =======================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_order_items():
    """Load order_items dataset from Google Drive"""
    try:
        order_items_url = "https://drive.google.com/uc?export=download&id=1l-ARGt-ORsoiGG4tBhbUNwkBG0fzaeQk"
        order_items = pd.read_csv(order_items_url)
        return order_items
    except Exception as e:
        st.error(f"❌ Failed to load order_items: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_products():
    """Load products dataset from Google Drive"""
    try:
        products_url = "https://drive.google.com/uc?export=download&id=1hBun8a4j9D81WDxBsaM3R4fc_1GKso8k"
        products = pd.read_csv(products_url)
        return products
    except Exception as e:
        st.error(f"❌ Failed to load products: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_orders():
    """Load orders dataset from Google Drive"""
    try:
        orders_url = "https://drive.google.com/uc?export=download&id=1rTfMh6_TdlT59Ty4Qh93ukkW_qRDjhC0"
        orders = pd.read_csv(orders_url)
        return orders
    except Exception as e:
        st.error(f"❌ Failed to load orders: {str(e)}")
        return None

def initialize_session_state():
    """Initialize session state for data storage"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'order_items' not in st.session_state:
        st.session_state.order_items = None
    if 'products' not in st.session_state:
        st.session_state.products = None
    if 'orders' not in st.session_state:
        st.session_state.orders = None

# ======================= MAIN WELCOME PAGE =======================

def main():
    """Main welcome page with data loading"""
    
    # Initialize session state
    initialize_session_state()
    
    # Custom CSS for transparent containers
    st.markdown("""
    <style>
    /* Remove all white backgrounds from containers */
    .dataframe, div[data-testid="stDataFrame"], 
    div[data-baseweb="card"], .stDataFrame,
    .stDataFrame div, .stDataFrame table {
        background-color: transparent !important;
    }
    
    /* Transparent metric containers */
    div[data-testid="stMetric"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Make all containers transparent */
    .stDataFrame, .stTable, .stAlert,
    div[class*="st-"], div[role="main"] > div > div {
        background-color: transparent !important;
    }
    
    /* Custom transparent info boxes */
    .transparent-info {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .transparent-info:hover {
        border-color: rgba(212, 180, 131, 0.3);
        transform: translateY(-2px);
    }
    
    /* Custom heading style */
    .dashboard-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(45deg, #7fb4ca, #d4b483);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .dashboard-subtitle {
        font-size: 1.2rem;
        color: var(--dark-text-secondary);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Custom stats cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        border-color: rgba(212, 180, 131, 0.3);
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--dark-text-warm);
        margin: 0.5rem 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: var(--dark-text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Custom button style */
    .load-btn {
        background: linear-gradient(45deg, #2c8c6e, #23785d) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 30px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .load-btn:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px rgba(44, 140, 110, 0.3) !important;
    }
    
    /* Feature cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 2rem;
        height: 100%;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        border-color: rgba(212, 180, 131, 0.3);
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--dark-text-warm);
        margin-bottom: 1rem;
    }
    
    .feature-list {
        list-style: none;
        padding-left: 0;
        margin-bottom: 0;
    }
    
    .feature-list li {
        padding: 0.3rem 0;
        color: var(--dark-text-secondary);
    }
    
    .feature-list li:before {
        content: "▸";
        color: var(--dark-text-warm);
        margin-right: 0.5rem;
    }
    
    /* Page tree / Site map styles */
    .page-tree-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .page-tree-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--dark-text-warm);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .page-tree {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .page-item {
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .page-item:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(212, 180, 131, 0.2);
        transform: translateX(5px);
    }
    
    .page-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
        width: 40px;
        text-align: center;
    }
    
    .page-content {
        flex: 1;
    }
    
    .page-number {
        font-size: 0.9rem;
        color: var(--dark-text-cool);
        background: rgba(127, 180, 202, 0.1);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        margin-right: 0.5rem;
        font-weight: 600;
    }
    
    .page-name {
        font-weight: 600;
        color: var(--dark-text-primary);
        margin-bottom: 0.2rem;
    }
    
    .page-desc {
        font-size: 0.85rem;
        color: var(--dark-text-secondary);
        line-height: 1.4;
    }
    
    .page-indicator {
        color: var(--dark-text-cool);
        font-size: 0.9rem;
        opacity: 0.7;
    }
    
    /* Tree connector lines */
    .tree-connector {
        position: relative;
        margin-left: 20px;
    }
    
    .tree-connector:before {
        content: "";
        position: absolute;
        left: -20px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Footer */
    .footer {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        color: var(--dark-text-secondary);
    }
    
    .analyst-info {
        margin-top: 1rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Main insights specific styling */
    .insights-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .insights-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--dark-text-warm);
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .insight-item {
        padding: 1rem;
        margin: 0.5rem 0;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        border-left: 4px solid var(--dark-text-warm);
    }
    
    .insight-header {
        font-weight: 600;
        color: var(--dark-text-primary);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .insight-content {
        color: var(--dark-text-secondary);
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Section
    st.markdown('<h1 class="dashboard-title">🇧🇷 Olist E-Commerce Revenue & Delivery Insights Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="dashboard-subtitle">Analyzing over 100,000 real orders from the Brazilian E-Commerce Dataset</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data Loading Section
    st.markdown('<h2>📁 Data Loading</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("🔄 Load All Data", key="load_data", type="primary", use_container_width=True):
            with st.spinner("Loading order_items..."):
                order_items = load_order_items()
                st.session_state.order_items = order_items
            
            with st.spinner("Loading products..."):
                products = load_products()
                st.session_state.products = products
            
            with st.spinner("Loading orders..."):
                orders = load_orders()
                st.session_state.orders = orders
            
            if all([order_items is not None, products is not None, orders is not None]):
                st.session_state.data_loaded = True
                st.success("🎉 All data loaded successfully! You can now navigate to other pages.")
    
    st.divider()
    
    # Data Status
    if st.session_state.data_loaded:
        st.markdown("### 📊 Data Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{len(st.session_state.order_items):,}</div>
                <div class="stat-label">Order Items</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{len(st.session_state.products):,}</div>
                <div class="stat-label">Products</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{len(st.session_state.orders):,}</div>
                <div class="stat-label">Orders</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick Data Preview
        with st.expander("📋 Quick Data Preview", expanded=False):
            tab1, tab2, tab3 = st.tabs(["Order Items", "Products", "Orders"])
            
            with tab1:
                st.dataframe(st.session_state.order_items.head(5), use_container_width=True)
            
            with tab2:
                st.dataframe(st.session_state.products.head(5), use_container_width=True)
            
            with tab3:
                st.dataframe(st.session_state.orders.head(5), use_container_width=True)
    
    st.markdown("---")
    
    # NEW: Pages Tree / Site Map Section
    st.markdown('<h2>🗺️ Dashboard Navigation Map</h2>', unsafe_allow_html=True)

    
    # Page Tree Container - UPDATED SECTION ONLY
    # ================================================================

    # ----------  Native-St only, same appearance  ----------
    st.markdown("### 📚 Complete Analysis Journey")

    # reusable helper
    def page_row(icon: str, number: int, name: str, desc: str, indicator: str):
        c1, c2, c3 = st.columns([1, 12, 3])
        c1.markdown(f'<span class="page-icon">{icon}</span>', unsafe_allow_html=True)
        c2.markdown(
            f'<div class="page-content">'
            f'<div><span class="page-number">{number}</span>'
            f'<span class="page-name">{name}</span></div>'
            f'<div class="page-desc">{desc}</div></div>',
            unsafe_allow_html=True,
        )
        c3.markdown(f'<span class="page-indicator">{indicator}</span>', unsafe_allow_html=True)

    # ---------- 1 ----------
    with st.container():
        page_row("💡", 1, "Main Insights",
                "Key takeaways, executive summary, and actionable recommendations",
                "→ Start Here")

    # ---------- 2 ----------
    with st.container():
        st.markdown('<div class="tree-connector">', unsafe_allow_html=True)
        page_row("💰", 2, "Revenue Overview",
                "Overall revenue metrics, trends, and top-performing segments",
                "→ Financial Analysis")

    # ---------- 3 ----------
    with st.container():
        st.markdown('<div class="tree-connector">', unsafe_allow_html=True)
        page_row("📦", 3, "Product Category Analysis",
                "Deep dive into product categories, performance, and patterns",
                "→ Product Focus")

    # ---------- 4 ----------
    with st.container():
        st.markdown('<div class="tree-connector">', unsafe_allow_html=True)
        page_row("🏢", 4, "Vendor Analysis",
                "Seller performance, rankings, and vendor-specific insights",
                "→ Seller Performance")

    # ---------- 5 ----------
    with st.container():
        st.markdown('<div class="tree-connector">', unsafe_allow_html=True)
        page_row("🚚", 5, "Freight Analysis",
                "Shipping costs, logistics efficiency, and freight optimization",
                "→ Logistics Focus")

    # ---------- 6 ----------
    with st.container():
        st.markdown('<div class="tree-connector">', unsafe_allow_html=True)
        page_row("⏱️", 6, "Order Timelines",
                "Processing stages, time analysis, and fulfillment efficiency",
                "→ Time Analysis")

    # ---------- 7 ----------
    with st.container():
        st.markdown('<div class="tree-connector">', unsafe_allow_html=True)
        page_row("🚨", 7, "Delay Analysis",
                "Delay patterns, root causes, and late delivery heatmaps",
                "→ Problem Areas")

    # ---------- 8 ----------
    with st.container():
        st.markdown('<div class="tree-connector">', unsafe_allow_html=True)
        page_row("📍", 8, "Geographic Analysis",
                "Regional trends, map visualizations, and location-based insights",
                "→ Spatial Analysis")

    # ---------- 9 ----------
    with st.container():
        st.markdown('<div class="tree-connector">', unsafe_allow_html=True)
        page_row("📊", 9, "Delivery Performance",
                "Overall delivery metrics, success rates, and performance KPIs",
                "→ Final Summary")

    # ================================================================
    # Quick Navigation Tips - Using Streamlit components
    st.markdown("""
    <div class="transparent-info">
        <h3 style="color: var(--dark-text-cool); margin-bottom: 1rem;">💡 Navigation Tips</h3>
        <p style="color: var(--dark-text-secondary); margin-bottom: 1rem;">
            Use the <b>sidebar on the left</b> to navigate between pages. The dashboard is organized in a logical flow:
        </p>
        <ul style="color: var(--dark-text-secondary); padding-left: 1.5rem;">
            <li><b>Start with Main Insights</b> for key takeaways and recommendations</li>
            <li><b>Explore Revenue & Product analysis</b> for financial performance</li>
            <li><b>Dive into Delivery & Logistics</b> for operational efficiency</li>
            <li><b>End with Performance Metrics</b> for overall assessment</li>
        </ul>
        <p style="color: var(--dark-text-secondary); margin-top: 1rem;">
            Each page contains interactive filters, detailed visualizations, and actionable insights.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main Insights Section - FIXED: Using proper Streamlit components
    st.markdown("### 💡 Key Insights Preview")
    
    with st.container():
        # Create a container with custom styling
        st.markdown("""
        <div class="insights-container">
            <div class="insights-title">
                <span>🎯 What You'll Discover</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Insight 1
        st.markdown("""
        <div class="insight-item">
            <div class="insight-header">💰 Revenue Optimization Opportunities</div>
            <div class="insight-content">
                Identify top-performing product categories and sellers that contribute disproportionately to revenue. 
                Discover pricing strategies and freight cost optimizations.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Insight 2
        st.markdown("""
        <div class="insight-item">
            <div class="insight-header">🚚 Delivery Performance Insights</div>
            <div class="insight-content">
                Analyze delivery timelines, identify delay patterns, and understand the impact of processing stages 
                on overall customer experience. Geographic trends reveal regional performance variations.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Insight 3
        st.markdown("""
        <div class="insight-item">
            <div class="insight-header">📦 Product & Category Intelligence</div>
            <div class="insight-content">
                Deep dive into product dimensions, weight impact on shipping costs, and category-wise performance. 
                Discover which products sell best in which regions and seasons.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Insight 4
        st.markdown("""
        <div class="insight-item">
            <div class="insight-header">🏢 Vendor Performance Analysis</div>
            <div class="insight-content">
                Evaluate seller performance metrics, identify top vendors, and discover partnership opportunities. 
                Understand vendor reliability and delivery consistency across different regions.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features Section
    st.markdown("### 🔍 Core Analysis Areas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">💰</span>
            <h3 class="feature-title">Revenue & Product Analysis</h3>
            <ul class="feature-list">
                <li>Financial performance metrics</li>
                <li>Product category profitability</li>
                <li>Top seller identification</li>
                <li>Price optimization opportunities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🚚</span>
            <h3 class="feature-title">Delivery & Logistics</h3>
            <ul class="feature-list">
                <li>Shipping cost analysis</li>
                <li>Delivery time optimization</li>
                <li>Delay pattern identification</li>
                <li>Geographic performance mapping</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Getting Started Section
    st.markdown("### 🚀 Getting Started")
    
    if st.session_state.data_loaded:
        with st.container():
            st.markdown("""
            <div class="transparent-info">
                <h3 style="color: var(--dark-text-cool); margin-bottom: 1rem;">✅ Ready to Explore!</h3>
                <p style="color: var(--dark-text-secondary); margin-bottom: 1rem;">
                    Your data is loaded and ready for analysis. Use the sidebar to navigate to:
                </p>
                <ul style="color: var(--dark-text-secondary); padding-left: 1.5rem;">
                    <li><b>💡 Main Insights</b> - Start with key takeaways and recommendations</li>
                    <li><b>💰 Revenue Overview</b> - Dive into financial performance</li>
                    <li><b>🚚 Delivery Analysis</b> - Explore logistics and timelines</li>
                </ul>
                <p style="color: var(--dark-text-secondary); margin-top: 1rem;">
                    Follow the logical flow or jump directly to your area of interest.
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        with st.container():
            st.markdown("""
            <div class="transparent-info">
                <h3 style="color: var(--dark-text-cool); margin-bottom: 1rem;">📥 First Step: Load Data</h3>
                <p style="color: var(--dark-text-secondary); margin-bottom: 1rem;">
                    To begin your analysis:
                </p>
                <ol style="color: var(--dark-text-secondary); padding-left: 1.5rem;">
                    <li>Click the <b>"Load All Data"</b> button above</li>
                    <li>Wait for all datasets to load (3 CSV files)</li>
                    <li>Use the sidebar or the navigation map to explore pages</li>
                </ol>
                <p style="color: var(--dark-text-secondary); margin-top: 1rem;">
                    The data will be cached for faster access on subsequent visits.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    
    # Analyst Info
    with st.container():
        st.markdown("""
        <div class="footer">
            <div class="analyst-info">
                <h3 style="color: var(--dark-text-warm); margin-bottom: 0.5rem;">👨‍💻 About the Analyst</h3>
                <p style="color: var(--dark-text-secondary); margin-bottom: 0.5rem;">
                    <b>Mohamed Elhasany</b> | General Data Analyst
                </p>
                <p style="color: var(--dark-text-secondary);">
                    📧 <b>Email:</b> elhasanymohamed123@gmail.com<br>
                    🔗 <b>Portfolio:</b> 
                    <a href="https://github.com/mohamed-elhasany" target="_blank" style="color: var(--dark-text-cool); text-decoration: none;">GitHub</a> •
                    <a href="https://khamsat.com/user/elhasany_123" target="_blank" style="color: var(--dark-text-cool); text-decoration: none;">Khamsat</a> •
                    <a href="https://www.freelancer.com/u/mohamede0226" target="_blank" style="color: var(--dark-text-cool); text-decoration: none;">Freelancer</a>
                </p>
            </div>
            <p style="color: var(--dark-text-secondary); margin-top: 1rem; font-size: 0.9rem;">
                Built with ❤️ using Streamlit and Plotly • Dataset: Brazilian E-Commerce Public Dataset by Olist
            </p>
        </div>
        """, unsafe_allow_html=True)
    lang = st.radio("اختر اللغة / Choose language", ("العربية", "English"))

    if lang == "العربية":
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem; margin: 2rem 0 ;direction: rtl; text-align: right;">
            <h4 style="color: var(--dark-text-warm); margin-top: 0;">💡 تعزيز تجربة اللوحة</h4>
            <p style="color: var(--dark-text-secondary); margin: 0.5rem 0;">
                ضع في اعتبارك أن تحديد أهدافك واحتياجاتك بشكل دقيق يجعل هذه اللوحة أكثر فائدة.
            </p>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>توضيح أهداف عملك والمقاييس الأساسية التي تهمك</li>
                <li>تحديد نقاط القرار الرئيسية</li>
                <li>تحديد مؤشرات النجاح والمعايير المستهدفة</li>
                <li>توضيح نقاط الألم</li>
                <li>تحديد خطوات واضحة بناءً على التحليلات</li>
            </ul>
            <p style="color: var(--dark-text-secondary); margin: 0.5rem 0 0 0;">
                كلما كانت احتياجاتك أكثر تحديدًا، كلما أصبحت هذه اللوحة أكثر قيمة وقابلة للاستخدام.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem; margin: 2rem 0;">
            <h4 style="color: var(--dark-text-warm); margin-top: 0;">💡 Dashboard Enhancement</h4>
            <p style="color: var(--dark-text-secondary); margin: 0.5rem 0;">
                keep in mind that specifying your goals and needs will make this dashboard more valuable.
            </p>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Clarify your business goals and key metrics that matter most</li>
                <li>Identify critical decision points</li>
                <li>Define success indicators and target benchmarks</li>
                <li>Map all pain points</li>
                <li>Establish clear actions from insights</li>
            </ul>
            <p style="color: var(--dark-text-secondary); margin: 0.5rem 0 0 0;">
                The more specific your needs are, the more meaningful and actionable this dashboard becomes.
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Call main() function directly instead of checking session_state
    main()