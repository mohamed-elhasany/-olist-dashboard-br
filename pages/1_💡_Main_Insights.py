# pages/1_💡_Main_Insights.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Main Insights | Olist Dashboard",
    page_icon="💡",
    layout="wide"
)

# Apply theme
try:
    import theme
    theme.inject()
except:
    st.warning("Theme module not found. Using default styling.")

# ======================= DATA LOADING & CACHING =======================

@st.cache_data(ttl=3600)
def compute_main_insights():
    """Compute comprehensive insights from all available data"""
    
    # Get data from session state
    if not st.session_state.get('data_loaded', False):
        return None
    
    insights = {}
    
    # Get data
    orders = st.session_state.get('orders')
    order_items = st.session_state.get('order_items')
    products = st.session_state.get('products')
    
    if orders is None or order_items is None:
        return None
    
    # ========== REVENUE INSIGHTS ==========
    if order_items is not None:
        try:
            # Total revenue
            if 'price' in order_items.columns and 'freight_value' in order_items.columns:
                order_items['total_revenue'] = order_items['price'] + order_items['freight_value']
                insights['total_revenue'] = order_items['total_revenue'].sum()
                
                # Average order value
                order_totals = order_items.groupby('order_id')['total_revenue'].sum()
                insights['avg_order_value'] = order_totals.mean()
                insights['total_orders'] = len(order_totals)
                insights['total_items_sold'] = len(order_items)
                insights['avg_items_per_order'] = insights['total_items_sold'] / insights['total_orders']
            
            # Revenue trend
            if 'order_purchase_timestamp' in orders.columns and 'order_id' in order_items.columns:
                # Merge to get purchase dates for revenue items
                merged = order_items.merge(
                    orders[['order_id', 'order_purchase_timestamp']], 
                    on='order_id', 
                    how='left'
                )
                merged['purchase_date'] = pd.to_datetime(merged['order_purchase_timestamp']).dt.date
                
                if 'total_revenue' in merged.columns:
                    daily_revenue = merged.groupby('purchase_date')['total_revenue'].sum().reset_index()
                    daily_revenue = daily_revenue.sort_values('purchase_date')
                    insights['revenue_trend'] = daily_revenue
                    
                    # Calculate month-over-month growth
                    if len(daily_revenue) > 30:
                        daily_revenue['month'] = pd.to_datetime(daily_revenue['purchase_date']).dt.to_period('M')
                        monthly_revenue = daily_revenue.groupby('month')['total_revenue'].sum()
                        if len(monthly_revenue) > 1:
                            revenue_growth = ((monthly_revenue.iloc[-1] - monthly_revenue.iloc[-2]) / monthly_revenue.iloc[-2] * 100)
                            insights['revenue_growth_rate'] = revenue_growth
                
        except Exception as e:
            st.warning(f"Revenue insights calculation failed: {str(e)}")
    
    # ========== DELIVERY INSIGHTS ==========
    if orders is not None:
        try:
            # Delivery status
            if 'order_status' in orders.columns:
                delivery_status = orders['order_status'].value_counts()
                insights['delivery_status'] = delivery_status
                insights['delivered_count'] = delivery_status.get('delivered', 0)
                insights['delivery_rate'] = (insights['delivered_count'] / len(orders)) * 100
            
            # Delay analysis
            if 'order_delivered_customer_date' in orders.columns and 'order_estimated_delivery_date' in orders.columns:
                orders_clean = orders.copy()
                for col in ['order_delivered_customer_date', 'order_estimated_delivery_date']:
                    if orders_clean[col].dtype == 'object':
                        orders_clean[col] = pd.to_datetime(orders_clean[col], errors='coerce')
                
                orders_clean['delay'] = orders_clean['order_estimated_delivery_date'] - orders_clean['order_delivered_customer_date']
                
                # Convert to days for analysis
                orders_clean['delay_days'] = orders_clean['delay'].dt.total_seconds() / (24 * 3600)
                
                delivered_orders = orders_clean[orders_clean['order_status'] == 'delivered']
                if len(delivered_orders) > 0:
                    delayed_orders = delivered_orders[delivered_orders['delay_days'] < 0]
                    insights['delayed_count'] = len(delayed_orders)
                    insights['delay_rate'] = (len(delayed_orders) / len(delivered_orders)) * 100
                    insights['avg_delay_days'] = abs(delayed_orders['delay_days'].mean()) if len(delayed_orders) > 0 else 0
                    insights['on_time_rate'] = 100 - insights['delay_rate']
                
        except Exception as e:
            st.warning(f"Delivery insights calculation failed: {str(e)}")
    
    # ========== GEOGRAPHIC INSIGHTS ==========
    if orders is not None and 'customer_state' in orders.columns:
        try:
            # Top states by orders
            state_orders = orders['customer_state'].value_counts().head(5)
            insights['top_states'] = state_orders
            
            # Regional concentration
            total_orders = len(orders)
            top_3_states = state_orders.head(3).sum()
            insights['top_3_concentration'] = (top_3_states / total_orders) * 100
            
        except Exception as e:
            st.warning(f"Geographic insights calculation failed: {str(e)}")
    
    # ========== PRODUCT CATEGORY INSIGHTS ==========
    if order_items is not None and products is not None:
        try:
            # Merge to get category information
            merged_items = order_items.merge(
                products[['product_id', 'product_category_name']], 
                on='product_id', 
                how='left'
            )
            merged_items['product_category_name'] = merged_items['product_category_name'].fillna('Unknown')
            
            # Top categories by revenue
            if 'total_revenue' in merged_items.columns:
                top_categories = merged_items.groupby('product_category_name')['total_revenue'].sum().nlargest(5)
                insights['top_categories_revenue'] = top_categories
            
            # Top categories by volume
            top_categories_volume = merged_items['product_category_name'].value_counts().head(5)
            insights['top_categories_volume'] = top_categories_volume
            
        except Exception as e:
            st.warning(f"Product category insights calculation failed: {str(e)}")
    
    # ========== VENDOR INSIGHTS ==========
    if order_items is not None and 'seller_id' in order_items.columns:
        try:
            # Top vendors by revenue
            if 'total_revenue' in order_items.columns:
                top_vendors = order_items.groupby('seller_id')['total_revenue'].sum().nlargest(5)
                insights['top_vendors'] = top_vendors
            
            # Vendor concentration
            total_vendors = order_items['seller_id'].nunique()
            insights['total_vendors'] = total_vendors
            
            # Top 10% vendor share
            vendor_revenue = order_items.groupby('seller_id')['total_revenue'].sum()
            top_10_percent = int(len(vendor_revenue) * 0.1)
            top_vendors_revenue = vendor_revenue.nlargest(top_10_percent).sum()
            insights['top_vendor_concentration'] = (top_vendors_revenue / insights['total_revenue']) * 100
            
        except Exception as e:
            st.warning(f"Vendor insights calculation failed: {str(e)}")
    
    # ========== FREIGHT INSIGHTS ==========
    if order_items is not None and 'freight_value' in order_items.columns and 'price' in order_items.columns:
        try:
            insights['total_freight'] = order_items['freight_value'].sum()
            insights['avg_freight_per_item'] = order_items['freight_value'].mean()
            insights['freight_to_price_ratio'] = (insights['total_freight'] / order_items['price'].sum()) * 100
            
        except Exception as e:
            st.warning(f"Freight insights calculation failed: {str(e)}")
    
    return insights

# ======================= VISUALIZATION FUNCTIONS =======================

def create_kpi_cards(insights):
    """Create KPI cards for top metrics"""
    
    if insights is None:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total Revenue
        revenue = insights.get('total_revenue', 0)
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem; text-align: center;">
            <div style="font-size: 0.9rem; color: var(--dark-text-secondary); margin-bottom: 0.5rem;">
                📈 Total Revenue
            </div>
            <div style="font-size: 1.8rem; color: #2A927A; font-weight: 600;">
                R${revenue:,.0f}
            </div>
            <div style="font-size: 0.8rem; color: var(--dark-text-secondary); margin-top: 0.5rem;">
                {insights.get('total_orders', 0):,} orders
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Delivery Rate
        delivery_rate = insights.get('delivery_rate', 0)
        delivery_color = "#2A927A" if delivery_rate >= 95 else "#C9D2BA" if delivery_rate >= 90 else "#8B4513"
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid {delivery_color}; 
                    border-radius: 8px; padding: 1.5rem; text-align: center;">
            <div style="font-size: 0.9rem; color: var(--dark-text-secondary); margin-bottom: 0.5rem;">
                📦 Delivery Rate
            </div>
            <div style="font-size: 1.8rem; color: {delivery_color}; font-weight: 600;">
                {delivery_rate:.1f}%
            </div>
            <div style="font-size: 0.8rem; color: var(--dark-text-secondary); margin-top: 0.5rem;">
                {insights.get('delivered_count', 0):,} delivered
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # On-Time Rate
        on_time_rate = insights.get('on_time_rate', 0)
        on_time_color = "#2A927A" if on_time_rate >= 85 else "#C9D2BA" if on_time_rate >= 75 else "#8B4513"
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid {on_time_color}; 
                    border-radius: 8px; padding: 1.5rem; text-align: center;">
            <div style="font-size: 0.9rem; color: var(--dark-text-secondary); margin-bottom: 0.5rem;">
                ⏱️ On-Time Delivery
            </div>
            <div style="font-size: 1.8rem; color: {on_time_color}; font-weight: 600;">
                {on_time_rate:.1f}%
            </div>
            <div style="font-size: 0.8rem; color: var(--dark-text-secondary); margin-top: 0.5rem;">
                Avg delay: {insights.get('avg_delay_days', 0):.1f} days
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Avg Order Value
        avg_order_value = insights.get('avg_order_value', 0)
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem; text-align: center;">
            <div style="font-size: 0.9rem; color: var(--dark-text-secondary); margin-bottom: 0.5rem;">
                💰 Avg Order Value
            </div>
            <div style="font-size: 1.8rem; color: #2C7D8B; font-weight: 600;">
                R${avg_order_value:.2f}
            </div>
            <div style="font-size: 0.8rem; color: var(--dark-text-secondary); margin-top: 0.5rem;">
                {insights.get('avg_items_per_order', 0):.1f} items/order
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_revenue_trend_chart(insights):
    """Create revenue trend chart"""
    
    if 'revenue_trend' not in insights:
        return None
    
    df = insights['revenue_trend'].copy()
    df['purchase_date'] = pd.to_datetime(df['purchase_date'])
    
    # Calculate 7-day moving average
    df['revenue_7d_avg'] = df['total_revenue'].rolling(window=7, min_periods=1).mean()
    
    fig = go.Figure()
    
    # Actual revenue (bars)
    fig.add_trace(go.Bar(
        x=df['purchase_date'],
        y=df['total_revenue'],
        name='Daily Revenue',
        marker_color='rgba(44, 125, 139, 0.3)',
        hovertemplate='Date: %{x|%Y-%m-%d}<br>Revenue: R$%{y:,.0f}<extra></extra>'
    ))
    
    # 7-day moving average (line)
    fig.add_trace(go.Scatter(
        x=df['purchase_date'],
        y=df['revenue_7d_avg'],
        name='7-Day Avg',
        line=dict(color='#2C7D8B', width=3),
        hovertemplate='Date: %{x|%Y-%m-%d}<br>7-Day Avg: R$%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Revenue Trend (7-Day Moving Average)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Date',
        yaxis_title='Revenue (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(tickformat=',.0f')
    )
    
    return fig

def create_top_categories_chart(insights):
    """Create chart for top product categories"""
    
    if 'top_categories_revenue' not in insights:
        return None
    
    top_cats = insights['top_categories_revenue'].reset_index()
    top_cats.columns = ['category', 'revenue']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_cats['category'],
        x=top_cats['revenue'],
        orientation='h',
        marker_color='#2A927A',
        text=[f'R${x:,.0f}' for x in top_cats['revenue']],
        textposition='auto',
        textfont=dict(color='white', size=11),
        hovertemplate='<b>%{y}</b><br>Revenue: R$%{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Top 5 Product Categories by Revenue',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Revenue (R$)',
        yaxis_title='Product Category',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=350,
        margin=dict(l=150, r=50, t=80, b=50),
        yaxis=dict(
            categoryorder='total ascending',
            tickfont=dict(size=11)
        ),
        xaxis=dict(tickformat=',.0f')
    )
    
    return fig

def create_top_states_chart(insights):
    """Create chart for top states"""
    
    if 'top_states' not in insights:
        return None
    
    top_states = insights['top_states'].reset_index()
    top_states.columns = ['state', 'orders']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_states['state'],
        x=top_states['orders'],
        orientation='h',
        marker_color='#C9D2BA',
        text=[f'{x:,}' for x in top_states['orders']],
        textposition='auto',
        textfont=dict(color='#333333', size=11),
        hovertemplate='<b>State %{y}</b><br>Orders: %{x:,}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Top 5 States by Order Volume',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Number of Orders',
        yaxis_title='State',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=300,
        margin=dict(l=80, r=50, t=80, b=50),
        yaxis=dict(
            categoryorder='total ascending',
            tickfont=dict(size=11)
        ),
        xaxis=dict(tickformat=',.0f')
    )
    
    return fig

def create_delivery_performance_gauge(insights):
    """Create gauge chart for delivery performance"""
    
    delivery_rate = insights.get('delivery_rate', 0)
    on_time_rate = insights.get('on_time_rate', 0)
    
    # Overall performance score (weighted average)
    performance_score = (delivery_rate * 0.6 + on_time_rate * 0.4)
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=performance_score,
        title={'text': "Overall Performance Score", 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#333333"},
            'bar': {'color': "#2A927A"},
            'steps': [
                {'range': [0, 70], 'color': "#8B4513"},
                {'range': [70, 85], 'color': "#C9D2BA"},
                {'range': [85, 100], 'color': "#2A927A"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        },
        number={'font': {'size': 40}, 'suffix': '%'}
    ))
    
    fig.update_layout(
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    return fig

# ======================= PAGE CONTENT =======================

def main():
    """Main content for Main Insights page"""
    
    # Page header
    st.markdown("""
    <h1 class="main-text">💡 Main Insights Dashboard</h1>
    <p class="sub-text">Executive summary of key metrics, trends, and performance indicators</p>
    """, unsafe_allow_html=True)
    
    # Quick navigation
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <p style="color: var(--dark-text-secondary); margin: 0;">
            🔍 <b>Detailed Analysis:</b> 
            <a href="/💰_Revenue_Overview" style="color: var(--dark-text-cool);">Revenue</a> • 
            <a href="/📦_Product_Category_Analysis" style="color: var(--dark-text-cool);">Products</a> • 
            <a href="/📊_Delivery_Performance" style="color: var(--dark-text-cool);">Delivery</a> • 
            <a href="/📍_Geographic_Analysis" style="color: var(--dark-text-cool);">Geography</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Check if data is loaded
    if not st.session_state.get('data_loaded', False):
        st.error("⚠️ Data not loaded. Please go to the Home page and click 'Load All Data'.")
        return
    
    # Load insights
    with st.spinner("💡 Loading insights..."):
        insights = compute_main_insights()
    
    if insights is None:
        st.error("❌ Failed to compute insights. Please check your data.")
        return
    
    # ======================= EXECUTIVE SUMMARY =======================
    
    st.markdown('<h2 class="main-text">📊 Executive Summary</h2>', unsafe_allow_html=True)
    
    # KPI Cards
    create_kpi_cards(insights)
    
    st.markdown("---")
    
    # ======================= REVENUE & PERFORMANCE =======================
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Revenue Trend
        fig_revenue = create_revenue_trend_chart(insights)
        if fig_revenue:
            st.plotly_chart(fig_revenue, use_container_width=True)
        else:
            st.info("Revenue trend data not available.")
    
    with col2:
        # Performance Gauge
        fig_gauge = create_delivery_performance_gauge(insights)
        if fig_gauge:
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Quick stats
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1rem; margin-top: 1rem;">
            <h4 class="warm-text" style="margin-top: 0;">📈 Quick Stats</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                <div style="color: var(--dark-text-secondary);">Total Orders</div>
                <div style="text-align: right; color: var(--dark-text-primary);">
                    {:,}
                </div>
                <div style="color: var(--dark-text-secondary);">Items Sold</div>
                <div style="text-align: right; color: var(--dark-text-primary);">
                    {:,}
                </div>
                <div style="color: var(--dark-text-secondary);">Total Vendors</div>
                <div style="text-align: right; color: var(--dark-text-primary);">
                    {:,}
                </div>
                <div style="color: var(--dark-text-secondary);">Freight Ratio</div>
                <div style="text-align: right; color: var(--dark-text-primary);">
                    {:.1f}%
                </div>
            </div>
        </div>
        """.format(
            insights.get('total_orders', 0),
            insights.get('total_items_sold', 0),
            insights.get('total_vendors', 0),
            insights.get('freight_to_price_ratio', 0)
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= TOP PERFORMERS =======================
    
    st.markdown('<h2 class="main-text">🏆 Top Performers</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Categories
        fig_categories = create_top_categories_chart(insights)
        if fig_categories:
            st.plotly_chart(fig_categories, use_container_width=True)
        else:
            st.info("Product category data not available.")
    
    with col2:
        # Top States
        fig_states = create_top_states_chart(insights)
        if fig_states:
            st.plotly_chart(fig_states, use_container_width=True)
        else:
            st.info("State data not available.")
        
        # Top vendors if available
        if 'top_vendors' in insights and len(insights['top_vendors']) > 0:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                <h4 class="warm-text" style="margin-top: 0;">🏢 Top Vendors</h4>
                <div style="max-height: 200px; overflow-y: auto;">
            """, unsafe_allow_html=True)
            
            for i, (vendor_id, revenue) in enumerate(insights['top_vendors'].head(5).items(), 1):
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; 
                            border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                    <div style="color: var(--dark-text-secondary);">
                        #{i} {vendor_id[:8]}...
                    </div>
                    <div style="color: var(--dark-text-primary); font-weight: 500;">
                        R${revenue:,.0f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= KEY INSIGHTS & RECOMMENDATIONS =======================
    
    st.markdown('<h2 class="main-text">💡 Key Insights & Recommendations</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Strengths
        st.markdown("""
        <div style="background: rgba(42, 146, 122, 0.1); border: 1px solid rgba(42, 146, 122, 0.3); 
                    border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem;">
            <h4 class="warm-text" style="margin-top: 0; color: #2A927A;">✅ Strengths</h4>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li><b>High Delivery Rate:</b> {:.1f}% of orders successfully delivered</li>
                <li><b>Strong Revenue Generation:</b> R${:,.0f} total revenue</li>
                <li><b>Diverse Product Portfolio:</b> Multiple high-performing categories</li>
                <li><b>Geographic Reach:</b> Orders distributed across {} states</li>
            </ul>
        </div>
        """.format(
            insights.get('delivery_rate', 0),
            insights.get('total_revenue', 0),
            insights.get('top_states', pd.Series()).size if 'top_states' in insights else 0
        ), unsafe_allow_html=True)
        
        # Growth Opportunities
        st.markdown("""
        <div style="background: rgba(44, 125, 139, 0.1); border: 1px solid rgba(44, 125, 139, 0.3); 
                    border-radius: 8px; padding: 1.5rem;">
            <h4 class="warm-text" style="margin-top: 0; color: #2C7D8B;">📈 Growth Opportunities</h4>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Increase average order value from R${:.2f}</li>
                <li>Expand to underperforming geographic regions</li>
                <li>Develop new product categories based on market trends</li>
                <li>Optimize freight costs (currently {:.1f}% of product value)</li>
            </ul>
        </div>
        """.format(
            insights.get('avg_order_value', 0),
            insights.get('freight_to_price_ratio', 0)
        ), unsafe_allow_html=True)
    
    with col2:
        # Areas for Improvement
        st.markdown("""
        <div style="background: rgba(139, 69, 19, 0.1); border: 1px solid rgba(139, 69, 19, 0.3); 
                    border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem;">
            <h4 class="warm-text" style="margin-top: 0; color: #8B4513;">⚠️ Areas for Improvement</h4>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li><b>Delivery Timeliness:</b> {:.1f}% on-time rate needs improvement</li>
                <li><b>Delay Management:</b> Average delay of {:.1f} days for late deliveries</li>
                <li><b>Market Concentration:</b> Top 3 states account for {:.1f}% of orders</li>
                <li><b>Order Volume:</b> Only {:.1f} items per order on average</li>
            </ul>
        </div>
        """.format(
            insights.get('on_time_rate', 0),
            insights.get('avg_delay_days', 0),
            insights.get('top_3_concentration', 0),
            insights.get('avg_items_per_order', 0)
        ), unsafe_allow_html=True)
        
        # Immediate Actions
        st.markdown("""
        <div style="background: rgba(212, 180, 131, 0.1); border: 1px solid rgba(212, 180, 131, 0.3); 
                    border-radius: 8px; padding: 1.5rem;">
            <h4 class="warm-text" style="margin-top: 0; color: #D4B483;">🎯 Immediate Actions</h4>
            <ol style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Address delivery delays in key regions</li>
                <li>Review and optimize logistics partnerships</li>
                <li>Implement upselling strategies to increase AOV</li>
                <li>Analyze and reduce freight costs</li>
                <li>Expand vendor base to reduce concentration risk</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= DATA SUMMARY =======================
    
    with st.expander("📋 Data Summary", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem;">
                <h4 class="warm-text" style="margin-top: 0;">📊 Performance Metrics</h4>
                <div style="display: grid; grid-template-columns: 1fr; gap: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">Delivery Rate:</span>
                        <span style="color: var(--dark-text-primary);">{:.1f}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">On-Time Rate:</span>
                        <span style="color: var(--dark-text-primary);">{:.1f}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">Delay Rate:</span>
                        <span style="color: var(--dark-text-primary);">{:.1f}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">Avg Order Value:</span>
                        <span style="color: var(--dark-text-primary);">R${:.2f}</span>
                    </div>
                </div>
            </div>
            """.format(
                insights.get('delivery_rate', 0),
                insights.get('on_time_rate', 0),
                insights.get('delay_rate', 0),
                insights.get('avg_order_value', 0)
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem;">
                <h4 class="warm-text" style="margin-top: 0;">💰 Financial Summary</h4>
                <div style="display: grid; grid-template-columns: 1fr; gap: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">Total Revenue:</span>
                        <span style="color: var(--dark-text-primary);">R${:,.0f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">Total Freight:</span>
                        <span style="color: var(--dark-text-primary);">R${:,.0f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">Avg Freight/Item:</span>
                        <span style="color: var(--dark-text-primary);">R${:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">Freight Ratio:</span>
                        <span style="color: var(--dark-text-primary);">{:.1f}%</span>
                    </div>
                </div>
            </div>
            """.format(
                insights.get('total_revenue', 0),
                insights.get('total_freight', 0),
                insights.get('avg_freight_per_item', 0),
                insights.get('freight_to_price_ratio', 0)
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem;">
                <h4 class="warm-text" style="margin-top: 0;">📦 Operational Stats</h4>
                <div style="display: grid; grid-template-columns: 1fr; gap: 0.5rem;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">Total Orders:</span>
                        <span style="color: var(--dark-text-primary);">{:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">Items Sold:</span>
                        <span style="color: var(--dark-text-primary);">{:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">Avg Items/Order:</span>
                        <span style="color: var(--dark-text-primary);">{:.1f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--dark-text-secondary);">Total Vendors:</span>
                        <span style="color: var(--dark-text-primary);">{:,}</span>
                    </div>
                </div>
            </div>
            """.format(
                insights.get('total_orders', 0),
                insights.get('total_items_sold', 0),
                insights.get('avg_items_per_order', 0),
                insights.get('total_vendors', 0)
            ), unsafe_allow_html=True)
    
    # ======================= PAGE FOOTER =======================
    
    st.markdown("---")
    
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
        <p>
            <b>Main Insights Dashboard</b> • Last Updated: {last_updated} • 
            Data Source: Olist E-commerce Dataset • 
            <a href="/🏠_Home" style="color: var(--dark-text-cool);">Return to Home</a>
        </p>
        <p style="margin-top: 0.5rem;">
            Use this dashboard for executive overview. Click on specific metrics for detailed analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ======================= CUSTOM CSS =======================

st.markdown("""
<style>
/* Main Insights specific styling */
.insight-card {
    transition: all 0.3s ease;
    animation: fadeInUp 0.5s ease-out;
}

.insight-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

/* KPI card animations */
@keyframes pulseKPI {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

.kpi-card {
    animation: pulseKPI 3s ease-in-out infinite;
}

/* Performance indicator colors */
.perf-excellent { color: #2A927A; }
.perf-good { color: #C9D2BA; }
.perf-fair { color: #D4B483; }
.perf-poor { color: #8B4513; }

/* Insight category styling */
.insight-strength {
    border-left: 4px solid #2A927A;
    padding-left: 12px;
}

.insight-opportunity {
    border-left: 4px solid #2C7D8B;
    padding-left: 12px;
}

.insight-improvement {
    border-left: 4px solid #8B4513;
    padding-left: 12px;
}

.insight-action {
    border-left: 4px solid #D4B483;
    padding-left: 12px;
}

/* Dashboard grid enhancements */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

/* Chart container optimizations */
.chart-container {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 1rem;
    transition: all 0.3s ease;
}

.chart-container:hover {
    border-color: rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.05);
}

/* Summary stat boxes */
.summary-stat {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    margin: 0.25rem 0;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 4px;
    transition: all 0.2s ease;
}

.summary-stat:hover {
    background: rgba(255, 255, 255, 0.05);
    transform: translateX(5px);
}

.summary-stat-label {
    color: var(--dark-text-secondary);
    font-size: 0.9rem;
}

.summary-stat-value {
    color: var(--dark-text-primary);
    font-weight: 500;
    font-size: 1rem;
}

/* Trend indicators */
.trend-up {
    color: #2A927A;
    font-weight: 500;
}

.trend-down {
    color: #8B4513;
    font-weight: 500;
}

.trend-neutral {
    color: var(--dark-text-secondary);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
    
    .insight-card {
        margin-bottom: 1rem;
    }
}

/* Loading animation for insights */
@keyframes loadingPulse {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
}

.loading-insights {
    animation: loadingPulse 1.5s ease-in-out infinite;
}

/* Export button styling */
.export-btn {
    background: linear-gradient(135deg, #2C7D8B 0%, #2A927A 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.export-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(44, 125, 139, 0.4) !important;
}

/* Print optimization */
@media print {
    .stPlotlyChart {
        page-break-inside: avoid;
    }
    
    .insight-card {
        border: 1px solid #ccc !important;
        box-shadow: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()