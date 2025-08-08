import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Simple path setup - add repo root to sys.path for shared imports
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

# Direct imports from specific modules (no __init__.py dependency)
from shared.common.snowflake_utils import get_connection, get_active_session_connection
from shared.common.ui_components import display_metric, create_line_chart, create_pie_chart, display_dataframe, create_scatter_plot, create_bar_chart, create_area_chart
from shared.common.data_utils import generate_sample_data, generate_customer_data, generate_trend_data

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_snowflake_connection():
    """Get Snowflake connection with environment detection"""
    try:
        # First try: SIS environment (get_active_session)
        return get_active_session_connection()
    except:
        try:
            # Second try: Local development with Snow CLI
            return get_connection("streamlit_env")
        except:
            # Third try: Default connection
            return get_connection()

def main():
    """Sales Dashboard Application."""
    st.title("📊 Sales Dashboard")
    st.markdown("---")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Dashboard Controls")
        
        # Connection test
        if st.button("Test Connection"):
            try:
                conn = get_snowflake_connection()
                if conn.test_connection():
                    st.success("✅ Connected to Snowflake!")
                    st.write(f"Database: {conn.current_database}")
                    st.write(f"Schema: {conn.current_schema}")
                    st.write(f"Warehouse: {conn.current_warehouse}")
                else:
                    st.error("❌ Connection failed")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")
        
        # Date range selector
        date_range = st.date_input(
            "Select Date Range",
            value=(pd.Timestamp.now() - pd.Timedelta(days=30), pd.Timestamp.now()),
            help="Select the date range for analysis"
        )
        
        # Region filter
        regions = ["All", "North", "South", "East", "West", "Central"]
        selected_region = st.selectbox("Region", regions)
        
        # Refresh data button
        refresh_data = st.button("🔄 Refresh Data")
    
    # Main content area
    col1, col2, col3, col4 = st.columns(4)
    
    # Key Metrics
    with col1:
        display_metric("Total Revenue", "$2.4M", "12%")
    
    with col2:
        display_metric("Orders", "1,234", "8%")
    
    with col3:
        display_metric("Customers", "856", "15%")
    
    with col4:
        display_metric("Avg. Order", "$1,943", "-3%")
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trend")
        # Generate sample data for demonstration
        sample_data = generate_sample_data(30)
        create_line_chart(
            sample_data, 
            "date", 
            "revenue",
            title="Daily Revenue"
        )
    
    with col2:
        st.subheader("🥧 Sales by Region")
        # Generate sample regional data
        regional_data = pd.DataFrame({
            'region': ['North', 'South', 'East', 'West', 'Central'],
            'sales': [450000, 380000, 520000, 290000, 360000]
        })
        create_pie_chart(
            regional_data,
            "region",
            "sales", 
            title="Regional Sales Distribution"
        )
    
    st.markdown("---")
    
    # Data table section
    st.subheader("📋 Recent Orders")
    
    # Sample orders data
    orders_data = pd.DataFrame({
        'Order ID': [f'ORD-{1000+i}' for i in range(10)],
        'Customer': [f'Customer {i+1}' for i in range(10)],
        'Product': ['Product A', 'Product B', 'Product C'] * 3 + ['Product A'],
        'Amount': np.random.uniform(100, 5000, 10).round(2),
        'Date': pd.date_range('2024-01-01', periods=10, freq='D'),
        'Status': np.random.choice(['Completed', 'Processing', 'Shipped'], 10)
    })
    
    display_dataframe(
        orders_data,
        height=300,
        use_container_width=True
    )
    
    # Advanced analytics section
    st.markdown("---")
    st.subheader("🔍 Advanced Analytics")
    
    # Create tabs for different analysis views
    tab1, tab2, tab3 = st.tabs(["Customer Analysis", "Product Performance", "Trends"])
    
    with tab1:
        st.write("Customer segmentation and lifetime value analysis")
        # Customer data
        customer_data = generate_customer_data(100)
        create_scatter_plot(
            customer_data,
            "total_orders",
            "total_spent",
            title="Customer Value Analysis"
        )
    
    with tab2:
        st.write("Product sales performance and inventory insights")
        # Product performance data
        product_data = pd.DataFrame({
            'product': [f'Product {chr(65+i)}' for i in range(8)],
            'units_sold': np.random.randint(50, 500, 8),
            'revenue': np.random.uniform(1000, 10000, 8).round(2),
            'profit_margin': np.random.uniform(0.1, 0.4, 8).round(3)
        })
        
        col1, col2 = st.columns(2)
        with col1:
            create_bar_chart(
                product_data,
                "product",
                "units_sold",
                title="Units Sold by Product"
            )
        
        with col2:
            create_bar_chart(
                product_data,
                "product", 
                "revenue",
                title="Revenue by Product"
            )
    
    with tab3:
        st.write("Sales trends and forecasting")
        # Trend analysis
        trend_data = generate_trend_data(90)
        create_area_chart(
            trend_data,
            "date",
            "cumulative_sales",
            title="Cumulative Sales Trend"
        )
        
        # Show trend metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("90-Day Growth", "23.5%", "2.1%")
        with col2:
            st.metric("Monthly Average", "$185K", "5.2%")
        with col3:
            st.metric("Forecast Next Month", "$225K", "12.8%")

if __name__ == "__main__":
    main() 