# REPO UNDER DEVELOPMENT IT'S STILL IN DRAFT FORM

# Multi-App Streamlit Repository with Snowflake Git Integration

This repository demonstrates how to set up **Snowflake's native git integration** for multiple Streamlit applications. This approach uses Snowflake's built-in git repository features to deploy apps directly from GitHub branches, enabling true git-based workflows with automated CI/CD.

## 🏗️ Repository Structure

```
snowflake-streamlit/
├── README.md                           # This file
├── .gitignore                         # Comprehensive git ignore patterns
├── requirements.txt                   # Core Python dependencies
├── apps/                              # Individual Streamlit applications
│   ├── sales_dashboard/               # Example app 1
│   │   ├── streamlit_app.py          # Main app file
│   │   ├── environment.yml           # App-specific dependencies
│   │   └── common/                   # Local copy of shared utilities
│   │       ├── snowflake_utils.py    # Snowflake connection utilities
│   │       ├── data_utils.py         # Data processing utilities
│   │       └── ui_components.py      # Reusable UI components
│   ├── customer_analytics/           # Example app 2
│   │   ├── streamlit_app.py
│   │   ├── environment.yml
│   │   └── common/
│   └── finance_dashboard/            # Example app 3
│       ├── streamlit_app.py
│       ├── environment.yml
│       └── common/
├── scripts/                           # Deployment and management scripts
│   ├── deploy_from_git.py            # Main git-based deployment script
│   ├── ensure_git_setup.py           # Git integration setup
│   ├── ci_deploy.py                  # CI/CD deployment script
│   └── create_app.py                 # App creation wizard
├── docs/                              # Documentation
│   ├── git_workflow.md               # Git branching strategy
│   └── github_actions_setup.md       # CI/CD setup guide
├── setup_git_integration.sql          # Snowflake git setup SQL
└── .github/                          # GitHub workflows
    └── workflows/
        └── deploy-streamlit.yml      # CI/CD pipeline
```

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd snowflake-streamlit

# Install dependencies
pip install -r requirements.txt

# Set up Snowflake git integration (one-time setup)
python scripts/ensure_git_setup.py
```

### 2. Create a New App

```bash
# Use the app creation wizard
python scripts/create_app.py

# Follow the prompts to create a new app with:
# - App name and description
# - Template selection (basic/advanced)
# - Automatic dependency setup
```

### 3. Deploy Apps

#### **🎯 Recommended: Use `--update` for Latest Code**
```bash
# Deploy specific app with latest git changes
python scripts/deploy_from_git.py --update finance_dashboard

# Deploy from specific branch
python scripts/deploy_from_git.py --update sales_dashboard --branch develop
```

#### **⚡ Quick Deploy (uses cached version)**
```bash
# Deploy without syncing (uses what's already in Snowflake)
python scripts/deploy_from_git.py --app sales_dashboard
```

#### **🔄 Manual Sync + Deploy**
```bash
# Sync git repository first, then deploy
python scripts/deploy_from_git.py --sync
python scripts/deploy_from_git.py --app sales_dashboard
```

#### **📦 Deploy All Apps**
```bash
# Deploy all apps (automatically syncs first)
python scripts/deploy_from_git.py --all
```

## 🔧 Deployment Commands Reference

| Command | Syncs Git? | Use Case |
|---------|------------|----------|
| `--update <app>` | ✅ Yes | **Recommended** - Deploy latest code |
| `--app <app>` | ❌ No | Quick deploy from cached version |
| `--all` | ✅ Yes | Deploy all apps with latest code |
| `--sync` | ✅ Yes | Just sync, no deployment |
| `--list` | - | List available apps |
| `--deployed` | - | List deployed apps |
| `--delete <app>` | - | Delete deployed app |

### Examples:
```bash
# Get latest code and deploy
python scripts/deploy_from_git.py --update finance_dashboard

# List available apps
python scripts/deploy_from_git.py --list

# Check what's currently deployed
python scripts/deploy_from_git.py --deployed

# Deploy from specific branch
python scripts/deploy_from_git.py --update sales_dashboard --branch feature/new-charts
```

## 🌊 Development Workflow

### Git Branching Strategy

1. **`main`** - Production deployments
2. **`develop`** - Development/staging deployments  
3. **`feature/*`** - Feature development branches
4. **`hotfix/*`** - Critical production fixes

### Developer Workflow

```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/sales-dashboard/new-metrics

# 2. Develop locally (optional)
cd apps/sales_dashboard
streamlit run streamlit_app.py

# 3. Deploy to staging for testing
cd ../..
python scripts/deploy_from_git.py --update sales_dashboard --branch feature/sales-dashboard/new-metrics

# 4. Create pull request to develop
# 5. After merge, deploy to production from main
python scripts/deploy_from_git.py --update sales_dashboard --branch main
```

## 🏗️ App Architecture

### Self-Contained Apps
Each app includes its own copy of shared utilities to avoid dependency issues:

```python
# In each app's streamlit_app.py
from common.snowflake_utils import get_snowflake_connection
from common.ui_components import display_metric
from common.data_utils import generate_sample_data
```

### App Structure
```
apps/your_app/
├── streamlit_app.py      # Entry point (required)
├── environment.yml       # Dependencies (required) 
└── common/              # Shared utilities (auto-created)
    ├── snowflake_utils.py
    ├── data_utils.py
    └── ui_components.py
```

### Creating New Apps
```bash
python scripts/create_app.py
# Choose template:
# - basic: Simple single-page app
# - advanced: Multi-page app with navigation
```

## 🔄 CI/CD Pipeline

### Automated Deployments
The GitHub Action automatically:
- **Validates** all apps before deployment
- **Detects changes** and deploys only modified apps  
- **Deploys to production** from `main` branch
- **Deploys to development** from `develop` branch
- **Runs dry-run validation** on pull requests

### Manual Deployments
Use GitHub Actions **workflow dispatch** for:
- Deploying specific apps
- Deploying from any branch
- Emergency production deployments

### Local CI Testing
```bash
# Test CI logic locally
python scripts/ci_deploy.py --validate-only
python scripts/ci_deploy.py --mode changed --dry-run
python scripts/ci_deploy.py --mode single --app finance_dashboard
```

## 🛠️ Management Commands

### Git Repository Management
```bash
# Check git repository status
python scripts/deploy_from_git.py --status

# Force sync from GitHub
python scripts/deploy_from_git.py --sync

# Setup/verify git integration
python scripts/ensure_git_setup.py
```

### App Management
```bash
# List available apps in repository
python scripts/deploy_from_git.py --list

# List deployed Streamlit apps
python scripts/deploy_from_git.py --deployed

# Delete deployed app
python scripts/deploy_from_git.py --delete app_name
```

## 🔧 Configuration

### Snowflake Connection
Uses Snowflake CLI configuration from `~/.snowflake/config.toml`:
```toml
[connections.streamlit_env]
account = "your-account"
user = "your-user"  
password = "your-password"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
```

### App Dependencies
Each app has its own `environment.yml`:
```yaml
name: your_app_name
channels:
  - snowflake
dependencies:
  - python=3.11
  - streamlit
  - pandas
  - numpy
  - snowflake-snowpark-python
```

## 🐛 Troubleshooting

### Common Issues

#### **"Stage does not exist" Error**
```bash
# Ensure git repository is properly connected
python scripts/ensure_git_setup.py
```

#### **Authentication Failures**
```bash
# Test Snowflake connection
snow connection test --connection streamlit_env

# Verify git repository access
python scripts/deploy_from_git.py --status
```

#### **Package/Python Version Errors**
- Use `python=3.11` in `environment.yml`
- Use only `snowflake` channel for dependencies
- Check available packages in Snowflake documentation

#### **Import Errors in Apps**
- Ensure `common/` directory exists in each app
- Use relative imports: `from common.snowflake_utils import ...`
- Recreate app with `python scripts/create_app.py` if needed

### Recovery Commands
```bash
# Reset to last known good state
git checkout main
python scripts/deploy_from_git.py --sync
python scripts/deploy_from_git.py --all

# Redeploy single app
python scripts/deploy_from_git.py --delete app_name
python scripts/deploy_from_git.py --update app_name
```

## 📚 Documentation

- **[Git Workflow Guide](docs/git_workflow.md)** - Branching strategy and best practices
- **[GitHub Actions Setup](docs/github_actions_setup.md)** - CI/CD pipeline configuration
- **[Git Integration Setup](setup_git_integration.sql)** - Snowflake SQL setup

## 🚀 Best Practices

1. **Always use `--update`** for production deployments to ensure latest code
2. **Test in staging** before deploying to production
3. **Use descriptive branch names** following the pattern in git workflow docs
4. **Keep apps self-contained** - each app has its own dependencies
5. **Monitor deployments** through GitHub Actions and Snowflake logs
6. **Use pull requests** for all changes to main/develop branches

---

This setup provides a robust, scalable solution for managing multiple Streamlit applications with true git integration and automated deployment pipelines! 🎯 