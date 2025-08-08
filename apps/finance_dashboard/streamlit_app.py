"""
Finance Dashboard - Self-contained Streamlit app with local utilities
"""
import streamlit as st
import pandas as pd
import numpy as np
from snowflake.snowpark.context import get_active_session

# Simple local imports - no path manipulation needed
from common.snowflake_utils import get_active_session_connection
from common.ui_components import display_metric, create_line_chart, create_bar_chart, create_pie_chart, display_dataframe
from common.data_utils import generate_sample_data

st.set_page_config(
    page_title="Finance Dashboard",
    page_icon="💰",
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
    """Finance Dashboard Application"""
    st.title("💰 Finance Dashboard")
    st.markdown("Financial analytics and performance tracking")
    
    # Sidebar
    with st.sidebar:
        st.header("Financial Controls")
        
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
            "Reporting Period",
            value=(pd.Timestamp.now() - pd.Timedelta(days=30), pd.Timestamp.now())
        )
        
        departments = ["All", "Sales", "Marketing", "Operations", "R&D", "Finance"]
        selected_dept = st.selectbox("Department", departments)
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Key financial metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_metric("Total Revenue", "$3.2M", "15%")
    with col2:
        display_metric("Net Profit", "$485K", "22%")
    with col3:
        display_metric("Operating Margin", "15.2%", "1.8%")
    with col4:
        display_metric("Cash Flow", "$720K", "8%")
    
    st.markdown("---")
    
    # Financial charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Monthly Revenue")
        revenue_data = generate_sample_data(12)
        revenue_data['revenue'] = revenue_data['revenue'] * 10  # Scale up for finance
        create_line_chart(revenue_data, "date", "revenue", "Monthly Revenue Trend")
    
    with col2:
        st.subheader("💼 Department Budgets")
        budget_data = pd.DataFrame({
            'department': ['Sales', 'Marketing', 'Operations', 'R&D', 'Finance'],
            'budget': [850000, 420000, 680000, 320000, 180000]
        })
        create_pie_chart(budget_data, "department", "budget", "Budget Allocation")
    
    st.markdown("---")
    
    # Financial analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["P&L Analysis", "Cash Flow", "Budget vs Actual", "Forecasting"])
    
    with tab1:
        st.subheader("Profit & Loss Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pnl_data = pd.DataFrame({
                'category': ['Revenue', 'COGS', 'Operating Expenses', 'Net Income'],
                'amount': [3200000, -1800000, -915000, 485000]
            })
            create_bar_chart(pnl_data, "category", "amount", "P&L Breakdown")
        
        with col2:
            # Monthly P&L trend
            monthly_pnl = pd.DataFrame({
                'month': pd.date_range('2024-01-01', periods=12, freq='M'),
                'revenue': np.random.normal(320000, 50000, 12),
                'expenses': np.random.normal(-220000, 30000, 12)
            })
            monthly_pnl['net_income'] = monthly_pnl['revenue'] + monthly_pnl['expenses']
            create_line_chart(monthly_pnl, "month", "net_income", "Monthly Net Income")
    
    with tab2:
        st.subheader("Cash Flow Analysis")
        
        # Cash flow data
        cashflow_data = pd.DataFrame({
            'month': pd.date_range('2024-01-01', periods=12, freq='M'),
            'operating_cf': np.random.normal(60000, 15000, 12),
            'investing_cf': np.random.normal(-20000, 10000, 12),
            'financing_cf': np.random.normal(-10000, 5000, 12)
        })
        cashflow_data['net_cf'] = (cashflow_data['operating_cf'] + 
                                   cashflow_data['investing_cf'] + 
                                   cashflow_data['financing_cf'])
        
        create_line_chart(cashflow_data, "month", "net_cf", "Net Cash Flow Trend")
        
        # Cash flow summary
        st.subheader("Cash Flow Summary")
        display_dataframe(cashflow_data, height=300, use_container_width=True)
    
    with tab3:
        st.subheader("Budget vs Actual Performance")
        
        budget_vs_actual = pd.DataFrame({
            'department': ['Sales', 'Marketing', 'Operations', 'R&D', 'Finance'],
            'budget': [850000, 420000, 680000, 320000, 180000],
            'actual': [892000, 398000, 715000, 287000, 165000],
            'variance': [42000, -22000, 35000, -33000, -15000]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            create_bar_chart(budget_vs_actual, "department", "budget", "Budgeted Amounts")
        
        with col2:
            create_bar_chart(budget_vs_actual, "department", "actual", "Actual Spending")
    
    with tab4:
        st.subheader("Financial Forecasting")
        
        # Forecast metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Q4 Revenue Forecast", "$3.8M", "18.8%")
        with col2:
            st.metric("Annual Profit Target", "$2.1M", "25.2%")
        with col3:
            st.metric("ROI Projection", "28.5%", "3.2%")
        
        # Forecast chart
        forecast_data = pd.DataFrame({
            'month': pd.date_range('2024-01-01', periods=18, freq='M'),
            'actual': list(np.random.normal(320000, 50000, 12)) + [None] * 6,
            'forecast': [None] * 12 + list(np.random.normal(380000, 60000, 6))
        })
        
        st.subheader("Revenue Forecast")
        create_line_chart(forecast_data, "month", "actual", "Actual vs Forecast")

if __name__ == "__main__":
    main()
