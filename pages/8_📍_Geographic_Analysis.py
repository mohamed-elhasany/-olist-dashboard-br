# pages/8_📍_Geographic_Analysis.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Geographic Analysis | Olist Dashboard",
    page_icon="📍",
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
def get_geographic_analysis(orders_data):
    """Cached geographic analysis - optimized for this page only"""
    
    # Create a copy to avoid modifying original
    geo_data = orders_data.copy()
    
    # Check if we have geographic data
    has_state_data = 'customer_state' in geo_data.columns
    
    if has_state_data:
        # Calculate state-level statistics
        state_stats = geo_data.groupby('customer_state').agg(
            total_orders=('order_id', 'nunique'),
            delivered_orders=('Net_State', lambda x: (x == 'Delivered').sum()),
            delayed_orders=('Delay', lambda x: (x < pd.Timedelta(0)).sum() if hasattr(x, 'dtype') and x.dtype != 'object' else 0)
        ).reset_index()
        
        # Calculate percentages
        state_stats['delivery_rate'] = (state_stats['delivered_orders'] / state_stats['total_orders'] * 100).fillna(0)
        state_stats['delay_rate'] = (state_stats['delayed_orders'] / state_stats['total_orders'] * 100).fillna(0)
        
        # Add state names for better display
        brazil_state_names = {
            'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
            'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
            'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
            'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
            'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
            'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
            'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
        }
        
        state_stats['state_name'] = state_stats['customer_state'].map(brazil_state_names)
        
        # Calculate regional metrics
        total_orders_national = state_stats['total_orders'].sum()
        state_stats['national_share'] = (state_stats['total_orders'] / total_orders_national * 100).fillna(0)
        
        # Segment states by order volume
        state_stats['volume_segment'] = pd.cut(
            state_stats['total_orders'],
            bins=[0, 100, 500, 2000, float('inf')],
            labels=['Very Low', 'Low', 'Medium', 'High'],
            include_lowest=True
        )
        
        # Calculate concentration metrics
        sorted_share = state_stats['national_share'].sort_values(ascending=False).reset_index(drop=True)
        top_3_share = sorted_share.head(3).sum()
        top_5_share = sorted_share.head(5).sum()
        
        concentration_stats = {
            'top_3_states_share': top_3_share,
            'top_5_states_share': top_5_share,
            'total_states': len(state_stats),
            'states_with_orders': len(state_stats[state_stats['total_orders'] > 0]),
            'national_total_orders': total_orders_national
        }
    else:
        state_stats = pd.DataFrame()
        concentration_stats = {
            'top_3_states_share': 0,
            'top_5_states_share': 0,
            'total_states': 0,
            'states_with_orders': 0,
            'national_total_orders': 0
        }
    
    return {
        'geo_data': geo_data,
        'state_stats': state_stats,
        'concentration_stats': concentration_stats,
        'has_state_data': has_state_data,
        'orders_data': geo_data
    }

# ======================= HELPER FUNCTIONS =======================

def create_state_orders_chart(state_stats, metric='total_orders', top_n=15):
    """Create horizontal bar chart for state orders"""
    
    if state_stats.empty or metric not in state_stats.columns:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'No State Data Available',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400
        )
        return fig
    
    # Sort and get top N states
    sorted_stats = state_stats.sort_values(metric, ascending=False).head(top_n)
    
    # Metric labels for display
    metric_labels = {
        'total_orders': 'Total Orders',
        'delivery_rate': 'Delivery Rate (%)',
        'delay_rate': 'Delay Rate (%)',
        'national_share': 'National Share (%)'
    }
    
    # Format values based on metric type
    if metric in ['delivery_rate', 'delay_rate', 'national_share']:
        values = sorted_stats[metric]
        text_values = [f'{v:.1f}%' for v in values]
    else:
        values = sorted_stats[metric]
        text_values = [f'{v:,.0f}' for v in values]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=values,
        y=sorted_stats['customer_state'],
        orientation='h',
        marker_color='#2C7D8B',
        text=text_values,
        textposition='auto',
        textfont=dict(color='white', size=11),
        hovertemplate='<b>%{y}</b><br>' +
                     f'{metric_labels.get(metric, metric)}: %{{x:,.0f}}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Top {top_n} States by {metric_labels.get(metric, metric)}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title=metric_labels.get(metric, metric),
        yaxis_title='State',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=400 + (top_n * 20),
        margin=dict(l=100, r=50, t=80, b=50),
        yaxis=dict(
            categoryorder='total ascending',
            tickfont=dict(size=11)
        )
    )
    
    return fig

def create_brazil_map_chart(state_stats, metric='total_orders'):
    """Create choropleth map of Brazil states"""
    
    if state_stats.empty:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'No Geographic Data Available',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=500
        )
        return fig
    
    # Brazil state coordinates (approximate centroids)
    brazil_state_coords = {
        'AC': {'lat': -9.0238, 'lon': -70.8120},
        'AL': {'lat': -9.5713, 'lon': -36.7819},
        'AP': {'lat': 0.9020, 'lon': -51.8544},
        'AM': {'lat': -3.4168, 'lon': -65.8561},
        'BA': {'lat': -12.5797, 'lon': -41.7007},
        'CE': {'lat': -5.4984, 'lon': -39.3206},
        'DF': {'lat': -15.7801, 'lon': -47.9292},
        'ES': {'lat': -19.1834, 'lon': -40.3089},
        'GO': {'lat': -15.8270, 'lon': -49.8362},
        'MA': {'lat': -5.4026, 'lon': -45.1116},
        'MT': {'lat': -12.6819, 'lon': -56.9211},
        'MS': {'lat': -20.7722, 'lon': -54.7852},
        'MG': {'lat': -18.5122, 'lon': -44.5550},
        'PA': {'lat': -3.4168, 'lon': -52.0030},
        'PB': {'lat': -7.2400, 'lon': -36.7820},
        'PR': {'lat': -24.7953, 'lon': -51.7955},
        'PE': {'lat': -8.8137, 'lon': -36.9541},
        'PI': {'lat': -6.6000, 'lon': -42.2800},
        'RJ': {'lat': -22.9068, 'lon': -43.1729},
        'RN': {'lat': -5.7945, 'lon': -36.5172},
        'RS': {'lat': -30.0346, 'lon': -51.2177},
        'RO': {'lat': -11.5057, 'lon': -63.5806},
        'RR': {'lat': 2.7376, 'lon': -62.0751},
        'SC': {'lat': -27.5954, 'lon': -48.5480},
        'SP': {'lat': -23.5505, 'lon': -46.6333},
        'SE': {'lat': -10.5741, 'lon': -37.3857},
        'TO': {'lat': -10.1753, 'lon': -48.2982}
    }
    
    # Add coordinates to state stats
    map_data = state_stats.copy()
    map_data['lat'] = map_data['customer_state'].map(lambda x: brazil_state_coords.get(x, {}).get('lat', 0))
    map_data['lon'] = map_data['customer_state'].map(lambda x: brazil_state_coords.get(x, {}).get('lon', 0))
    
    # Remove states without coordinates
    map_data = map_data[map_data['lat'] != 0]
    
    if map_data.empty:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'No Valid State Coordinates Available',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=500
        )
        return fig
    
    # Metric labels
    metric_labels = {
        'total_orders': 'Total Orders',
        'delivery_rate': 'Delivery Rate',
        'delay_rate': 'Delay Rate',
        'national_share': 'National Share'
    }
    
    # Create bubble map
    fig = go.Figure()
    
    # Calculate bubble sizes
    if metric in map_data.columns:
        values = map_data[metric]
        max_val = values.max()
        min_val = values.min()
        
        if max_val > min_val:
            sizes = 10 + 30 * (values - min_val) / (max_val - min_val)
        else:
            sizes = [20] * len(values)
        
        # Format hover text
        if metric in ['delivery_rate', 'delay_rate', 'national_share']:
            hover_values = [f'{v:.1f}%' for v in values]
        else:
            hover_values = [f'{v:,.0f}' for v in values]
        
        fig.add_trace(go.Scattergeo(
            lon=map_data['lon'],
            lat=map_data['lat'],
            text=map_data['customer_state'] + '<br>' + hover_values,
            mode='markers+text',
            marker=dict(
                size=sizes,
                color=values,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(
                    title=metric_labels.get(metric, metric),
                    title_side="right"  # FIXED: title_side instead of titleside
                ),
                line=dict(width=1, color='white')
            ),
            textposition="top center",
            textfont=dict(size=10, color='#202020'),
            hovertemplate='<b>%{text}</b><br>' +
                         'Lat: %{lat:.2f}<br>' +
                         'Lon: %{lon:.2f}<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': f'Brazil: {metric_labels.get(metric, metric)} by State',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        geo=dict(
            scope='south america',
            projection_type='mercator',
            showland=True,
            landcolor='#f5f5f5',
            countrycolor='#888888',
            coastlinecolor='#888888',
            showcountries=True,
            showsubunits=True,
            subunitcolor='#dddddd',
            center=dict(lat=-15, lon=-55),
            projection_scale=4
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=500,
        margin=dict(l=0, r=0, t=80, b=0)
    )
    
    # Fix hover background and text color
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",  # White background
            font_size=12,
            font_color="black"  # Black text
        )
    )
    
    return fig

def create_regional_performance_matrix(state_stats):
    """Create heatmap matrix of state performance metrics"""
    
    if state_stats.empty or len(state_stats) < 3:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'Insufficient State Data for Performance Matrix',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400
        )
        return fig
    
    # Select top states by order volume
    top_states = state_stats.nlargest(15, 'total_orders')
    
    # Prepare metrics for matrix
    metrics = ['total_orders', 'delivery_rate', 'delay_rate']
    metric_names = ['Order Volume', 'Delivery Rate', 'Delay Rate']
    
    # Normalize each metric for comparison
    matrix_data = []
    state_labels = []
    
    for _, state_row in top_states.iterrows():
        state_metrics = []
        for metric in metrics:
            if metric in state_row:
                # Normalize to 0-1 scale within top states
                metric_values = top_states[metric]
                min_val = metric_values.min()
                max_val = metric_values.max()
                
                if max_val > min_val:
                    norm_value = (state_row[metric] - min_val) / (max_val - min_val)
                else:
                    norm_value = 0.5
                
                state_metrics.append(norm_value)
            else:
                state_metrics.append(0)
        
        matrix_data.append(state_metrics)
        state_labels.append(state_row['customer_state'])
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix_data,
        x=metric_names,
        y=state_labels,
        colorscale='RdYlGn',
        reversescale=False,
        hoverongaps=False,
        colorbar=dict(
            title="Performance<br>(0=Low, 1=High)",
            title_side="right"  # FIXED: title_side instead of titleside
        ),
        hovertemplate='<b>%{y} - %{x}</b><br>' +
                     'Performance Score: %{z:.2f}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Regional Performance Matrix (Top 15 States)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Performance Metric',
        yaxis_title='State',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        height=500,
        margin=dict(l=100, r=50, t=80, b=50)
    )
    
    # Fix hover background and text color
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",  # White background
            font_size=12,
            font_color="black"  # Black text
        )
    )
    
    return fig

def create_regional_concentration_chart(state_stats):
    """Create Lorenz curve for regional concentration"""
    
    if state_stats.empty or len(state_stats) < 2:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'Insufficient Data for Concentration Analysis',
                'x': 0.5,
                'xanchor': 'center'
            },
            height=400
        )
        return fig, 0
    
    # Sort states by order share
    sorted_shares = state_stats['national_share'].sort_values(ascending=False).reset_index(drop=True)
    cumulative_pct = sorted_shares.cumsum()
    
    # Perfect equality line
    perfect_equality = np.linspace(0, 100, len(sorted_shares))
    
    # Calculate Gini coefficient
    lorenz_area = np.trapz(cumulative_pct, dx=1)
    perfect_area = np.trapz(perfect_equality, dx=1)
    gini_coefficient = (perfect_area - lorenz_area) / perfect_area if perfect_area > 0 else 0
    
    fig = go.Figure()
    
    # Lorenz curve
    fig.add_trace(go.Scatter(
        x=list(range(1, len(sorted_shares) + 1)),
        y=cumulative_pct,
        mode='lines',
        line=dict(color='#2C7D8B', width=3),
        fill='tozeroy',
        fillcolor='rgba(44, 125, 139, 0.2)',
        name='Actual Distribution'
    ))
    
    # Perfect equality line
    fig.add_trace(go.Scatter(
        x=list(range(1, len(sorted_shares) + 1)),
        y=perfect_equality,
        mode='lines',
        line=dict(color='#C9D2BA', width=2, dash='dash'),
        name='Perfect Equality'
    ))
    
    # Add annotation for Gini coefficient
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
            'text': 'Regional Concentration Analysis (Lorenz Curve)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title="States (sorted by order share)",
        yaxis_title="Cumulative Order Share (%)",
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
    
    # Fix hover background and text color
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",  # White background
            font_size=12,
            font_color="black"  # Black text
        )
    )
    
    return fig, gini_coefficient

# ======================= PAGE INITIALIZATION =======================

def initialize_page():
    """Initialize the geographic analysis page"""
    
    # Check if data is loaded
    if not st.session_state.get('data_loaded', False):
        st.error("⚠️ Data not loaded. Please go to the Home page and click 'Load All Data'.")
        st.stop()
    
    if st.session_state.orders is None:
        st.error("❌ Orders data not available. Please reload data from Home page.")
        st.stop()
    
    # Initialize geographic analysis with caching
    if 'geographic_analysis' not in st.session_state:
        with st.spinner("📍 Analyzing geographic patterns..."):
            results = get_geographic_analysis(st.session_state.orders)
            st.session_state.geographic_analysis = results
    
    return st.session_state.geographic_analysis

# ======================= MAIN PAGE CONTENT =======================

def main():
    """Main content for Geographic Analysis page"""
    
    # Page header
    st.markdown("""
    <h1 class="main-text">📍 Geographic Analysis</h1>
    <p class="sub-text">Regional distribution, performance, and geographic patterns across Brazil</p>
    """, unsafe_allow_html=True)
    
    # Quick navigation
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                border-radius: 8px; padding: 1rem; margin: 1rem 0;">
        <p style="color: var(--dark-text-secondary); margin: 0;">
            🔍 <b>Related Analysis:</b> 
            <a href="/🚨_Delay_Analysis" style="color: var(--dark-text-cool);">Delay Analysis</a> • 
            <a href="/📊_Delivery_Performance" style="color: var(--dark-text-cool);">Delivery Performance</a> • 
            <a href="/⏱️_Order_Timelines" style="color: var(--dark-text-cool);">Order Timelines</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize data
    analysis_data = initialize_page()
    state_stats = analysis_data['state_stats']
    concentration_stats = analysis_data['concentration_stats']
    has_state_data = analysis_data['has_state_data']
    
    # ======================= GEOGRAPHIC OVERVIEW =======================
    
    st.markdown('<h2 class="main-text">🗺️ Geographic Overview</h2>', unsafe_allow_html=True)
    
    # Check if we have geographic data
    if not has_state_data or state_stats.empty:
        st.warning("""
        ⚠️ **No Geographic Data Available**
        
        This analysis requires customer state data ('customer_state' column).
        No geographic information was found in the dataset.
        
        Some visualizations may not be available.
        """)
    
    # Geographic metrics
    if has_state_data and not state_stats.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="States with Orders",
                value=f"{concentration_stats['states_with_orders']}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="National Orders",
                value=f"{concentration_stats['national_total_orders']:,}",
                delta=None
            )
        
        with col3:
            top_state = state_stats.loc[state_stats['total_orders'].idxmax(), 'customer_state'] \
                        if len(state_stats) > 0 else 'N/A'
            st.metric(
                label="Top State",
                value=top_state,
                delta=None
            )
        
        with col4:
            avg_delivery = state_stats['delivery_rate'].mean()
            st.metric(
                label="Avg Delivery Rate",
                value=f"{avg_delivery:.1f}%",
                delta=None
            )
        
        # Concentration metrics
        st.markdown("### 🎯 Market Concentration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.8rem; color: #2C7D8B; font-weight: 600;">
                    {concentration_stats['top_3_states_share']:.1f}%
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                    Top 3 States<br>Market Share
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.8rem; color: #2C7D8B; font-weight: 600;">
                    {concentration_stats['top_5_states_share']:.1f}%
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                    Top 5 States<br>Market Share
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Calculate Herfindahl-Hirschman Index (HHI)
            market_shares = state_stats['national_share'] / 100
            hhi = (market_shares ** 2).sum() * 10000
            hhi_category = "Highly Concentrated" if hhi > 2500 else "Moderately Concentrated" if hhi > 1500 else "Unconcentrated"
            
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; text-align: center;">
                <div style="font-size: 1.8rem; color: #2C7D8B; font-weight: 600;">
                    {hhi:,.0f}
                </div>
                <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">
                    HHI Index<br>{hhi_category}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= BRAZIL MAP VISUALIZATION =======================
    
    if has_state_data and not state_stats.empty:
        st.markdown('<h2 class="main-text">🗺️ Brazil Map Visualization</h2>', unsafe_allow_html=True)
        
        # Map controls
        col1, col2 = st.columns(2)
        
        with col1:
            map_metric = st.selectbox(
                "Map Visualization Metric",
                ["total_orders", "delivery_rate", "delay_rate", "national_share"],
                help="Select what to visualize on the Brazil map"
            )
        
        with col2:
            map_type = st.selectbox(
                "Map Display Type",
                ["Bubble Map", "Performance Matrix", "Concentration Analysis"],
                help="Select how to visualize geographic data"
            )
        
        if map_type == "Bubble Map":
            # Create Brazil map
            fig_map = create_brazil_map_chart(state_stats, metric=map_metric)
            st.plotly_chart(fig_map, use_container_width=True)
            
            # Map interpretation
            metric_labels = {
                'total_orders': 'Order Volume',
                'delivery_rate': 'Delivery Performance',
                'delay_rate': 'Delay Patterns',
                'national_share': 'Market Share'
            }
            
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <p style="color: var(--dark-text-secondary); margin: 0;">
                    📍 <b>Map Interpretation:</b> Showing {metric_labels[map_metric]} across Brazilian states.
                    Larger and darker bubbles indicate higher values. Hover over states for detailed metrics.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        elif map_type == "Performance Matrix":
            # Create performance matrix
            fig_matrix = create_regional_performance_matrix(state_stats)
            st.plotly_chart(fig_matrix, use_container_width=True)
            
            st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <h4 class="warm-text" style="margin-top: 0;">🎯 Matrix Interpretation</h4>
                <ul style="color: var(--dark-text-secondary); margin: 0.5rem 0; padding-left: 1.2rem;">
                    <li><span style="color: #2A927A;">🟢 Green</span>: High performance relative to other states</li>
                    <li><span style="color: #C9D2BA;">🟡 Yellow</span>: Medium performance</li>
                    <li><span style="color: #8B4513;">🔴 Red</span>: Low performance relative to other states</li>
                </ul>
                <p style="color: var(--dark-text-secondary); margin: 0; font-size: 0.9rem;">
                    Note: Each metric is normalized separately. Green indicates high order volume, high delivery rates, or low delay rates.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        else:  # Concentration Analysis
            # Create concentration analysis
            fig_concentration, gini_coefficient = create_regional_concentration_chart(state_stats)
            st.plotly_chart(fig_concentration, use_container_width=True)
            
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                        border-radius: 8px; padding: 1.5rem; margin: 1rem 0;">
                <h4 class="warm-text" style="margin-top: 0;">📊 Concentration Analysis Insights</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
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
                        <div style="color: var(--dark-text-secondary); font-size: 0.9rem;">Top 3 States Share</div>
                        <div style="color: var(--dark-text-primary); font-size: 1.5rem; font-weight: 600;">
                            {concentration_stats['top_3_states_share']:.1f}%
                        </div>
                        <div style="color: var(--dark-text-secondary); font-size: 0.8rem;">of national orders</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ======================= STATE COMPARISON =======================
        
        st.markdown('<h2 class="main-text">📊 State Comparison Analysis</h2>', unsafe_allow_html=True)
        
        # Comparison controls
        col1, col2 = st.columns(2)
        
        with col1:
            comparison_metric = st.selectbox(
                "Comparison Metric",
                ["total_orders", "delivery_rate", "delay_rate", "national_share"],
                help="Select metric for state comparison"
            )
        
        with col2:
            top_n_states = st.slider(
                "Number of States to Show",
                min_value=5,
                max_value=27,
                value=15,
                help="Adjust how many states to display"
            )
        
        # Create comparison chart
        fig_comparison = create_state_orders_chart(
            state_stats, 
            metric=comparison_metric,
            top_n=top_n_states
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Regional segmentation
        st.markdown("### 🎯 Regional Segmentation")
        
        if 'volume_segment' in state_stats.columns:
            segment_summary = state_stats.groupby('volume_segment').agg(
                state_count=('customer_state', 'count'),
                total_orders=('total_orders', 'sum'),
                avg_delivery_rate=('delivery_rate', 'mean'),
                avg_delay_rate=('delay_rate', 'mean')
            ).reset_index()
            
            cols = st.columns(len(segment_summary))
            
            for idx, row in segment_summary.iterrows():
                with cols[idx]:
                    segment_color = ['#2C7D8B', '#2A927A', '#C9D2BA', '#8B4513'][idx % 4]
                    segment_pct = (row['total_orders'] / concentration_stats['national_total_orders'] * 100) \
                                  if concentration_stats['national_total_orders'] > 0 else 0
                    
                    st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                                border-radius: 8px; padding: 1rem; text-align: center;">
                        <div style="color: {segment_color}; font-size: 1.5rem; font-weight: 600;">
                            {row['state_count']}
                        </div>
                        <div style="color: var(--dark-text-primary); font-size: 1rem; font-weight: 500;">
                            {row['volume_segment']}
                        </div>
                        <div style="color: var(--dark-text-secondary); font-size: 0.8rem; margin-top: 0.5rem;">
                            {segment_pct:.1f}% of orders<br>
                            {row['avg_delivery_rate']:.1f}% delivery rate
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ======================= REGIONAL STRATEGY INSIGHTS =======================
    
    st.markdown('<h2 class="main-text">💡 Regional Strategy Insights</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">🎯 Market Development</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Focus growth efforts on high-potential underserved regions</li>
                <li>Strengthen presence in core high-volume markets</li>
                <li>Develop region-specific marketing and fulfillment strategies</li>
                <li>Optimize logistics networks based on regional patterns</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; padding: 1.5rem;">
            <h3 class="warm-text" style="margin-top: 0;">📊 Performance Optimization</h3>
            <ul style="color: var(--dark-text-secondary); padding-left: 1.2rem;">
                <li>Address delivery challenges in specific regions</li>
                <li>Implement region-specific service level agreements</li>
                <li>Monitor regional performance trends regularly</li>
                <li>Benchmark regional performance against national averages</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ======================= DATA EXPLORER =======================
    
    with st.expander("🔍 Explore Geographic Data", expanded=False):
        if has_state_data and not state_stats.empty:
            st.markdown("### 📊 State-Level Statistics")
            
            # Format for display
            display_stats = state_stats.copy()
            
            # Format numeric columns
            display_stats['total_orders'] = display_stats['total_orders'].apply(lambda x: f"{x:,}")
            display_stats['delivered_orders'] = display_stats['delivered_orders'].apply(lambda x: f"{x:,}")
            display_stats['delayed_orders'] = display_stats['delayed_orders'].apply(lambda x: f"{x:,}")
            display_stats['delivery_rate'] = display_stats['delivery_rate'].apply(lambda x: f"{x:.1f}%")
            display_stats['delay_rate'] = display_stats['delay_rate'].apply(lambda x: f"{x:.1f}%")
            display_stats['national_share'] = display_stats['national_share'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(
                display_stats,
                use_container_width=True,
                column_config={
                    "customer_state": "State Code",
                    "state_name": "State Name",
                    "total_orders": "Total Orders",
                    "delivered_orders": "Delivered Orders",
                    "delayed_orders": "Delayed Orders",
                    "delivery_rate": "Delivery Rate",
                    "delay_rate": "Delay Rate",
                    "national_share": "National Share",
                    "volume_segment": "Volume Segment"
                },
                hide_index=True
            )
            
            # Export option
            csv = state_stats.to_csv(index=False)
            st.download_button(
                label="📥 Download Geographic Data (CSV)",
                data=csv,
                file_name="olist_geographic_analysis.csv",
                mime="text/csv",
                type="secondary"
            )
        else:
            st.info("No geographic data available for display.")
    
    # ======================= PAGE FOOTER =======================
    
    st.markdown("---")
    
    if has_state_data and not state_stats.empty:
        total_states = concentration_stats['states_with_orders']
        national_orders = concentration_stats['national_total_orders']
        top_3_share = concentration_stats['top_3_states_share']
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
            <p>
                <b>Geographic Analysis</b> • {total_states} states analyzed • 
                {national_orders:,} national orders • 
                Top 3 states: {top_3_share:.1f}% market share
            </p>
            <p style="margin-top: 0.5rem;">
                Use regional analysis to develop targeted strategies and optimize operations across different Brazilian states.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; color: var(--dark-text-secondary); font-size: 0.9rem;">
            <p>
                <b>Geographic Analysis</b> • Geographic data not available in current dataset
            </p>
            <p style="margin-top: 0.5rem;">
                To enable geographic analysis, ensure orders data includes 'customer_state' column with Brazilian state codes.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ======================= CUSTOM CSS =======================

st.markdown("""
<style>
/* Geographic analysis styling */
.region-high { color: #2A927A; }
.region-medium { color: #C9D2BA; }
.region-low { color: #8B4513; }

/* Map optimizations */
.js-plotly-plot .scattergeo .trace {
    will-change: transform;
}

/* Performance matrix styling */
.js-plotly-plot .heatmaplayer .trace {
    transition: opacity 0.3s ease;
}

.js-plotly-plot .heatmaplayer .trace:hover {
    opacity: 0.9;
}

/* Metric card enhancements for geographic page */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    transition: all 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(44, 125, 139, 0.3) !important;
    box-shadow: 0 5px 15px rgba(44, 125, 139, 0.2);
}

/* Regional segment cards */
.region-card {
    transition: all 0.3s ease;
}

.region-card:hover {
    transform: translateY(-5px);
    border-color: rgba(212, 180, 131, 0.3) !important;
}

/* Fix Plotly hover styles */
.hovertext {
    background-color: white !important;
    color: black !important;
    border: 1px solid #ddd !important;
}

.hoverlabel {
    background-color: white !important;
    color: black !important;
    border: 1px solid #ddd !important;
}

/* Override Plotly default hover colors */
.js-plotly-plot .hovertext,
.js-plotly-plot .hoverlabel {
    background-color: white !important;
    color: black !important;
    fill: black !important;
}

/* Ensure text in hover boxes is black */
.hovertext text,
.hoverlabel text {
    fill: black !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()