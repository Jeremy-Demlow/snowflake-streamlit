# Snowflake Git Integration Setup Guide

This guide explains how to set up **Snowflake's native git integration** for deploying Streamlit applications directly from GitHub repositories.

## Overview

Unlike the Snowflake CLI deployment approach, this method uses Snowflake's built-in git repository integration to deploy Streamlit apps directly from your git repository. This is the proper way to achieve the git-based workflow you described in your Slack conversation.

## Key Differences

| CLI Approach (Previous) | Git Integration (Correct) |
|-------------------------|---------------------------|
| `snow streamlit deploy` | `CREATE STREAMLIT ... ROOT_LOCATION = '@git_repo/...'` |
| Local file upload | Direct git repository access |
| Manual sync required | Automatic git fetch |
| No branching workflow | Full git branching support |
| Snowflake projects | Pure git repositories |

## Setup Steps

### 1. Set Up Git Repository Integration

First, you need to create the API integration and git repository in Snowflake. Run the SQL commands from `setup_git_integration.sql`:

```sql
-- 1. Create API Integration for GitHub
CREATE OR REPLACE API INTEGRATION github_oauth
    API_USER_AUTHENTICATION = (TYPE = SNOWFLAKE_GITHUB_APP)
    API_PROVIDER = GIT_HTTPS_API
    API_ALLOWED_PREFIXES = ('https://github.com/')
    ENABLED = TRUE;

-- 2. Create Git Repository (replace with your actual repo URL)
CREATE OR REPLACE GIT REPOSITORY streamlit_apps_repo
    API_INTEGRATION = github_oauth
    ORIGIN = 'https://github.com/your-org/snowflake-streamlit.git';
```

### 2. Alternative: PAT Authentication

If OAuth is not available, use Personal Access Token authentication:

```sql
-- Create secret for PAT
CREATE OR REPLACE SECRET github_pat
    TYPE = PASSWORD
    USERNAME = 'your-github-username'
    PASSWORD = 'your_github_personal_access_token';

-- Create API integration for PAT
CREATE OR REPLACE API INTEGRATION github_pat_integration
    API_PROVIDER = GIT_HTTPS_API
    API_ALLOWED_PREFIXES = ('https://github.com/')
    ALLOWED_AUTHENTICATION_SECRETS = ALL
    ENABLED = TRUE;

-- Create git repository with PAT
CREATE OR REPLACE GIT REPOSITORY streamlit_apps_repo
    API_INTEGRATION = github_pat_integration
    GIT_CREDENTIALS = github_pat
    ORIGIN = 'https://github.com/your-org/snowflake-streamlit.git';
```

### 3. Repository Structure

Your repository should be structured like this for git integration:

```
snowflake-streamlit/
├── apps/
│   ├── sales_dashboard/
│   │   ├── streamlit_app.py     # Main Streamlit file
│   │   ├── pages/               # Additional pages
│   │   │   └── details.py
│   │   └── utils.py             # Local utilities
│   ├── financial_reports/
│   │   ├── streamlit_app.py
│   │   └── pages/
│   └── data_explorer/
│       ├── streamlit_app.py
│       └── pages/
├── shared/                      # Shared utilities (optional)
│   └── common/
│       ├── snowflake_utils.py
│       └── ui_components.py
└── scripts/
    └── deploy_from_git.py       # Git deployment script
```

### 4. Deploy Apps from Git

Use the new git-based deployment script:

```bash
# Deploy specific app from main branch
python scripts/deploy_from_git.py --app sales_dashboard

# Deploy from specific branch
python scripts/deploy_from_git.py --app sales_dashboard --branch feature/new-charts

# Deploy all apps
python scripts/deploy_from_git.py --all

# Update app from git (pulls latest changes)
python scripts/deploy_from_git.py --update sales_dashboard

# Sync git repository
python scripts/deploy_from_git.py --sync

# List deployed apps
python scripts/deploy_from_git.py --deployed
```

## Git Workflow with Snowflake

### 1. Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/sales-dashboard/new-charts

# 2. Make changes to apps/sales_dashboard/streamlit_app.py
# ... edit files ...

# 3. Commit and push
git add apps/sales_dashboard/
git commit -m "feat: add new revenue charts to sales dashboard"
git push origin feature/sales-dashboard/new-charts

# 4. Deploy from feature branch for testing
python scripts/deploy_from_git.py --app sales_dashboard --branch feature/sales-dashboard/new-charts

# 5. Create pull request to main
# 6. After merge, deploy from main
python scripts/deploy_from_git.py --app sales_dashboard --branch main
```

### 2. How Snowflake Git Integration Works

When you run:
```sql
CREATE STREAMLIT STREAMLIT.APPS.SALES_DASHBOARD
ROOT_LOCATION = '@streamlit_apps_repo/branches/main/apps/sales_dashboard/'
MAIN_FILE = 'streamlit_app.py'
```

Snowflake:
1. Connects to your git repository using the API integration
2. Accesses the specified branch and path
3. Creates the Streamlit app directly from the git files
4. Updates automatically when you run `ALTER GIT REPOSITORY ... FETCH`

### 3. Branching Strategy

```
main branch (production)
├── apps/sales_dashboard/streamlit_app.py
├── apps/financial_reports/streamlit_app.py
└── apps/data_explorer/streamlit_app.py

develop branch (staging)
├── apps/sales_dashboard/streamlit_app.py (with new features)
├── apps/financial_reports/streamlit_app.py
└── apps/data_explorer/streamlit_app.py

feature/dashboard/new-charts branch
├── apps/sales_dashboard/streamlit_app.py (experimental features)
└── ...
```

Deploy different environments from different branches:
- Production: `main` branch
- Staging: `develop` branch  
- Testing: feature branches

## Benefits of Git Integration

### 1. True Git Workflow
- ✅ Deploy directly from any git branch
- ✅ Automatic sync with repository changes
- ✅ No manual file uploads
- ✅ Full version control integration

### 2. Branch-Based Deployments
- ✅ Deploy different versions from different branches
- ✅ Test features in isolation
- ✅ Easy rollbacks to previous versions
- ✅ Environment-specific deployments

### 3. Collaborative Development
- ✅ Multiple developers can work on different apps
- ✅ Pull request workflow for code reviews
- ✅ Automatic deployment from approved changes
- ✅ Clear separation between development and production

### 4. Simplified Management
- ✅ No Snowflake project files needed
- ✅ Standard git repository structure
- ✅ Works with any git hosting (GitHub, GitLab, etc.)
- ✅ Integration with CI/CD pipelines

## Troubleshooting

### Common Issues

1. **Git Repository Access**
   ```bash
   # Check git repository status
   python scripts/deploy_from_git.py --status
   
   # Sync repository
   python scripts/deploy_from_git.py --sync
   ```

2. **Authentication Issues**
   - For OAuth: Ensure GitHub App is properly configured
   - For PAT: Verify personal access token has repo access

3. **Path Issues**
   - Ensure your app structure matches the ROOT_LOCATION path
   - Check that `streamlit_app.py` exists in the correct location

4. **Permission Issues**
   ```sql
   -- Grant necessary permissions
   GRANT USAGE ON GIT REPOSITORY streamlit_apps_repo TO ROLE your_role;
   GRANT CREATE STREAMLIT ON SCHEMA STREAMLIT.APPS TO ROLE your_role;
   ```

## Migration from CLI to Git Integration

If you have existing CLI-deployed apps, migrate them:

1. **Remove CLI-specific files**:
   - Delete `snowflake.yml` files
   - Delete `environment.yml` files (dependencies handled by git)
   - Clean up project structure

2. **Set up git integration** as described above

3. **Redeploy from git**:
   ```bash
   # Delete old CLI-deployed app
   DROP STREAMLIT STREAMLIT.PUBLIC.sales_dashboard;
   
   # Deploy from git
   python scripts/deploy_from_git.py --app sales_dashboard
   ```

## Next Steps

1. **Set up the git repository integration** using the SQL commands
2. **Push your repository** to GitHub
3. **Test deployment** with a simple app
4. **Configure branch-based workflows** for your team
5. **Set up CI/CD integration** for automatic deployments

This approach gives you the true git-integrated Streamlit workflow that was discussed in your Slack conversation! 