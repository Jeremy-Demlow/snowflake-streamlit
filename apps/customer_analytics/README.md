# Customer Analytics

A Streamlit application built with the dashboard template.

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
   cd apps/customer_analytics
   ```

2. Install dependencies:
   ```bash
   conda env create -f environment.yml
   conda activate streamlit_customer_analytics_env
   ```

3. Run locally:
   ```bash
   streamlit run streamlit_app.py
   ```

### Deployment

Deploy to Snowflake using the deployment script:

```bash
# From project root
python scripts/deploy.py --app customer_analytics
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
