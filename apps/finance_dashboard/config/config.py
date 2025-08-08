"""
Configuration for finance_dashboard application.
"""

# App metadata
APP_NAME = "finance_dashboard"
APP_TITLE = "Finance Dashboard"
APP_DESCRIPTION = "A Streamlit application for finance dashboard"

# Database configuration
DEFAULT_WAREHOUSE = "COMPUTE_WH"
DEFAULT_DATABASE = "STREAMLIT"
DEFAULT_SCHEMA = "PUBLIC"

# UI configuration
PAGE_CONFIG = {
    "page_title": APP_TITLE,
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Feature flags
ENABLE_CACHING = True
ENABLE_METRICS = True
ENABLE_EXPORT = True

# Chart configuration
DEFAULT_CHART_HEIGHT = 400
DEFAULT_TABLE_HEIGHT = 300
