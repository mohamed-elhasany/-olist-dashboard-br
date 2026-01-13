# analysis/revenue_analysis.py
"""
Enhanced Revenue Analysis Module for Olist Dashboard
Core functions from Revenue_Analy_plots.py with improved structure
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


class RevenueAnalyzer:
    """
    Main class for revenue analysis operations
    """
    
    def __init__(self, order_items: pd.DataFrame, products: pd.DataFrame):
        """
        Initialize analyzer with data
        
        Args:
            order_items: DataFrame containing order items data
            products: DataFrame containing products data
        """
        self.order_items = order_items
        self.products = products
        self.order_items_detailed = None
        self.analysis_results = None
        
    def prepare_data(self) -> pd.DataFrame:
        """
        Prepare and merge data for analysis
        
        Returns:
            DataFrame: Detailed order items with product information
        """
        # Merge order_items with products
        self.order_items_detailed = pd.merge(
            self.order_items, 
            self.products, 
            on='product_id', 
            how='left'
        )
        
        # Fill missing category names
        self.order_items_detailed['product_category_name'] = self.order_items_detailed['product_category_name'].fillna('Others')
        
        # Calculate total revenue (price + freight_value)
        self.order_items_detailed['Total'] = self.order_items_detailed['price'] + self.order_items_detailed['freight_value']
        
        return self.order_items_detailed
    
    def run_comprehensive_analysis(self) -> dict:
        """
        Run complete revenue analysis
        
        Returns:
            dict: Comprehensive analysis results
        """
        if self.order_items_detailed is None:
            self.prepare_data()
        
        # Calculate core metrics
        total_revenue = self.order_items_detailed['Total'].sum()
        
        order_totals = self.order_items_detailed.groupby('order_id')['Total'].sum()
        aov = order_totals.mean()
        
        total_orders = len(order_totals)
        total_products = len(self.order_items_detailed)
        avg_items_per_order = total_products / total_orders
        
        # Category analysis
        category_revenue_all = self._analyze_by_category('Total')
        category_revenue_freight = self._analyze_by_category('freight_value')
        category_revenue_price = self._analyze_by_category('price')
        
        # Vendor analysis
        vendor_revenue_all = self._analyze_by_vendor('Total')
        vendor_revenue_freight = self._analyze_by_vendor('freight_value')
        vendor_revenue_price = self._analyze_by_vendor('price')
        
        # Volume and weight analysis
        dimensional_columns = ['product_weight_g', 'product_length_cm', 
                              'product_height_cm', 'product_width_cm']
        missing_counts = self.order_items_detailed[dimensional_columns].isna().sum()
        
        volume_analysis_data = self.order_items_detailed.dropna(subset=dimensional_columns).copy()
        volume_analysis_data['Volume_cm'] = (
            volume_analysis_data['product_width_cm'] * 
            volume_analysis_data['product_height_cm'] * 
            volume_analysis_data['product_length_cm']
        )
        
        # Top performers
        top_category = category_revenue_all.iloc[0] if len(category_revenue_all) > 0 else None
        top_vendor = vendor_revenue_all.iloc[0] if len(vendor_revenue_all) > 0 else None
        
        # Store results
        self.analysis_results = {
            # Core metrics
            'total_revenue': total_revenue,
            'average_order_value': aov,
            'total_orders': total_orders,
            'total_products': total_products,
            'avg_items_per_order': avg_items_per_order,
            
            # Category revenue data
            'category_revenue_all': category_revenue_all,
            'category_revenue_freight': category_revenue_freight,
            'category_revenue_price': category_revenue_price,
            
            # Vendor revenue data
            'vendor_revenue_all': vendor_revenue_all,
            'vendor_revenue_freight': vendor_revenue_freight,
            'vendor_revenue_price': vendor_revenue_price,
            
            # Volume analysis data
            'volume_analysis_data': volume_analysis_data,
            'missing_dimensional_data': missing_counts,
            
            # Top performers
            'top_category': top_category,
            'top_vendor': top_vendor,
            
            # Raw detailed data
            'order_items_detailed': self.order_items_detailed
        }
        
        return self.analysis_results
    
    def _analyze_by_category(self, metric_column: str) -> pd.DataFrame:
        """
        Analyze revenue by product category
        
        Args:
            metric_column: Column to analyze ('Total', 'freight_value', 'price')
            
        Returns:
            DataFrame: Sorted category analysis
        """
        return (
            self.order_items_detailed
            .groupby('product_category_name', as_index=False)
            .agg(Total=(metric_column, 'sum'))
            .sort_values('Total', ascending=False)
            .reset_index(drop=True)
        )
    
    def _analyze_by_vendor(self, metric_column: str) -> pd.DataFrame:
        """
        Analyze revenue by vendor/seller
        
        Args:
            metric_column: Column to analyze ('Total', 'freight_value', 'price')
            
        Returns:
            DataFrame: Sorted vendor analysis
        """
        return (
            self.order_items_detailed
            .groupby('seller_id', as_index=False)
            .agg(Total=(metric_column, 'sum'))
            .sort_values('Total', ascending=False)
            .reset_index(drop=True)
        )
    
    def get_metrics_summary(self) -> dict:
        """
        Get key metrics as a simplified dictionary
        
        Returns:
            dict: Key metrics for display
        """
        if self.analysis_results is None:
            self.run_comprehensive_analysis()
        
        return {
            'total_revenue': self.analysis_results['total_revenue'],
            'average_order_value': self.analysis_results['average_order_value'],
            'total_orders': self.analysis_results['total_orders'],
            'total_products': self.analysis_results['total_products'],
            'avg_items_per_order': self.analysis_results['avg_items_per_order']
        }


# ===================== VISUALIZATION FUNCTIONS =====================

def create_category_revenue_chart(category_revenue_all: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """
    Create horizontal bar chart for top categories by revenue
    
    Args:
        category_revenue_all: Category revenue DataFrame
        top_n: Number of top categories to display
        
    Returns:
        Plotly Figure: Horizontal bar chart
    """
    # Get top categories
    top_categories = category_revenue_all.head(top_n)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_categories['product_category_name'],
        x=top_categories['Total'],
        orientation='h',
        marker_color='#2C7D8B',
        text=[f'R${val:,.0f}' for val in top_categories['Total']],
        textposition='auto',
        textfont=dict(size=10, color='white'),
        hovertemplate='<b>%{y}</b><br>Total Revenue: R$%{x:,.2f}<br><extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Top {top_n} Product Categories by Revenue',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Total Revenue (R$)',
        yaxis_title='Product Category',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(color='#333333'),
        height=400 + (top_n * 25),
        margin=dict(l=250, r=50, t=80, b=50),
        xaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#e0e0e0', tickformat=',.0f'),
        yaxis=dict(gridcolor='rgba(0,0,0,0)', autorange='reversed', tickfont=dict(size=11))
    )
    
    return fig


def create_vendor_revenue_chart(vendor_revenue_all: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """
    Create horizontal bar chart for top vendors by revenue
    
    Args:
        vendor_revenue_all: Vendor revenue DataFrame
        top_n: Number of top vendors to display
        
    Returns:
        Plotly Figure: Horizontal bar chart
    """
    top_vendors = vendor_revenue_all.head(top_n)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_vendors['seller_id'].astype(str),
        x=top_vendors['Total'],
        orientation='h',
        marker_color='#2A927A',
        text=[f'R${val:,.0f}' for val in top_vendors['Total']],
        textposition='auto',
        textfont=dict(size=10, color='white'),
        hovertemplate='<b>Vendor %{y}</b><br>Total Revenue: R$%{x:,.2f}<br><extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Top {top_n} Vendors by Revenue',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Total Revenue (R$)',
        yaxis_title='Vendor ID',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(color='#333333'),
        height=400 + (top_n * 25),
        margin=dict(l=100, r=50, t=80, b=50),
        xaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#e0e0e0', tickformat=',.0f'),
        yaxis=dict(gridcolor='rgba(0,0,0,0)', autorange='reversed', tickfont=dict(size=11))
    )
    
    return fig


def create_freight_weight_scatter(volume_analysis_data: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot: freight cost vs product weight
    
    Args:
        volume_analysis_data: DataFrame with product dimensions
        
    Returns:
        Plotly Figure: Scatter plot
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=volume_analysis_data['product_weight_g'],
        y=volume_analysis_data['freight_value'],
        mode='markers',
        marker=dict(color='#2C7D8B', size=6, opacity=0.7),
        hovertemplate='<b>Weight vs Freight</b><br>Weight: %{x}g<br>Freight: R$%{y:.2f}<br><extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Freight Cost vs Product Weight',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Product Weight (grams)',
        yaxis_title='Freight Value (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(color='#333333'),
        height=400,
        xaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#e0e0e0'),
        yaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#e0e0e0')
    )
    
    return fig


def create_freight_volume_scatter(volume_analysis_data: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot: freight cost vs product volume
    
    Args:
        volume_analysis_data: DataFrame with product dimensions
        
    Returns:
        Plotly Figure: Scatter plot
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=volume_analysis_data['Volume_cm'],
        y=volume_analysis_data['freight_value'],
        mode='markers',
        marker=dict(color='#2A927A', size=6, opacity=0.7),
        hovertemplate='<b>Volume vs Freight</b><br>Volume: %{x:.0f}cm³<br>Freight: R$%{y:.2f}<br><extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Freight Cost vs Product Volume',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Product Volume (cm³)',
        yaxis_title='Freight Value (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(color='#333333'),
        height=400,
        xaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#e0e0e0'),
        yaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#e0e0e0')
    )
    
    return fig


def create_freight_price_scatter(volume_analysis_data: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot: freight cost vs product price
    
    Args:
        volume_analysis_data: DataFrame with product dimensions
        
    Returns:
        Plotly Figure: Scatter plot
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=volume_analysis_data['price'],
        y=volume_analysis_data['freight_value'],
        mode='markers',
        marker=dict(color='#C9D2BA', size=6, opacity=0.7),
        hovertemplate='<b>Price vs Freight</b><br>Price: R$%{x:.2f}<br>Freight: R$%{y:.2f}<br><extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Freight Cost vs Product Price',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Product Price (R$)',
        yaxis_title='Freight Value (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(color='#333333'),
        height=400,
        xaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#e0e0e0'),
        yaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#e0e0e0')
    )
    
    return fig


def create_price_weight_volume_scatter(volume_analysis_data: pd.DataFrame) -> go.Figure:
    """
    Create bubble chart: price vs weight with volume as bubble size
    
    Args:
        volume_analysis_data: DataFrame with product dimensions
        
    Returns:
        Plotly Figure: Bubble chart
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=volume_analysis_data['product_weight_g'],
        y=volume_analysis_data['price'],
        mode='markers',
        marker=dict(
            color=volume_analysis_data['Volume_cm'],
            size=volume_analysis_data['Volume_cm'] / 100,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Volume (cm³)",
                title_side="right",
                tickformat=",.0f"
            )
        ),
        hovertemplate='<b>Weight vs Price vs Volume</b><br>' +
                     'Weight: %{x}g<br>' +
                     'Price: R$%{y:.2f}<br>' +
                     'Volume: %{marker.color:.0f}cm³<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Product Price vs Weight (Bubble Size = Volume)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': '#333333'}
        },
        xaxis_title='Product Weight (grams)',
        yaxis_title='Product Price (R$)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        font=dict(color='#333333'),
        height=450,
        xaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#e0e0e0'),
        yaxis=dict(gridcolor='#e0e0e0', zerolinecolor='#e0e0e0')
    )
    
    return fig


# ===================== UTILITY FUNCTIONS =====================

def get_revenue_metrics_display(metrics: dict) -> str:
    """
    Format revenue metrics for display
    
    Args:
        metrics: Dictionary of revenue metrics
        
    Returns:
        str: Formatted metrics text
    """
    return f"""
    **Total Revenue:** R${metrics['total_revenue']:,.2f}
    
    **Average Order Value:** R${metrics['average_order_value']:,.2f}
    
    **Total Orders:** {metrics['total_orders']:,}
    
    **Total Products Sold:** {metrics['total_products']:,}
    
    **Avg Items per Order:** {metrics['avg_items_per_order']:.2f}
    """


def analyze_revenue_data(order_items: pd.DataFrame, products: pd.DataFrame) -> dict:
    """
    Convenience function to run complete revenue analysis
    
    Args:
        order_items: Order items DataFrame
        products: Products DataFrame
        
    Returns:
        dict: Analysis results
    """
    analyzer = RevenueAnalyzer(order_items, products)
    return analyzer.run_comprehensive_analysis()