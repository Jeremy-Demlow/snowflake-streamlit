#!/usr/bin/env python3
"""
App creation wizard for Streamlit applications.

This script creates new Streamlit app structures with proper
configuration files and templates.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import yaml
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AppCreator:
    """Creates new Streamlit application structures."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.apps_dir = project_root / "apps"
        self.templates_dir = project_root / "templates"
        
    def create_app_directory(self, app_name: str) -> Path:
        """Create the app directory structure."""
        app_dir = self.apps_dir / app_name
        
        if app_dir.exists():
            raise ValueError(f"App directory already exists: {app_dir}")
            
        # Create directory structure
        directories = [
            app_dir,
            app_dir / "pages",
            app_dir / "config",
            app_dir / "tests"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
            
        return app_dir
    
    def create_snowflake_config(self, app_dir: Path, app_name: str, 
                               template: str = "basic") -> None:
        """Create snowflake.yml configuration file."""
        
        config = {
            'definition_version': '2',
            'entities': {
                f'{app_name}_app': {
                    'type': 'streamlit',
                    'identifier': {
                        'name': f'{app_name}_app'
                    },
                    'main_file': 'streamlit_app.py',
                    'pages_dir': 'pages',
                    'query_warehouse': 'COMPUTE_WH',
                    'stage': 'streamlit',
                    'artifacts': [
                        'streamlit_app.py',
                        'environment.yml',
                        'pages/',
                        'config/',
                        '../../shared/'  # Include shared utilities
                    ]
                }
            }
        }
        
        config_file = app_dir / "snowflake.yml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
            
        logger.info(f"Created Snowflake config: {config_file}")
    
    def create_environment_config(self, app_dir: Path, template: str = "basic") -> None:
        """Create environment.yml file."""
        
        base_deps = [
            'streamlit>=1.28.0',
            'snowflake-snowpark-python>=1.11.0',
            'pandas>=2.0.0',
            'plotly>=5.0.0'
        ]
        
        # Add template-specific dependencies
        template_deps = {
            'basic': [],
            'analytics': [
                'numpy>=1.24.0',
                'scipy>=1.11.0',
                'scikit-learn>=1.3.0'
            ],
            'dashboard': [
                'altair>=5.0.0',
                'seaborn>=0.12.0',
                'matplotlib-base>=3.7.0'
            ],
            'ml': [
                'numpy>=1.24.0',
                'scipy>=1.11.0',
                'scikit-learn>=1.3.0',
                'joblib>=1.3.0'
            ]
        }
        
        dependencies = base_deps + template_deps.get(template, [])
        
        config = {
            'name': f'streamlit_{app_dir.name}_env',
            'channels': ['snowflake', 'conda-forge', 'defaults'],
            'dependencies': dependencies
        }
        
        env_file = app_dir / "environment.yml"
        with open(env_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
            
        logger.info(f"Created environment config: {env_file}")
    
    def create_main_app(self, app_dir: Path, app_name: str, template: str = "basic") -> None:
        """Create the main streamlit_app.py file."""
        
        templates = {
            'basic': self._get_basic_template(app_name),
            'analytics': self._get_analytics_template(app_name),
            'dashboard': self._get_dashboard_template(app_name),
            'ml': self._get_ml_template(app_name)
        }
        
        content = templates.get(template, templates['basic'])
        
        app_file = app_dir / "streamlit_app.py"
        with open(app_file, 'w') as f:
            f.write(content)
            
        logger.info(f"Created main app file: {app_file}")
    
    def create_sample_page(self, app_dir: Path, app_name: str) -> None:
        """Create a sample page."""
        
        content = f'''import streamlit as st
import sys
from pathlib import Path

# Add shared utilities to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from shared.common import snowflake_utils, ui_components

st.set_page_config(
    page_title="{app_name.replace('_', ' ').title()} - Details",
    page_icon="📊",
    layout="wide"
)

st.title("Details Page")

st.write("This is a sample details page for the {app_name} application.")

# Example of using shared utilities
if st.button("Test Connection"):
    if snowflake_utils.test_connection():
        ui_components.create_alert("Connection successful!", "success")
    else:
        ui_components.create_alert("Connection failed!", "error")

# Example data display
st.subheader("Sample Data")
sample_data = {{
    "Metric": ["Revenue", "Users", "Sessions"],
    "Value": [100000, 5000, 15000]
}}

import pandas as pd
df = pd.DataFrame(sample_data)
ui_components.create_data_table(df, "Sample Metrics")
'''
        
        page_file = app_dir / "pages" / "details.py"
        with open(page_file, 'w') as f:
            f.write(content)
            
        logger.info(f"Created sample page: {page_file}")
    
    def create_config_file(self, app_dir: Path, app_name: str) -> None:
        """Create app configuration file."""
        
        content = f'''"""
Configuration for {app_name} application.
"""

# App metadata
APP_NAME = "{app_name}"
APP_TITLE = "{app_name.replace('_', ' ').title()}"
APP_DESCRIPTION = "A Streamlit application for {app_name.replace('_', ' ')}"

# Database configuration
DEFAULT_WAREHOUSE = "COMPUTE_WH"
DEFAULT_DATABASE = "STREAMLIT"
DEFAULT_SCHEMA = "PUBLIC"

# UI configuration
PAGE_CONFIG = {{
    "page_title": APP_TITLE,
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}}

# Feature flags
ENABLE_CACHING = True
ENABLE_METRICS = True
ENABLE_EXPORT = True

# Chart configuration
DEFAULT_CHART_HEIGHT = 400
DEFAULT_TABLE_HEIGHT = 300
'''
        
        config_file = app_dir / "config" / "config.py"
        with open(config_file, 'w') as f:
            f.write(content)
            
        logger.info(f"Created config file: {config_file}")
    
    def create_readme(self, app_dir: Path, app_name: str, template: str) -> None:
        """Create README file for the app."""
        
        content = f'''# {app_name.replace('_', ' ').title()}

A Streamlit application built with the {template} template.

## Description

This application provides [describe your app's purpose here].

## Features

- Feature 1
- Feature 2
- Feature 3

## Usage

### Local Development

1. Navigate to the app directory:
   ```bash
   cd apps/{app_name}
   ```

2. Install dependencies:
   ```bash
   conda env create -f environment.yml
   conda activate streamlit_{app_name}_env
   ```

3. Run locally:
   ```bash
   streamlit run streamlit_app.py
   ```

### Deployment

Deploy to Snowflake using the deployment script:

```bash
# From project root
python scripts/deploy.py --app {app_name}
```

## Configuration

App-specific configuration can be found in `config/config.py`.

## Pages

- **Main**: Overview and primary functionality
- **Details**: Detailed views and analysis

## Dependencies

See `environment.yml` for the complete list of dependencies.

## Development

### Adding New Pages

1. Create a new Python file in the `pages/` directory
2. Follow the naming convention: `page_name.py`
3. Import shared utilities from the project root

### Modifying Configuration

Update `config/config.py` to modify app settings and feature flags.

## Support

For issues or questions, please refer to the main project documentation.
'''
        
        readme_file = app_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(content)
            
        logger.info(f"Created README: {readme_file}")
    
    def create_test_file(self, app_dir: Path, app_name: str) -> None:
        """Create a basic test file."""
        
        content = f'''"""
Tests for {app_name} application.
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
        pytest.fail(f"Failed to import streamlit_app: {{e}}")

def test_config_imports():
    """Test that config can be imported."""
    try:
        from config import config
        assert config.APP_NAME == "{app_name}"
    except ImportError as e:
        pytest.fail(f"Failed to import config: {{e}}")

def test_shared_utilities():
    """Test that shared utilities can be imported."""
    try:
        from shared.common import snowflake_utils, ui_components
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import shared utilities: {{e}}")

# Add more specific tests here as needed
'''
        
        test_file = app_dir / "tests" / f"test_{app_name}.py"
        with open(test_file, 'w') as f:
            f.write(content)
            
        logger.info(f"Created test file: {test_file}")
    
    def _get_basic_template(self, app_name: str) -> str:
        """Get basic app template."""
        return f'''import streamlit as st
import sys
from pathlib import Path

# Add shared utilities to path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

# Import shared utilities
from shared.common import snowflake_utils, ui_components, data_utils

# Import app configuration
from config.config import PAGE_CONFIG, APP_TITLE, APP_DESCRIPTION

# Configure the page
st.set_page_config(**PAGE_CONFIG)

def main():
    """Main application function."""
    st.title(APP_TITLE)
    st.write(APP_DESCRIPTION)
    
    # Test connection
    with st.sidebar:
        st.header("Connection Status")
        if snowflake_utils.test_connection():
            ui_components.create_alert("✅ Connected to Snowflake", "success")
        else:
            ui_components.create_alert("❌ Connection failed", "error")
            
    # Main content
    st.header("Welcome!")
    st.write("This is your new Streamlit application.")
    
    # Sample metrics
    sample_metrics = {{
        "total_records": 1000,
        "active_users": 250,
        "daily_sessions": 500
    }}
    
    ui_components.display_metrics(sample_metrics)
    
    # Sample data section
    with st.expander("Sample Data"):
        query = "SELECT 1 as id, 'Sample' as name, 100 as value"
        try:
            df = data_utils.load_data(query)
            ui_components.create_data_table(df, "Sample Data")
        except Exception as e:
            st.error(f"Error loading data: {{e}}")

if __name__ == "__main__":
    main()
'''
    
    def _get_analytics_template(self, app_name: str) -> str:
        """Get analytics app template."""
        return f'''import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add shared utilities to path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from shared.common import snowflake_utils, ui_components, data_utils
from config.config import PAGE_CONFIG, APP_TITLE

st.set_page_config(**PAGE_CONFIG)

def main():
    """Analytics application."""
    st.title(APP_TITLE)
    st.write("Analytics Dashboard")
    
    # Filters
    with st.sidebar:
        st.header("Filters")
        date_range = st.date_input("Select Date Range", value=[])
        metric_type = st.selectbox("Metric Type", ["Revenue", "Users", "Sessions"])
    
    # Analytics content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Key Metrics")
        metrics = {{
            "total_revenue": 150000,
            "avg_user_value": 75.50,
            "conversion_rate": 0.125
        }}
        ui_components.display_metrics(metrics)
    
    with col2:
        st.subheader("Trends")
        # Sample trend data
        dates = pd.date_range("2024-01-01", periods=30, freq="D")
        values = np.random.randint(100, 1000, 30)
        trend_df = pd.DataFrame({{"date": dates, "value": values}})
        ui_components.create_line_chart(trend_df, "date", "value", "Daily Trend")

if __name__ == "__main__":
    main()
'''
    
    def _get_dashboard_template(self, app_name: str) -> str:
        """Get dashboard app template."""
        return f'''import streamlit as st
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
            chart_data = pd.DataFrame({{
                "Category": ["A", "B", "C", "D"],
                "Value": [100, 200, 150, 300]
            }})
            ui_components.create_bar_chart(chart_data, "Category", "Value", "Sales by Category")
        
        with col2:
            # Sample pie chart
            ui_components.create_pie_chart(chart_data, "Category", "Value", "Category Distribution")
    
    with tab3:
        st.header("Data Explorer")
        
        # Sample data table
        sample_data = pd.DataFrame({{
            "ID": range(1, 11),
            "Product": [f"Product {{i}}" for i in range(1, 11)],
            "Sales": np.random.randint(100, 1000, 10),
            "Region": np.random.choice(["North", "South", "East", "West"], 10)
        }})
        
        ui_components.create_data_table(sample_data, "Sample Sales Data")

if __name__ == "__main__":
    main()
'''
    
    def _get_ml_template(self, app_name: str) -> str:
        """Get ML app template."""
        return f'''import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from shared.common import snowflake_utils, ui_components, data_utils
from config.config import PAGE_CONFIG, APP_TITLE

st.set_page_config(**PAGE_CONFIG)

def main():
    """ML application."""
    st.title(APP_TITLE)
    st.write("Machine Learning Dashboard")
    
    # Model selection
    with st.sidebar:
        st.header("Model Configuration")
        model_type = st.selectbox("Model Type", ["Linear Regression", "Random Forest", "XGBoost"])
        test_size = st.slider("Test Size", 0.1, 0.5, 0.2)
    
    # ML workflow
    tab1, tab2, tab3 = st.tabs(["Data", "Training", "Predictions"])
    
    with tab1:
        st.header("Dataset")
        st.write("Load and explore your dataset here.")
        
        # Sample dataset
        n_samples = st.number_input("Number of samples", 100, 10000, 1000)
        if st.button("Generate Sample Data"):
            data = {{
                "feature_1": np.random.randn(n_samples),
                "feature_2": np.random.randn(n_samples),
                "target": np.random.randn(n_samples)
            }}
            df = pd.DataFrame(data)
            ui_components.create_data_table(df.head(20), "Sample Data")
    
    with tab2:
        st.header("Model Training")
        st.write(f"Training {{model_type}} with test size {{test_size}}")
        
        if st.button("Train Model"):
            with st.spinner("Training model..."):
                # Simulate training
                import time
                time.sleep(2)
                
                # Display training results
                metrics = {{
                    "accuracy": 0.85,
                    "precision": 0.82,
                    "recall": 0.88,
                    "f1_score": 0.85
                }}
                ui_components.display_metrics(metrics)
    
    with tab3:
        st.header("Predictions")
        st.write("Make predictions with your trained model.")
        
        col1, col2 = st.columns(2)
        with col1:
            feature_1 = st.number_input("Feature 1", -3.0, 3.0, 0.0)
            feature_2 = st.number_input("Feature 2", -3.0, 3.0, 0.0)
        
        with col2:
            if st.button("Predict"):
                # Simulate prediction
                prediction = np.random.randn()
                st.metric("Prediction", f"{{prediction:.3f}}")

if __name__ == "__main__":
    main()
'''
    
    def create_app(self, app_name: str, template: str = "basic", 
                  description: str = "") -> None:
        """Create a complete app structure."""
        
        logger.info(f"Creating app: {app_name} with template: {template}")
        
        # Validate app name
        if not app_name.replace('_', '').isalnum():
            raise ValueError("App name must contain only letters, numbers, and underscores")
        
        # Create directory structure
        app_dir = self.create_app_directory(app_name)
        
        # Create all files
        self.create_snowflake_config(app_dir, app_name, template)
        self.create_environment_config(app_dir, template)
        self.create_main_app(app_dir, app_name, template)
        self.create_sample_page(app_dir, app_name)
        self.create_config_file(app_dir, app_name)
        self.create_readme(app_dir, app_name, template)
        self.create_test_file(app_dir, app_name)
        
        logger.info(f"Successfully created app: {app_name}")
        logger.info(f"App directory: {app_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Create new Streamlit applications"
    )
    
    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name of the app to create"
    )
    
    parser.add_argument(
        "--template",
        type=str,
        choices=["basic", "analytics", "dashboard", "ml"],
        default="basic",
        help="Template to use for the app"
    )
    
    parser.add_argument(
        "--description",
        type=str,
        default="",
        help="Description of the app"
    )
    
    args = parser.parse_args()
    
    # Initialize creator
    creator = AppCreator(
        project_root=Path(__file__).parent.parent
    )
    
    try:
        creator.create_app(args.name, args.template, args.description)
        print(f"Successfully created app: {args.name}")
        print(f"To deploy: python scripts/deploy.py --app {args.name}")
        
    except Exception as e:
        logger.error(f"Failed to create app: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 