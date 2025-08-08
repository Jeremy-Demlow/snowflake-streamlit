import streamlit as st
import sys
from pathlib import Path

# Add shared utilities to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from shared.common import snowflake_utils, ui_components

st.set_page_config(
    page_title="Finance Dashboard - Details",
    page_icon="📊",
    layout="wide"
)

st.title("Details Page")

st.write("This is a sample details page for the finance_dashboard application.")

# Example of using shared utilities
if st.button("Test Connection"):
    if snowflake_utils.test_connection():
        ui_components.create_alert("Connection successful!", "success")
    else:
        ui_components.create_alert("Connection failed!", "error")

# Example data display
st.subheader("Sample Data")
sample_data = {
    "Metric": ["Revenue", "Users", "Sessions"],
    "Value": [100000, 5000, 15000]
}

import pandas as pd
df = pd.DataFrame(sample_data)
ui_components.create_data_table(df, "Sample Metrics")
