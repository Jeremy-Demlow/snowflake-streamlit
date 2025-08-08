"""
Customer Analytics - Self-contained Streamlit app with local utilities
"""
import streamlit as st
import pandas as pd
import numpy as np
from snowflake.snowpark.context import get_active_session

# Simple local imports - no path manipulation needed
from common.snowflake_utils import get_active_session_connection
from common.ui_components import display_metric, create_line_chart, create_pie_chart, display_dataframe, create_scatter_plot, create_bar_chart
from common.data_utils import generate_customer_data

st.set_page_config(
    page_title="Customer Analytics",
    page_icon="👥",
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
    """Customer Analytics Application"""
    st.title("👥 Customer Analytics")
    st.markdown("Customer segmentation and lifetime value analysis")
    
    # Sidebar
    with st.sidebar:
        st.header("Analytics Controls")
        
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
            "Analysis Period",
            value=(pd.Timestamp.now() - pd.Timedelta(days=90), pd.Timestamp.now())
        )
        
        segments = ["All", "Premium", "Standard", "Basic", "New"]
        selected_segment = st.selectbox("Customer Segment", segments)
        
        if st.button("🔄 Refresh Analysis"):
            st.rerun()
    
    # Key customer metrics using nice utility functions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_metric("Total Customers", "12,540", "8%")
    with col2:
        display_metric("New Customers", "189", "15%")
    with col3:
        display_metric("Retention Rate", "92.3%", "2.1%")
    with col4:
        display_metric("Avg LTV", "$1,251", "5%")
    
    st.markdown("---")
    
    # Customer analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Segmentation", "Lifetime Value", "Retention", "Acquisition"])
    
    with tab1:
        st.subheader("Customer Segmentation Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            segment_data = pd.DataFrame({
                'segment': ['Premium', 'Standard', 'Basic', 'New'],
                'customers': [1250, 4560, 5890, 840]
            })
            create_pie_chart(segment_data, "segment", "customers", "Customer Distribution")
        
        with col2:
            revenue_data = pd.DataFrame({
                'segment': ['Premium', 'Standard', 'Basic', 'New'],
                'avg_revenue': [850, 420, 180, 125]
            })
            create_bar_chart(revenue_data, "segment", "avg_revenue", "Average Revenue by Segment")
    
    with tab2:
        st.subheader("Customer Lifetime Value Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ltv_data = generate_customer_data(500)
            create_scatter_plot(ltv_data, "total_orders", "total_spent", "Customer Value Distribution")
        
        with col2:
            tenure_data = pd.DataFrame({
                'tenure_months': ['0-6', '6-12', '12-24', '24+'],
                'avg_ltv': [245, 580, 1250, 2100]
            })
            create_bar_chart(tenure_data, "tenure_months", "avg_ltv", "LTV by Customer Tenure")
    
    with tab3:
        st.subheader("Customer Retention Analysis")
        
        # Retention cohort
        cohort_data = pd.DataFrame({
            'month': pd.date_range('2024-01-01', periods=12, freq='M'),
            'retention_rate': [100, 85, 78, 72, 68, 65, 62, 60, 58, 56, 55, 54]
        })
        create_line_chart(cohort_data, "month", "retention_rate", "12-Month Retention Cohort")
        
        # Churn risk analysis
        st.subheader("Churn Risk Analysis")
        
        churn_data = pd.DataFrame({
            'risk_level': ['Low', 'Medium', 'High', 'Critical'],
            'customers': [8500, 2800, 950, 290],
            'churn_probability': [5, 25, 65, 85]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            create_bar_chart(churn_data, "risk_level", "customers", "Customers by Churn Risk")
        
        with col2:
            display_dataframe(churn_data, height=200, use_container_width=True)
    
    with tab4:
        st.subheader("Customer Acquisition Analysis")
        
        # Acquisition channels
        acquisition_data = pd.DataFrame({
            'channel': ['Organic Search', 'Paid Ads', 'Social Media', 'Email', 'Referral'],
            'customers': [3200, 2800, 1500, 1200, 800],
            'cost_per_acquisition': [45, 120, 85, 25, 15]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            create_pie_chart(acquisition_data, "channel", "customers", "Customer Acquisition by Channel")
        
        with col2:
            create_bar_chart(acquisition_data, "channel", "cost_per_acquisition", "Cost per Acquisition")
        
        # Monthly acquisition trend
        st.subheader("Acquisition Trend")
        
        trend_data = pd.DataFrame({
            'month': pd.date_range('2024-01-01', periods=12, freq='M'),
            'new_customers': np.random.randint(150, 250, 12)
        })
        create_line_chart(trend_data, "month", "new_customers", "Monthly New Customer Acquisition")

if __name__ == "__main__":
    main()
