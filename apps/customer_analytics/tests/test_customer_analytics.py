"""
Tests for customer_analytics application.
"""

import pytest
import sys
from pathlib import Path

# Add app directory to path
app_path = Path(__file__).parent.parent
sys.path.insert(0, str(app_path))

# Add shared utilities to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

def test_app_imports():
    """Test that the app can be imported without errors."""
    try:
        import streamlit_app
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import streamlit_app: {e}")

def test_config_imports():
    """Test that config can be imported."""
    try:
        from config import config
        assert config.APP_NAME == "customer_analytics"
    except ImportError as e:
        pytest.fail(f"Failed to import config: {e}")

def test_shared_utilities():
    """Test that shared utilities can be imported."""
    try:
        from shared.common import snowflake_utils, ui_components
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import shared utilities: {e}")

# Add more specific tests here as needed
