import streamlit as st
import sys
from pathlib import Path

# Add repo root to path for shared imports
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

# Direct imports from specific modules (no __init__.py dependency)
from shared.common.snowflake_utils import get_connection, get_active_session_connection
from shared.common.ui_components import create_alert

st.set_page_config(
    page_title="Customer Analytics - Details",
    page_icon="📊",
    layout="wide"
)

st.title("Details Page")

st.write("This is a sample details page for the customer_analytics application.")

# Test connection functionality
if st.button("Test Connection"):
    try:
        # Try SIS environment first, then local
        try:
            conn = get_active_session_connection()
        except:
            conn = get_connection("streamlit_env")
            
        if conn.test_connection():
            create_alert("Successfully connected to Snowflake!", "success")
            st.write(f"**Database:** {conn.current_database}")
            st.write(f"**Schema:** {conn.current_schema}")
            st.write(f"**Warehouse:** {conn.current_warehouse}")
        else:
            create_alert("Connection test failed", "error")
    except Exception as e:
        create_alert(f"Connection error: {str(e)}", "error")

# Some sample content
st.subheader("Sample Data Analysis")
st.write("This page could contain detailed customer analysis, drill-down views, or specific customer profiles.")
