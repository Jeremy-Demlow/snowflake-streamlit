import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add shared utilities to path  
sys.path.insert(0, str(Path(__file__).parent))

from common import snowflake_utils, ui_components, data_utils

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Sales Dashboard Application."""
    st.title("🚀 Sales Dashboard")
    st.markdown("Real-time sales analytics and performance metrics")
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
            
        # Region filter
        regions = ["All", "North", "South", "East", "West"]
        selected_region = st.selectbox("Region", regions)
        
        # Sales rep filter
        sales_reps = ["All", "John Doe", "Jane Smith", "Bob Johnson", "Alice Brown"]
        selected_rep = st.selectbox("Sales Rep", sales_reps)
        
        # Connection status
        st.divider()
        st.subheader("📡 Connection")
        if snowflake_utils.test_connection():
            ui_components.create_alert("Connected", "success")
            
            # Get warehouse info
            warehouse_info = snowflake_utils.get_warehouse_info()
            st.caption(f"Warehouse: {warehouse_info.get('warehouse', 'Unknown')}")
        else:
            ui_components.create_alert("Disconnected", "error")
    
    # Main dashboard content
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "💰 Revenue", "👥 Customers", "📋 Details"])
    
    with tab1:
        st.header("Key Performance Indicators")
        
        # Sample KPIs - in real app, this would come from Snowflake
        kpis = {
            "total_revenue": 1250000,
            "monthly_growth": 0.125,
            "total_orders": 3456,
            "avg_order_value": 361.45,
            "new_customers": 89,
            "customer_retention": 0.92
        }
        
        # Format KPIs nicely
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Revenue",
                f"${kpis['total_revenue']:,.0f}",
                f"{kpis['monthly_growth']:.1%}"
            )
            st.metric(
                "Total Orders",
                f"{kpis['total_orders']:,}",
                "156"
            )
        
        with col2:
            st.metric(
                "Avg Order Value",
                f"${kpis['avg_order_value']:.2f}",
                "$23.45"
            )
            st.metric(
                "New Customers",
                f"{kpis['new_customers']:,}",
                "12"
            )
        
        with col3:
            st.metric(
                "Customer Retention",
                f"{kpis['customer_retention']:.1%}",
                "2.3%"
            )
            
        # Revenue trend chart
        st.subheader("📈 Revenue Trend (Last 30 Days)")
        
        # Generate sample trend data
        dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
        revenue = np.random.normal(40000, 8000, 30).cumsum()
        trend_data = pd.DataFrame({
            'Date': dates,
            'Daily Revenue': np.abs(np.diff(np.concatenate([[0], revenue])))
        })
        
        ui_components.create_line_chart(
            trend_data, 
            'Date', 
            'Daily Revenue', 
            "Daily Revenue Trend"
        )
    
    with tab2:
        st.header("💰 Revenue Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue by region
            region_data = pd.DataFrame({
                'Region': ['North', 'South', 'East', 'West'],
                'Revenue': [320000, 280000, 410000, 240000]
            })
            
            ui_components.create_bar_chart(
                region_data,
                'Region',
                'Revenue',
                "Revenue by Region"
            )
        
        with col2:
            # Revenue by product category
            category_data = pd.DataFrame({
                'Category': ['Electronics', 'Clothing', 'Home', 'Sports'],
                'Revenue': [450000, 320000, 280000, 200000]
            })
            
            ui_components.create_pie_chart(
                category_data,
                'Category',
                'Revenue',
                "Revenue by Category"
            )
        
        # Monthly revenue table
        st.subheader("Monthly Revenue Breakdown")
        monthly_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Revenue': [180000, 195000, 210000, 225000, 240000, 255000],
            'Orders': [720, 780, 840, 900, 960, 1020],
            'AOV': [250, 250, 250, 250, 250, 250]
        })
        
        ui_components.create_data_table(monthly_data, "Monthly Performance")
        
        # Download button
        ui_components.create_download_button(
            monthly_data,
            "monthly_revenue.csv",
            "📥 Download Monthly Data"
        )
    
    with tab3:
        st.header("👥 Customer Analytics")
        
        # Customer metrics
        customer_metrics = {
            "total_customers": 12540,
            "new_this_month": 189,
            "churn_rate": 0.045,
            "lifetime_value": 1250.75
        }
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Customers", f"{customer_metrics['total_customers']:,}")
        with col2:
            st.metric("New This Month", f"{customer_metrics['new_this_month']:,}")
        with col3:
            st.metric("Churn Rate", f"{customer_metrics['churn_rate']:.1%}")
        with col4:
            st.metric("Avg LTV", f"${customer_metrics['lifetime_value']:.2f}")
        
        # Customer segmentation
        st.subheader("Customer Segmentation")
        
        segment_data = pd.DataFrame({
            'Segment': ['Premium', 'Standard', 'Basic', 'New'],
            'Customers': [1250, 4560, 5890, 840],
            'Avg Revenue': [850, 420, 180, 125]
        })
        
        col1, col2 = st.columns(2)
        with col1:
            ui_components.create_bar_chart(
                segment_data,
                'Segment',
                'Customers',
                "Customers by Segment"
            )
        
        with col2:
            ui_components.create_bar_chart(
                segment_data,
                'Segment',
                'Avg Revenue',
                "Average Revenue by Segment"
            )
    
    with tab4:
        st.header("📋 Detailed Sales Data")
        
        # Generate sample detailed data
        np.random.seed(42)  # For consistent sample data
        n_records = 100
        
        detailed_data = pd.DataFrame({
            'Order ID': [f"ORD-{1000 + i}" for i in range(n_records)],
            'Date': pd.date_range(start='2024-01-01', periods=n_records, freq='D')[:n_records],
            'Customer': [f"Customer {i+1}" for i in range(n_records)],
            'Product': np.random.choice(['Electronics', 'Clothing', 'Home', 'Sports'], n_records),
            'Region': np.random.choice(['North', 'South', 'East', 'West'], n_records),
            'Sales Rep': np.random.choice(['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown'], n_records),
            'Revenue': np.random.normal(350, 150, n_records).round(2),
            'Quantity': np.random.randint(1, 10, n_records)
        })
        
        # Ensure positive revenue
        detailed_data['Revenue'] = np.abs(detailed_data['Revenue'])
        
        # Add filters for the detailed data
        with st.expander("🔍 Filter Detailed Data"):
            filter_cols = ['Product', 'Region', 'Sales Rep']
            filters = ui_components.create_filter_sidebar(detailed_data, filter_cols, "Data Filters")
        
        # Apply filters if any exist
        if 'filters' in locals():
            filtered_data = ui_components.apply_filters(detailed_data, filters)
        else:
            filtered_data = detailed_data
        
        # Display the data
        ui_components.create_data_table(
            filtered_data, 
            f"Sales Details ({len(filtered_data)} records)"
        )
        
        # Show data info
        ui_components.show_data_info(filtered_data)
        
        # Export functionality
        ui_components.create_download_button(
            filtered_data,
            "sales_details.csv",
            "📥 Download Filtered Data"
        )

if __name__ == "__main__":
    main() 