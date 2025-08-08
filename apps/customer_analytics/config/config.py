"""
Configuration for customer_analytics application.
"""

# App metadata
APP_NAME = "customer_analytics"
APP_TITLE = "Customer Analytics"
APP_DESCRIPTION = "A Streamlit application for customer analytics"

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
