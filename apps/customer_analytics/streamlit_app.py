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
from shared.common.ui_components import display_metric, create_line_chart, create_pie_chart, display_dataframe, create_scatter_plot, create_bar_chart
from shared.common.data_utils import generate_customer_data

st.set_page_config(
    page_title="Customer Analytics",
    page_icon="👥",
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
    """Customer Analytics Application."""
    st.title("👥 Customer Analytics")
    st.markdown("---")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Analytics Controls")
        
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
            "Analysis Period",
            value=(pd.Timestamp.now() - pd.Timedelta(days=90), pd.Timestamp.now()),
            help="Select the period for customer analysis"
        )
        
        # Customer segment filter
        segments = ["All", "Premium", "Standard", "Basic", "New"]
        selected_segment = st.selectbox("Customer Segment", segments)
        
        # Refresh data button
        refresh_data = st.button("🔄 Refresh Analysis")
    
    # Key customer metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_metric("Total Customers", "12,540", "8%")
    
    with col2:
        display_metric("New Customers", "189", "15%")
    
    with col3:
        display_metric("Retention Rate", "92.3%", "2.1%")
    
    with col4:
        display_metric("Avg. LTV", "$1,251", "5%")
    
    st.markdown("---")
    
    # Customer analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Segmentation", "Lifetime Value", "Retention", "Acquisition"])
    
    with tab1:
        st.subheader("Customer Segmentation Analysis")
        
        # Segment distribution
        col1, col2 = st.columns(2)
        
        with col1:
            segment_data = pd.DataFrame({
                'segment': ['Premium', 'Standard', 'Basic', 'New'],
                'customers': [1250, 4560, 5890, 840],
                'percentage': [10.0, 36.4, 46.9, 6.7]
            })
            
            create_pie_chart(
                segment_data,
                "segment",
                "customers",
                title="Customer Distribution by Segment"
            )
        
        with col2:
            # Revenue by segment
            revenue_data = pd.DataFrame({
                'segment': ['Premium', 'Standard', 'Basic', 'New'],
                'avg_revenue': [850, 420, 180, 125]
            })
            
            create_bar_chart(
                revenue_data,
                "segment",
                "avg_revenue",
                title="Average Revenue by Segment"
            )
    
    with tab2:
        st.subheader("Customer Lifetime Value Analysis")
        
        # LTV distribution
        ltv_data = generate_customer_data(500)
        
        col1, col2 = st.columns(2)
        
        with col1:
            create_scatter_plot(
                ltv_data,
                "total_orders",
                "total_spent",
                title="Customer Value Distribution"
            )
        
        with col2:
            # LTV by tenure
            tenure_data = pd.DataFrame({
                'tenure_months': ['0-6', '6-12', '12-24', '24+'],
                'avg_ltv': [245, 580, 1250, 2100]
            })
            
            create_bar_chart(
                tenure_data,
                "tenure_months",
                "avg_ltv",
                title="LTV by Customer Tenure"
            )
    
    with tab3:
        st.subheader("Customer Retention Analysis")
        
        # Retention cohort
        cohort_data = pd.DataFrame({
            'month': pd.date_range('2024-01-01', periods=12, freq='M'),
            'retention_rate': [100, 85, 78, 72, 68, 65, 62, 60, 58, 56, 55, 54]
        })
        
        create_line_chart(
            cohort_data,
            "month",
            "retention_rate",
            title="12-Month Retention Cohort"
        )
        
        # Churn risk analysis
        st.subheader("Churn Risk Analysis")
        
        churn_data = pd.DataFrame({
            'risk_level': ['Low', 'Medium', 'High', 'Critical'],
            'customers': [8500, 2800, 950, 290],
            'churn_probability': [5, 25, 65, 85]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            create_bar_chart(
                churn_data,
                "risk_level",
                "customers",
                title="Customers by Churn Risk"
            )
        
        with col2:
            display_dataframe(
                churn_data,
                height=200,
                use_container_width=True
            )
    
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
            create_pie_chart(
                acquisition_data,
                "channel",
                "customers",
                title="Customer Acquisition by Channel"
            )
        
        with col2:
            create_bar_chart(
                acquisition_data,
                "channel",
                "cost_per_acquisition",
                title="Cost per Acquisition by Channel"
            )
        
        # Monthly acquisition trend
        st.subheader("Acquisition Trend")
        
        trend_data = pd.DataFrame({
            'month': pd.date_range('2024-01-01', periods=12, freq='M'),
            'new_customers': np.random.randint(150, 250, 12),
            'acquisition_cost': np.random.randint(8000, 15000, 12)
        })
        
        create_line_chart(
            trend_data,
            "month",
            "new_customers",
            title="Monthly New Customer Acquisition"
        )

if __name__ == "__main__":
    main()
