import streamlit as st
from snowflake.snowpark.context import get_active_session

# Simple local imports - no path manipulation needed
from common.snowflake_utils import get_active_session_connection
from common.ui_components import create_alert

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
        # Try the enhanced connection first, then fallback
        try:
            conn = get_active_session_connection()
            if conn.test_connection():
                create_alert("Successfully connected to Snowflake!", "success")
                st.write(f"**Database:** {conn.current_database}")
                st.write(f"**Schema:** {conn.current_schema}")
                st.write(f"**Warehouse:** {conn.current_warehouse}")
            else:
                create_alert("Connection test failed", "error")
        except:
            # Fallback to direct session
            session = get_active_session()
            create_alert("Successfully connected to Snowflake!", "success")
            st.write(f"**Database:** {session.get_current_database()}")
            st.write(f"**Schema:** {session.get_current_schema()}")
            st.write(f"**Warehouse:** {session.get_current_warehouse()}")
            
    except Exception as e:
        create_alert(f"Connection error: {str(e)}", "error")

# Some sample content
st.subheader("Sample Data Analysis")
st.write("This page could contain detailed customer analysis, drill-down views, or specific customer profiles.")
