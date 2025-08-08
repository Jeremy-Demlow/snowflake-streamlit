"""
Sales Dashboard - Self-contained Streamlit app with local utilities
"""
import streamlit as st
import pandas as pd
import numpy as np
from snowflake.snowpark.context import get_active_session

# Simple local imports - no path manipulation needed
from common.snowflake_utils import get_active_session_connection
from common.ui_components import display_metric, create_line_chart, create_pie_chart, display_dataframe
from common.data_utils import generate_sample_data

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_snowflake_connection():
    """Get Snowflake connection - works in SIS"""
    try:
        return get_active_session_connection()
    except:
        # Fallback for local development would go here
        return get_active_session()

def main():
    """Sales Dashboard Application"""
    st.title("📊 Sales Dashboard")
    st.markdown("Real-time sales analytics and performance metrics")
    
    # Sidebar
    with st.sidebar:
        st.header("Dashboard Controls")
        
        # Connection test
        if st.button("Test Connection"):
            try:
                conn = get_snowflake_connection()
                if hasattr(conn, 'test_connection') and conn.test_connection():
                    st.success("✅ Connected to Snowflake!")
                    st.write(f"**Database:** {conn.current_database}")
                    st.write(f"**Schema:** {conn.current_schema}")
                    st.write(f"**Warehouse:** {conn.current_warehouse}")
                else:
                    # Direct session test
                    session = get_active_session()
                    st.success("✅ Connected to Snowflake!")
                    st.write(f"**Database:** {session.get_current_database()}")
                    st.write(f"**Schema:** {session.get_current_schema()}")
                    st.write(f"**Warehouse:** {session.get_current_warehouse()}")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")
        
        # Filters
        date_range = st.date_input(
            "Date Range",
            value=(pd.Timestamp.now() - pd.Timedelta(days=30), pd.Timestamp.now())
        )
        
        regions = ["All", "North", "South", "East", "West", "Central"]
        selected_region = st.selectbox("Region", regions)
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Main metrics using nice utility functions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_metric("Total Revenue", "$2.4M", "12%")
    with col2:
        display_metric("Orders", "1,234", "8%")
    with col3:
        display_metric("Customers", "856", "15%")
    with col4:
        display_metric("Avg Order", "$1,943", "-3%")
    
    st.markdown("---")
    
    # Charts using nice utility functions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Revenue Trend")
        sample_data = generate_sample_data(30)
        create_line_chart(sample_data, "date", "revenue", "Daily Revenue")
    
    with col2:
        st.subheader("🥧 Sales by Region")
        regional_data = pd.DataFrame({
            'region': ['North', 'South', 'East', 'West', 'Central'],
            'sales': [450000, 380000, 520000, 290000, 360000]
        })
        create_pie_chart(regional_data, "region", "sales", "Regional Sales")
    
    st.markdown("---")
    
    # Data table using nice utility
    st.subheader("📋 Recent Orders")
    orders_data = pd.DataFrame({
        'Order ID': [f'ORD-{1000+i}' for i in range(10)],
        'Customer': [f'Customer {i+1}' for i in range(10)],
        'Product': ['Product A', 'Product B', 'Product C'] * 3 + ['Product A'],
        'Amount': np.random.uniform(100, 5000, 10).round(2),
        'Date': pd.date_range('2024-01-01', periods=10, freq='D'),
        'Status': np.random.choice(['Completed', 'Processing', 'Shipped'], 10)
    })
    
    display_dataframe(orders_data, height=300, use_container_width=True)
    
    # Advanced analytics tabs
    st.markdown("---")
    st.subheader("🔍 Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Performance", "Trends", "Forecasting"])
    
    with tab1:
        st.write("**Performance Metrics**")
        perf_data = generate_sample_data(7)
        create_line_chart(perf_data, "date", "orders", "Weekly Orders")
    
    with tab2:
        st.write("**Sales Trends**")
        trend_data = generate_sample_data(90)
        trend_data['cumulative'] = trend_data['revenue'].cumsum()
        create_line_chart(trend_data, "date", "cumulative", "Cumulative Revenue")
    
    with tab3:
        st.write("**Revenue Forecasting**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("30-Day Forecast", "$2.8M", "16.7%")
        with col2:
            st.metric("Growth Rate", "12.3%", "2.1%")
        with col3:
            st.metric("Confidence", "94%", "1.2%")

if __name__ == "__main__":
    main() 