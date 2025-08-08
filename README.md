# Multi-App Streamlit Repository with Snowflake Git Integration

This repository demonstrates how to set up **Snowflake's native git integration** for multiple Streamlit applications. Unlike CLI-based deployments, this approach uses Snowflake's built-in git repository features to deploy apps directly from GitHub branches, enabling true git-based workflows.

## Repository Structure

```
snowflake-streamlit/
├── README.md                           # This file
├── .gitignore                         # Git ignore patterns
├── global_config/                     # Global configuration
│   ├── snowflake.yml                 # Global Snowflake configuration
│   └── shared_environment.yml        # Shared dependencies
├── shared/                            # Shared utilities and components
│   ├── __init__.py
│   ├── common/                        # Common functions
│   │   ├── __init__.py
│   │   ├── snowflake_utils.py        # Snowflake connection utilities
│   │   ├── data_utils.py             # Data processing utilities
│   │   └── ui_components.py          # Reusable UI components
│   └── config/                        # Shared configuration
│       ├── __init__.py
│       └── app_config.py             # Application configuration
├── apps/                              # Individual Streamlit applications
│   ├── sales_dashboard/               # Example app 1
│   │   ├── snowflake.yml             # App-specific Snowflake config
│   │   ├── streamlit_app.py          # Main app file
│   │   ├── environment.yml           # App-specific dependencies
│   │   ├── pages/                    # App pages
│   │   │   ├── overview.py
│   │   │   └── details.py
│   │   ├── config/                   # App configuration
│   │   │   └── config.py
│   │   └── README.md                 # App-specific documentation
│   ├── financial_reports/             # Example app 2
│   │   ├── snowflake.yml
│   │   ├── streamlit_app.py
│   │   ├── environment.yml
│   │   ├── pages/
│   │   └── README.md
│   └── data_explorer/                 # Example app 3
│       ├── snowflake.yml
│       ├── streamlit_app.py
│       ├── environment.yml
│       ├── pages/
│       └── README.md
├── scripts/                           # Deployment and management scripts
│   ├── deploy.py                     # Main deployment script
│   ├── create_app.py                 # App creation wizard
│   ├── sync_from_git.py              # Git sync utilities
│   └── manage_apps.py                # App management utilities
├── docs/                              # Documentation
│   ├── developer_guide.md            # Developer workflow guide
│   ├── deployment_guide.md           # Deployment instructions
│   └── git_workflow.md               # Git branching strategy
└── .github/                          # GitHub workflows (optional)
    └── workflows/
        └── deploy.yml                # CI/CD pipeline
```

## Quick Start

### 1. Initial Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd snowflake-streamlit

# Configure your Snowflake connection (using streamlit_env from your config)
snow configure

# Install dependencies
pip install -r requirements.txt
```

### 2. Create a New App

```bash
# Use the app creation wizard
python scripts/create_app.py --name my_new_app --template basic

# Or manually create the structure
mkdir -p apps/my_new_app/{pages,config}
```

### 3. Deploy an App

```bash
# Deploy a specific app
python scripts/deploy.py --app sales_dashboard --connection streamlit_env

# Deploy all apps
python scripts/deploy.py --all --connection streamlit_env
```

## Development Workflow

### Git Branching Strategy

1. **Main Branch**: Production-ready code
2. **Develop Branch**: Integration branch for features
3. **Feature Branches**: `feature/app-name/feature-description`
4. **Hotfix Branches**: `hotfix/app-name/issue-description`

### Developer Workflow

1. Create feature branch: `git checkout -b feature/sales-dashboard/new-chart`
2. Develop and test locally
3. Create pull request to `develop`
4. After review, merge to `develop`
5. Deploy to staging for testing
6. Merge to `main` for production deployment

## App Management

### Creating a New App

Each app is self-contained but can use shared resources:

```python
# Example app structure
apps/my_app/
├── streamlit_app.py      # Entry point
├── snowflake.yml         # Snowflake configuration
├── environment.yml       # Dependencies
├── pages/               # Multi-page support
├── config/              # App-specific config
└── README.md            # App documentation
```

### Shared Resources

- Common functions in `shared/common/`
- Shared UI components in `shared/common/ui_components.py`
- Database utilities in `shared/common/snowflake_utils.py`

## Configuration Management

### Global Configuration

The `global_config/snowflake.yml` contains shared settings:
- Default warehouse
- Global stage configuration
- Shared artifacts

### App-Specific Configuration

Each app can override global settings in its own `snowflake.yml`:
- App-specific warehouses
- Different databases/schemas
- Custom query tags

## Deployment Options

### 1. Single App Deployment
```bash
python scripts/deploy.py --app sales_dashboard
```

### 2. Bulk Deployment
```bash
python scripts/deploy.py --all
```

### 3. Environment-Specific Deployment
```bash
python scripts/deploy.py --app sales_dashboard --env production
```

## Git Integration with Snowflake

### Current Limitations (as of conversation)
- SSH not supported (HTTPS only)
- Limited branching workflow in Snowflake UI
- Manual pull operations

### Workarounds Implemented
1. **PAT Authentication**: Use Personal Access Token for initial setup
2. **OAuth for Users**: Individual users can authenticate via OAuth
3. **Automated Sync**: Scripts to pull latest changes from git
4. **Branch Management**: Deploy from specific branches

## Best Practices

### 1. App Independence
- Each app should be deployable independently
- Minimize dependencies between apps
- Use shared utilities for common functionality

### 2. Configuration Management
- Environment-specific configurations
- Secure credential management
- Clear documentation of requirements

### 3. Testing Strategy
- Local development with sample data
- Staging environment for integration testing
- Production deployment with monitoring

### 4. Documentation
- App-specific README files
- Clear API documentation for shared utilities
- Deployment runbooks

## Troubleshooting

### Common Issues

1. **Connection Problems**: Check `~/.snowflake/config.toml`
2. **Permission Issues**: Verify role permissions for git repositories
3. **Deployment Failures**: Check warehouse availability and permissions

### Support

- Check the `docs/` directory for detailed guides
- Review app-specific README files
- Contact the development team for access issues

## Contributing

1. Follow the git workflow outlined in `docs/git_workflow.md`
2. Update documentation when adding new features
3. Test your changes in a non-production environment
4. Follow the code style guidelines

---

This repository structure addresses the challenges mentioned in your Slack conversation:
- Support for multiple Streamlit apps
- Proper git integration with Snowflake
- Developer-friendly branching workflows
- Scalable deployment strategies 