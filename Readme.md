# 📊 Olist Brazilian E-Commerce Dashboard

🇧🇷 **Interactive Analytics Dashboard for Brazil's Largest E-Commerce Marketplace**

A comprehensive Streamlit-powered analytics platform that transforms raw e-commerce data from Olist into actionable business insights through interactive visualizations and performance metrics.

---

## ✨ **Dashboard Highlights**

### **📈 Revenue Intelligence**

- **Total Revenue Analytics**: Track sales performance across product categories and vendors
- **Price vs Freight Analysis**: Optimize pricing strategies with shipping cost correlations
- **Vendor Performance**: Identify top-performing sellers and revenue concentration

### **🚚 Delivery Operations**

- **Timeline Analysis**: Breakdown of order processing stages (site → seller → shipping)
- **Delay Heatmaps**: Visual patterns in delivery delays and bottleneck identification
- **Geographic Performance**: Regional delivery success rates across Brazilian states

### **📦 Product Insights**

- **Category Analytics**: Revenue distribution across product categories
- **Dimensional Analysis**: Freight optimization based on product weight and dimensions
- **Performance Benchmarks**: SLA compliance and delivery success metrics

---

## 🛠️ **Technology Stack**

| Component           | Technology      | Purpose                      |
| ------------------- | --------------- | ---------------------------- |
| **Frontend**        | Streamlit       | Interactive web dashboard    |
| **Data Processing** | Pandas, NumPy   | Data manipulation & analysis |
| **Visualization**   | Plotly          | Interactive charts & graphs  |
| **Caching**         | Streamlit Cache | Performance optimization     |
| **Styling**         | Custom CSS      | Dark theme UI/UX             |

---

## 📁 **Data Architecture**

### **Primary Datasets**

1. **`order_items.csv`** - Order line items with pricing and freight details
2. **`products.csv`** - Product catalog with dimensions and categories
3. **`orders.csv`** - Order metadata and delivery timelines

### **Data Flow**

Google Drive → Cached Load → Data Processing → Interactive Visualizations

---

## 🚀 **Quick Start Guide**

### **1. Installation**

```bash
# Clone repository
git clone https://github.com/yourusername/olist-dashboard.git
cd olist-dashboard

# Install dependencies
pip install -r requirements.txt
```

### **2. Launch Dashboard**

- streamlit run "🏠_Home.py"

### **3. Data Loading**

- Open dashboard at [http://localhost:8501](http://localhost:8501)
- Click "Load All Data" in sidebar
- Wait for data caching (first-time only)
- Explore interactive visualizations

---

### **📊 Navigation Map**

- **🏠 Home Dashboard**: Quick metrics overview, dataset previews, navigation guidance
- **💰 Revenue Overview**: Total revenue metrics, top categories & vendors, revenue composition analysis
- **📦 Product Category Analysis**: Category performance ranking, revenue concentration metrics, growth opportunity identification
- **🏢 Vendor Analysis**: Vendor segmentation by revenue, concentration analysis (Lorenz curves), health check metrics
- **🚚 Freight Analysis**: Shipping cost vs. product dimensions, freight efficiency metrics, optimization recommendations
- **⏱️ Order Timelines**: Processing stage duration analysis, timeline distribution visualization, performance trend tracking
- **🚨 Delay Analysis**: Delay severity classification, stage-wise delay patterns, heatmap visualization
- **📍 Geographic Analysis**: Brazil state-level performance, regional concentration metrics, map visualizations
- **📊 Delivery Performance**: SLA compliance tracking, delivery success rates, performance benchmarks

---

### **⚡ Performance Features**

- Smart Caching: 1-hour TTL for frequently accessed data
- Lazy Loading: Data loads only when needed per page
- Interactive Filters: Real-time filtering without page reloads
- Optimized Visualizations: Efficient Plotly rendering

---

### **🎨 UI/UX Features**

- Dark Theme: Custom CSS for reduced eye strain
- Responsive Design: Adapts to different screen sizes
- Interactive Charts: Hover details and zoom capabilities
- Print Optimization: Charts designed for reporting

---

### **📈 Business Applications**

- **For Executives**: Revenue tracking and forecasting, market concentration analysis, strategic partnership identification
- **For Operations**: Delivery bottleneck identification, freight cost optimization, vendor performance monitoring
- **For Analysts**: Data exploration without coding, custom visualization generation, performance trend analysis

---

### **📝 Notes & Considerations**

**Data Limitations**

- Analysis based on historical Olist dataset
- Excludes orders without items in order_items table
- Geographic coverage limited to Brazilian states

**Performance Notes**

- Initial data load may take 1-2 minutes
- Large datasets optimized for 8GB+ RAM systems
- Caching improves subsequent page loads

**Best Practices**

- Use "Load All Data" once per session
- Apply filters progressively for complex queries
- Export specific insights using CSV download buttons

---

### **🤝 Contributing**

**Report Issues**

- Check existing issues on GitHub
- Provide dataset version and error details
- Include screenshots for UI issues

**Feature Requests**

- Describe business use case
- Specify required data points
- Suggest visualization approach

---

### **📧 Contact & Support**

- **Developer**: Mohamed Elhasany
- **Role**: General Data Analyst
- **Email**: elhasanymohamed123@gmail.com

**Professional Profiles:**

- [GitHub](https://github.com/mohamed-elhasany)
- [Khamsat](https://khamsat.com/user/elhasany_123)
- [Freelancer](https://www.freelancer.com/u/mohamede0226)

**Services Offered**: Custom dashboard development, e-commerce analytics consulting, data pipeline implementation, business intelligence solutions

---

### **📄 License**

This dashboard is provided for educational and analytical purposes.  
Commercial use requires permission from the dataset owner (Olist) and dashboard developer.

---

### **🚨 Disclaimer**

This dashboard analyzes public historical data from Olist (2016-2018).  
Insights should be validated with current business data for operational decisions.

---

### **🌟 Acknowledgments**

- Olist for making the e-commerce dataset publicly available
- Streamlit for the excellent dashboard framework
- Plotly for interactive visualization capabilities
- Pandas community for robust data analysis tools

**Last Updated**: January 2026  
**Dataset Version**: Olist Public Dataset  
**Dashboard Version**: 1.0.0
