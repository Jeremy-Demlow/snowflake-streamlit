import streamlit as st
import pandas as pd
import sys
from pathlib import Path

shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from shared.common import snowflake_utils, ui_components, data_utils
from config.config import PAGE_CONFIG, APP_TITLE

st.set_page_config(**PAGE_CONFIG)

def main():
    """Dashboard application."""
    st.title(APP_TITLE)
    
    # Dashboard layout
    tab1, tab2, tab3 = st.tabs(["Overview", "Charts", "Data"])
    
    with tab1:
        st.header("Overview")
        
        # KPI row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Sales", "$1.2M", "12%")
        with col2:
            st.metric("Orders", "1,234", "5%")
        with col3:
            st.metric("Customers", "567", "8%")
        with col4:
            st.metric("Avg Order", "$972", "3%")
    
    with tab2:
        st.header("Charts")
        
        col1, col2 = st.columns(2)
        with col1:
            # Sample bar chart
            chart_data = pd.DataFrame({
                "Category": ["A", "B", "C", "D"],
                "Value": [100, 200, 150, 300]
            })
            ui_components.create_bar_chart(chart_data, "Category", "Value", "Sales by Category")
        
        with col2:
            # Sample pie chart
            ui_components.create_pie_chart(chart_data, "Category", "Value", "Category Distribution")
    
    with tab3:
        st.header("Data Explorer")
        
        # Sample data table
        sample_data = pd.DataFrame({
            "ID": range(1, 11),
            "Product": [f"Product {i}" for i in range(1, 11)],
            "Sales": np.random.randint(100, 1000, 10),
            "Region": np.random.choice(["North", "South", "East", "West"], 10)
        })
        
        ui_components.create_data_table(sample_data, "Sample Sales Data")

if __name__ == "__main__":
    main()
