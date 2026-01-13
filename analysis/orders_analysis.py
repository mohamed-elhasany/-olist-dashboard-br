# analysis/orders_analysis.py
"""
Enhanced Orders Analysis Module for Olist Dashboard
Core functions from Orders_Analy_plots.py with improved structure
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Optional, List, Tuple

class OrdersAnalyzer:
    """
    Main class for orders analysis operations
    Assumes orders data is already cleaned and prepared
    """
    
    def __init__(self, orders: pd.DataFrame):
        """
        Initialize analyzer with pre-cleaned orders data
        
        Args:
            orders: DataFrame containing cleaned orders data with all timing metrics calculated
        """
        # Store the data and ensure Delay column is timedelta
        self.orders = orders.copy()
        self.orders_clean = orders.copy()  # Already cleaned
        
        # Ensure Delay column is timedelta if it exists
        if 'Delay' in self.orders.columns:
            self._convert_delay_to_timedelta()
    
    def _convert_delay_to_timedelta(self):
        """Convert Delay column to timedelta if it's not already"""
        # Check if Delay column exists and needs conversion
        if 'Delay' in self.orders.columns:
            if not pd.api.types.is_timedelta64_dtype(self.orders['Delay']):
                try:
                    # Try to convert string/timedelta format to timedelta
                    self.orders['Delay'] = pd.to_timedelta(self.orders['Delay'])
                except (ValueError, TypeError):
                    # If conversion fails, try parsing as days or hours
                    try:
                        # Check if it's numeric (like days)
                        if pd.api.types.is_numeric_dtype(self.orders['Delay']):
                            self.orders['Delay'] = pd.to_timedelta(self.orders['Delay'], unit='D')
                        else:
                            # Try other common formats
                            self.orders['Delay'] = pd.to_timedelta(self.orders['Delay'].astype(str))
                    except Exception:
                        # If all conversions fail, set to NaT and log warning
                        print("Warning: Could not convert Delay column to timedelta")
                        self.orders['Delay'] = pd.NaT
        
        # Do the same for orders_clean
        if 'Delay' in self.orders_clean.columns:
            if not pd.api.types.is_timedelta64_dtype(self.orders_clean['Delay']):
                try:
                    self.orders_clean['Delay'] = pd.to_timedelta(self.orders_clean['Delay'])
                except (ValueError, TypeError):
                    try:
                        if pd.api.types.is_numeric_dtype(self.orders_clean['Delay']):
                            self.orders_clean['Delay'] = pd.to_timedelta(self.orders_clean['Delay'], unit='D')
                        else:
                            self.orders_clean['Delay'] = pd.to_timedelta(self.orders_clean['Delay'].astype(str))
                    except Exception:
                        print("Warning: Could not convert Delay column to timedelta in orders_clean")
                        self.orders_clean['Delay'] = pd.NaT
    
    def get_delivery_performance(self) -> dict:
        """
        Calculate delivery performance metrics
        
        Returns:
            dict: Delivery performance statistics
        """
        # Create a safe working copy
        working = self.orders[['Net_State', 'Delay']].copy()
        
        # Ensure Delay is timedelta for comparisons
        if not pd.api.types.is_timedelta64_dtype(working['Delay']):
            working['Delay'] = pd.to_timedelta(working['Delay'], errors='coerce')
        
        # Drop NaN values from Delay column for accurate categorization
        working_clean = working.dropna(subset=['Delay'])
        
        # Categorize orders (your original logic)
        # Note: Use pd.Timedelta(0) for comparison
        zero_td = pd.Timedelta(0)
        
        # Handle cases where Delay might still be object type
        try:
            delay_delivered = working_clean.loc[(working_clean['Delay'] < zero_td) & (working_clean['Net_State'] == 'Delivered')]
            delay_not_delivered = working_clean.loc[(working_clean['Delay'] < zero_td) & (working_clean['Net_State'] == 'Not_Delivered')]
            no_delay_delivered = working_clean.loc[(working_clean['Delay'] > zero_td) & (working_clean['Net_State'] == 'Delivered')]
            no_delay_not_delivered = working_clean.loc[(working_clean['Delay'] > zero_td) & (working_clean['Net_State'] == 'Not_Delivered')]
        except TypeError as e:
            # Fallback: convert to numeric days if comparison fails
            print(f"Warning: Delay comparison failed: {e}")
            # Convert to days
            working_clean['delay_days'] = pd.to_timedelta(working_clean['Delay']).dt.total_seconds() / (24 * 3600)
            
            delay_delivered = working_clean.loc[(working_clean['delay_days'] < 0) & (working_clean['Net_State'] == 'Delivered')]
            delay_not_delivered = working_clean.loc[(working_clean['delay_days'] < 0) & (working_clean['Net_State'] == 'Not_Delivered')]
            no_delay_delivered = working_clean.loc[(working_clean['delay_days'] > 0) & (working_clean['Net_State'] == 'Delivered')]
            no_delay_not_delivered = working_clean.loc[(working_clean['delay_days'] > 0) & (working_clean['Net_State'] == 'Not_Delivered')]
        
        total_orders = len(working_clean)
        delivered_orders = len(working_clean[working_clean['Net_State'] == 'Delivered'])
        not_delivered_orders = len(working_clean[working_clean['Net_State'] == 'Not_Delivered'])
        
        return {
            'delay_delivered': delay_delivered,
            'delay_not_delivered': delay_not_delivered,
            'no_delay_delivered': no_delay_delivered,
            'no_delay_not_delivered': no_delay_not_delivered,
            'total_orders': total_orders,
            'delivered_orders': delivered_orders,
            'not_delivered_orders': not_delivered_orders,
            'delivery_rate': (delivered_orders / total_orders * 100) if total_orders > 0 else 0,
            'on_time_rate': (len(no_delay_delivered) / delivered_orders * 100) if delivered_orders > 0 else 0
        }
    
    def get_delayed_orders_by_stage(self, 
                                   delivery_status: str = 'Delivered',
                                   pct_col: str = 'Site_Real_PCT') -> pd.DataFrame:
        """
        Get delayed orders filtered by delivery status and percentage column
        
        Args:
            delivery_status: 'Delivered', 'Not_Delivered', or 'All'
            pct_col: Percentage column to filter by
            
        Returns:
            DataFrame: Filtered delayed orders
        """
        # Ensure Delay is timedelta
        if not pd.api.types.is_timedelta64_dtype(self.orders_clean['Delay']):
            self.orders_clean['Delay'] = pd.to_timedelta(self.orders_clean['Delay'], errors='coerce')
        
        # Get delayed orders (Delay < 0)
        try:
            delayed = self.orders_clean.loc[self.orders_clean['Delay'] < pd.Timedelta(0)].copy()
        except TypeError:
            # Fallback: convert to days
            self.orders_clean['delay_days'] = pd.to_timedelta(self.orders_clean['Delay']).dt.total_seconds() / (24 * 3600)
            delayed = self.orders_clean.loc[self.orders_clean['delay_days'] < 0].copy()
        
        if delivery_status != 'All':
            delayed = delayed.loc[delayed['Net_State'] == delivery_status]
        
        if delayed.empty:
            return pd.DataFrame()
        
        # Convert delay to days if not already
        if 'delay_days' not in delayed.columns:
            delayed['delay_days'] = delayed['Delay'].dt.total_seconds() / (24 * 3600)
        
        return delayed


# ===================== VISUALIZATION FUNCTIONS =====================

def create_delay_heatmap(delayed_orders: pd.DataFrame,
                        pct_col: str = 'Site_Real_PCT',
                        delay_day_ranges: Optional[List[Tuple]] = None,
                        color_scale: str = 'Blues',
                        title: Optional[str] = None) -> go.Figure:
    """
    Create heatmap of delayed orders vs percentage metric
    
    Args:
        delayed_orders: DataFrame of delayed orders
        pct_col: Percentage column for analysis
        delay_day_ranges: Custom delay day ranges
        color_scale: Plotly color scale
        title: Custom chart title
        
    Returns:
        Plotly Figure: Heatmap
    """
    if delayed_orders.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': 'No delayed orders available for the selected filters',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#333333'}
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='white',
            height=400
        )
        return fig
    
    # Ensure delay_days exists and is numeric
    if 'delay_days' not in delayed_orders.columns:
        # Try to create it from Delay column
        if 'Delay' in delayed_orders.columns:
            # Convert Delay to timedelta if needed
            if not pd.api.types.is_timedelta64_dtype(delayed_orders['Delay']):
                delayed_orders['Delay'] = pd.to_timedelta(delayed_orders['Delay'], errors='coerce')
            delayed_orders['delay_days'] = delayed_orders['Delay'].dt.total_seconds() / (24 * 3600)
        else:
            raise ValueError("No delay information available in delayed_orders DataFrame")
    
    # Define delay day ranges
    if delay_day_ranges is None:
        delay_day_ranges = [(-30, -20), (-20, -10), (-10, -5), (-5, -2), (-2, 0)]
    
    # Create bins
    bins = [delay_day_ranges[0][0]] + [r[1] for r in delay_day_ranges]
    labels = [f"{start}–{end}" for start, end in delay_day_ranges]
    delayed_orders['delay_bin'] = pd.cut(
        delayed_orders['delay_days'], 
        bins=bins, 
        labels=labels, 
        include_lowest=True
    )
    
    # Create percentage bins
    pct_bins = np.linspace(0, 100, 11)
    pct_labels = [f"{int(low)}–{int(high)} %" for low, high in zip(pct_bins[:-1], pct_bins[1:])]
    delayed_orders['pct_bin'] = pd.cut(
        delayed_orders[pct_col], 
        bins=pct_bins, 
        labels=pct_labels, 
        include_lowest=True
    )
    
    # Create pivot table
    heat = pd.crosstab(delayed_orders['delay_bin'], delayed_orders['pct_bin'], dropna=False).fillna(0)
    heat = heat.sort_index(ascending=False)
    
    # Prepare data for heatmap
    z = heat.values
    z_text = np.where(z == 0, '', z.astype(int).astype(str))
    
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=heat.columns,
            y=heat.index,
            colorscale=color_scale,
            colorbar=dict(title="Orders", tickformat=","),
            text=z_text,
            texttemplate="%{text}",
            textfont=dict(size=10, color='#202020'),
            hovertemplate=(
                '<b>Delay:</b> %{y}<br>'
                '<b>% Range:</b> %{x}<br>'
                '<b>Orders:</b> %{z}<extra></extra>'
            )
        )
    )
    
    # Default title
    if title is None:
        pct_display = pct_col.replace('_', ' ')
        title = f"Delayed Orders Analysis - {pct_display}"
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis=dict(
            title=f"{pct_col.replace('_', ' ')} ranges",
            side='bottom',
            tickangle=45,
            gridcolor='rgba(0,0,0,0)',
            tickfont=dict(color='#333333', size=11)
        ),
        yaxis=dict(
            title='Delay ranges (days)',
            autorange='reversed',
            gridcolor='rgba(0,0,0,0)',
            tickfont=dict(color='#333333', size=11)
        ),
        font=dict(color='#333333'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        margin=dict(l=100, r=30, t=60, b=80),
        height=500
    )
    
    return fig


def create_delivery_performance_chart(delivery_performance: dict, 
                                     chart_type: str = 'delivered') -> go.Figure:
    """
    Create delivery performance chart
    
    Args:
        delivery_performance: Dictionary from get_delivery_performance()
        chart_type: 'delivered' or 'not_delivered'
        
    Returns:
        Plotly Figure: Performance chart
    """
    if chart_type == 'delivered':
        counts = {
            'No Delay': len(delivery_performance['no_delay_delivered']),
            'With Delay': len(delivery_performance['delay_delivered'])
        }
        total = counts['No Delay'] + counts['With Delay']
        title = 'Delivered Orders Performance'
        colors = ['#2A927A', '#C9D2BA']
        x_label = 'Delivered'
    else:
        counts = {
            'No Delay': len(delivery_performance['no_delay_not_delivered']),
            'With Delay': len(delivery_performance['delay_not_delivered'])
        }
        total = counts['No Delay'] + counts['With Delay']
        title = 'Not Delivered Orders Analysis'
        colors = ['#2C7D8B', '#8B4513']
        x_label = 'Not Delivered'
    
    # Calculate percentages
    percentages = {k: (v / total * 100) if total > 0 else 0 for k, v in counts.items()}
    
    fig = go.Figure()
    
    # Add bars
    categories = list(counts.keys())
    for i, category in enumerate(categories):
        fig.add_trace(go.Bar(
            name=category,
            x=[x_label],
            y=[counts[category]],
            marker_color=colors[i],
            text=[f"{counts[category]:,}<br>({percentages[category]:.1f}%)"],
            textposition='auto',
            textfont=dict(color='white', size=12),
            hovertemplate=f'<b>{x_label} - {category}</b><br>' +
                         'Count: %{y:,}<br>' +
                         'Percentage: %{text}<br>' +
                         '<extra></extra>'
        ))
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#333333'}
        },
        xaxis_title='Delivery Status',
        yaxis_title='Number of Orders',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(color='#333333'),
        height=400,
        margin=dict(l=80, r=50, t=80, b=50),
        barmode='group',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            font=dict(size=11)
        ),
        xaxis=dict(gridcolor='rgba(0,0,0,0)', tickfont=dict(size=12)),
        yaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#e0e0e0', tickformat=',.0f')
    )
    
    return fig


def create_geo_bubble_map(orders: pd.DataFrame,
                         metric: str = 'orders',
                         status: str = 'All',
                         delayed_only: bool = False,
                         bubble_size_multiplier: float = 1.0,
                         color_scale: str = 'Viridis',
                         show_state_names: bool = True) -> go.Figure:
    """
    Create geographic bubble map for Brazil states
    
    Args:
        orders: Orders DataFrame
        metric: 'orders', 'revenue', or 'delayed'
        status: 'Delivered', 'Not_Delivered', or 'All'
        delayed_only: Filter for delayed orders only
        bubble_size_multiplier: Size multiplier for bubbles
        color_scale: Color scale for bubbles
        show_state_names: Show state names on map
        
    Returns:
        Plotly Figure: Bubble map
    """
    # Brazil state centroids
    BRAZIL_STATE_CENTROIDS = {
        'AC': {'lat': -9.0238, 'lon': -70.8120}, 'AL': {'lat': -9.5713, 'lon': -36.7819},
        'AP': {'lat': 0.9020, 'lon': -51.8544}, 'AM': {'lat': -3.4168, 'lon': -65.8561},
        'BA': {'lat': -12.5797, 'lon': -41.7007}, 'CE': {'lat': -5.4984, 'lon': -39.3206},
        'DF': {'lat': -15.7801, 'lon': -47.9292}, 'ES': {'lat': -19.1834, 'lon': -40.3089},
        'GO': {'lat': -15.8270, 'lon': -49.8362}, 'MA': {'lat': -5.4026, 'lon': -45.1116},
        'MT': {'lat': -12.6819, 'lon': -56.9211}, 'MS': {'lat': -20.7722, 'lon': -54.7852},
        'MG': {'lat': -18.5122, 'lon': -44.5550}, 'PA': {'lat': -3.4168, 'lon': -52.0030},
        'PB': {'lat': -7.2400, 'lon': -36.7820}, 'PR': {'lat': -24.7953, 'lon': -51.7955},
        'PE': {'lat': -8.8137, 'lon': -36.9541}, 'PI': {'lat': -6.6000, 'lon': -42.2800},
        'RJ': {'lat': -22.9068, 'lon': -43.1729}, 'RN': {'lat': -5.7945, 'lon': -36.5172},
        'RS': {'lat': -30.0346, 'lon': -51.2177}, 'RO': {'lat': -11.5057, 'lon': -63.5806},
        'RR': {'lat': 2.7376, 'lon': -62.0751}, 'SC': {'lat': -27.5954, 'lon': -48.5480},
        'SP': {'lat': -23.5505, 'lon': -46.6333}, 'SE': {'lat': -10.5741, 'lon': -37.3857},
        'TO': {'lat': -10.1753, 'lon': -48.2982}
    }
    
    BRAZIL_STATE_NAMES = {
        'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
        'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
        'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
        'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
        'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
        'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
        'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
    }
    
    # Create a copy to avoid modifying original
    df = orders.copy()
    
    # Ensure Delay is timedelta for delayed filtering
    if delayed_only or metric == 'delayed':
        if 'Delay' in df.columns:
            if not pd.api.types.is_timedelta64_dtype(df['Delay']):
                df['Delay'] = pd.to_timedelta(df['Delay'], errors='coerce')
    
    # Filter data
    if status != 'All':
        df = df.loc[df['Net_State'] == status].copy()
    
    if delayed_only or metric == 'delayed':
        try:
            df = df.loc[df['Delay'] < pd.Timedelta(0)]
        except TypeError:
            # Fallback: convert to days
            df['delay_days'] = pd.to_timedelta(df['Delay']).dt.total_seconds() / (24 * 3600)
            df = df.loc[df['delay_days'] < 0]
    
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': "No data available for selected filters",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#333333'}
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='white',
            height=400
        )
        return fig
    
    # Aggregate by state
    if metric == 'orders':
        geo_df = df.groupby('customer_state', as_index=False).agg(
            value=('order_id', 'nunique')
        )
    elif metric == 'delayed':
        geo_df = df.groupby('customer_state', as_index=False).agg(
            value=('order_id', 'nunique')
        )
    else:  # Assuming revenue metric
        if 'TOTAL' in df.columns:
            geo_df = df.groupby('customer_state', as_index=False).agg(
                value=('TOTAL', 'sum')
            )
        else:
            geo_df = df.groupby('customer_state', as_index=False).agg(
                value=('order_id', 'nunique')
            )
    
    geo_df = geo_df.rename(columns={'customer_state': 'state'})
    
    # Add coordinates
    geo_df['lat'] = geo_df['state'].map(lambda x: BRAZIL_STATE_CENTROIDS.get(x, {}).get('lat', None))
    geo_df['lon'] = geo_df['state'].map(lambda x: BRAZIL_STATE_CENTROIDS.get(x, {}).get('lon', None))
    geo_df['state_name'] = geo_df['state'].map(lambda x: BRAZIL_STATE_NAMES.get(x, x))
    
    # Remove states without coordinates
    geo_df = geo_df.dropna(subset=['lat', 'lon'])
    
    if geo_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': "No states with coordinates found in data",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#333333'}
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='white',
            height=400
        )
        return fig
    
    # Calculate bubble sizes
    min_value = geo_df['value'].min()
    max_value = geo_df['value'].max()
    
    if max_value > min_value:
        geo_df['bubble_size'] = 10 + 30 * (geo_df['value'] - min_value) / (max_value - min_value)
    else:
        geo_df['bubble_size'] = 20
    
    geo_df['bubble_size'] = geo_df['bubble_size'] * bubble_size_multiplier
    
    # Create figure
    fig = go.Figure()
    
    fig.add_trace(go.Scattergeo(
        lon=geo_df['lon'],
        lat=geo_df['lat'],
        text=geo_df['state'] + '<br>' + geo_df['value'].apply(lambda x: f"{x:,}"),
        mode='markers+text' if show_state_names else 'markers',
        marker=dict(
            size=geo_df['bubble_size'],
            color=geo_df['value'],
            colorscale=color_scale,
            colorbar=dict(title="Value", title_side="right"),
            line=dict(width=1.5, color='white'),
            sizemode='diameter',
            opacity=0.85,
            showscale=True
        ),
        textposition="top center",
        textfont=dict(size=10, color='#333333'),
        hovertemplate=(
            '<b>%{customdata[0]} (%{customdata[1]})</b><br>' +
            'Value: %{customdata[2]:,}<br>' +
            '<extra></extra>'
        ),
        customdata=geo_df[['state_name', 'state', 'value']],
        showlegend=False
    ))
    
    # Build title
    metric_display = metric.capitalize()
    status_display = status if status != 'All' else 'All Orders'
    
    if delayed_only:
        title_text = f"{metric_display} by State - {status_display} (Delayed Only)"
    else:
        title_text = f"{metric_display} by State - {status_display}"
    
    fig.update_layout(
        title={
            'text': title_text,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(color='#333333'),
        height=500,
        margin=dict(l=0, r=0, t=80, b=20),
        geo=dict(
            scope='south america',
            projection_type='mercator',
            showcountries=True,
            countrycolor='#888888',
            showland=True,
            landcolor='#f5f5f5',
            showocean=True,
            oceancolor='#e8f4f8',
            coastlinecolor='#888888',
            center=dict(lat=-15, lon=-55),
            projection_scale=4
        )
    )
    
    return fig


def create_daily_trend_chart(orders: pd.DataFrame,
                            metric: str = 'orders',
                            date_col: str = 'order_purchase_timestamp',
                            window: int = 7) -> go.Figure:
    """
    Create daily trend chart with rolling average
    
    Args:
        orders: Orders DataFrame
        metric: 'orders' or 'revenue'
        date_col: Date column to use
        window: Rolling window size in days
        
    Returns:
        Plotly Figure: Trend chart
    """
    # Ensure date column is datetime
    orders = orders.copy()
    orders['date'] = pd.to_datetime(orders[date_col]).dt.date
    
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
        mode='lines+markers',
        line=dict(color='#2C7D8B', width=2),
        marker=dict(size=4),
        hovertemplate='%{x|%Y-%m-%d}<br>' +
                      f'{metric.title()} ({window}-day avg): %{{y:,.0f}}' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Daily {metric.title()} Trend ({window}-day rolling average)',
        xaxis_title='Date',
        yaxis_title=f'{metric.title()} ({window}-day avg)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(color='#333333'),
        height=400
    )
    
    return fig


# ===================== UTILITY FUNCTIONS =====================

def get_delivery_metrics_display(metrics: dict) -> str:
    """
    Format delivery metrics for display
    
    Args:
        metrics: Dictionary from get_delivery_performance()
        
    Returns:
        str: Formatted metrics text
    """
    return f"""
    **Total Orders:** {metrics['total_orders']:,}
    
    **Delivered Orders:** {metrics['delivered_orders']:,} ({metrics['delivery_rate']:.1f}%)
    
    **On-Time Delivery Rate:** {metrics['on_time_rate']:.1f}%
    
    **Delayed & Delivered:** {len(metrics['delay_delivered']):,}
    
    **Delayed & Not Delivered:** {len(metrics['delay_not_delivered']):,}
    """


def analyze_orders_data(orders: pd.DataFrame) -> dict:
    """
    Convenience function to run complete orders analysis
    
    Args:
        orders: Orders DataFrame
        
    Returns:
        dict: Analysis results including analyzer object and performance metrics
    """
    analyzer = OrdersAnalyzer(orders)
    performance = analyzer.get_delivery_performance()
    
    return {
        'analyzer': analyzer,
        'performance': performance,
        'orders_data': analyzer.orders
    }