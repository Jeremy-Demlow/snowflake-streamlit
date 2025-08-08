# GitHub Actions Setup for Streamlit Deployment

This guide walks you through setting up automated deployments of your Streamlit apps using GitHub Actions.

## 🚀 Overview

The GitHub Action workflow automatically:
- **Validates** all apps before deployment
- **Detects changes** and deploys only modified apps
- **Supports multiple environments** (main → production, develop → development)
- **Provides manual deployment** options via workflow dispatch
- **Dry run testing** for pull requests

## 📋 Prerequisites

1. **Snowflake Account** with proper permissions
2. **GitHub Repository** with admin access
3. **Snowflake CLI access** (for initial setup)
4. **Git repository integrated** with Snowflake (completed in previous setup)

## 🔧 Setup Instructions

### 1. Configure GitHub Secrets

In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions** and add these secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `SNOWFLAKE_ACCOUNT` | Your Snowflake account identifier | `abc12345.us-east-1` |
| `SNOWFLAKE_USER` | Snowflake username | `DEPLOYMENT_USER` |
| `SNOWFLAKE_PASSWORD` | Snowflake password | `your-secure-password` |
| `SNOWFLAKE_ROLE` | Snowflake role for deployments | `ACCOUNTADMIN` |
| `SNOWFLAKE_WAREHOUSE` | Default warehouse | `COMPUTE_WH` |
| `SNOWFLAKE_DATABASE` | Database for apps | `STREAMLIT` |
| `SNOWFLAKE_SCHEMA` | Schema for apps | `APPS` |

### 2. Create Deployment User (Recommended)

For production, create a dedicated service account:

```sql
-- Create role for CI/CD deployments
CREATE OR REPLACE ROLE STREAMLIT_DEPLOYER;

-- Grant necessary permissions
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE STREAMLIT_DEPLOYER;
GRANT USAGE ON DATABASE STREAMLIT TO ROLE STREAMLIT_DEPLOYER;
GRANT ALL ON SCHEMA STREAMLIT.APPS TO ROLE STREAMLIT_DEPLOYER;
GRANT USAGE ON GIT REPOSITORY streamlit_apps_repo TO ROLE STREAMLIT_DEPLOYER;

-- Create user
CREATE OR REPLACE USER streamlit_ci_user
    PASSWORD = 'your-secure-password'
    DEFAULT_ROLE = 'STREAMLIT_DEPLOYER'
    DEFAULT_WAREHOUSE = 'COMPUTE_WH'
    DEFAULT_NAMESPACE = 'STREAMLIT.APPS';

-- Assign role to user
GRANT ROLE STREAMLIT_DEPLOYER TO USER streamlit_ci_user;
```

### 3. Test Locally First

Before pushing to GitHub, test the deployment logic locally:

```bash
# Test validation
python scripts/ci_deploy.py --validate-only

# Test change detection (dry run)
python scripts/ci_deploy.py --mode changed --dry-run

# Test single app deployment
python scripts/ci_deploy.py --mode single --app finance_dashboard --dry-run

# Actual deployment test
python scripts/ci_deploy.py --mode single --app finance_dashboard
```

### 4. Workflow Triggers

The GitHub Action triggers on:

#### **Automatic Triggers:**
- **Push to `main`**: Deploys changed apps to production
- **Push to `develop`**: Deploys changed apps to development  
- **Pull Request**: Dry run validation only
- **Changes in `apps/` directory**: Only triggers when Streamlit apps are modified

#### **Manual Triggers:**
- **Workflow Dispatch**: Manual deployment with options
  - **Mode**: `changed`, `all`, or `single`
  - **App Name**: For single app deployments
  - **Branch**: Which branch to deploy from

## 🎯 Usage Examples

### Automatic Deployment

1. **Make changes** to any app in `apps/` directory
2. **Commit and push** to `main` or `develop` branch
3. **GitHub Action runs** automatically
4. **Apps are deployed** to Snowflake

### Manual Deployment

1. Go to **Actions** tab in GitHub
2. Select **Deploy Streamlit Apps** workflow
3. Click **Run workflow**
4. Choose your options:
   - **Mode**: `changed` (only modified apps), `all` (all apps), `single` (specific app)
   - **App Name**: Required for single mode
   - **Branch**: Which branch to deploy from

### Pull Request Testing

1. **Create PR** with app changes
2. **GitHub Action runs** validation and dry run
3. **Review results** before merging
4. **Merge PR** triggers production deployment

## 📊 Workflow Jobs

### 1. **Validate**
- Checks all apps for required files
- Detects which apps have changed
- Sets outputs for downstream jobs

### 2. **Deploy for PR** (Pull Requests only)
- Runs dry run validation
- Shows what would be deployed
- No actual deployment occurs

### 3. **Deploy to Production** (`main` branch)
- Deploys changed apps to production
- Uses `main` branch in Snowflake git repo
- Requires all validations to pass

### 4. **Deploy to Development** (`develop` branch)
- Deploys changed apps to development
- Uses `develop` branch in Snowflake git repo
- Great for testing before production

### 5. **Manual Deployment** (Workflow Dispatch)
- Flexible manual deployment options
- Can deploy specific apps or all apps
- Can deploy from any branch

### 6. **Notify**
- Provides deployment summary
- Shows success/failure status
- Lists deployed apps

## 🔍 Monitoring and Troubleshooting

### Viewing Deployment Status

1. **Actions Tab**: See all workflow runs
2. **Job Details**: Click on specific jobs for logs
3. **Summary**: View deployment summary with app list

### Common Issues

#### **Authentication Errors**
- Check GitHub secrets are correctly set
- Verify Snowflake user has proper permissions
- Ensure password is current

#### **Git Repository Sync Issues**
- Verify git repository exists in Snowflake
- Check OAuth/PAT authentication is working
- Ensure latest commits are pushed to GitHub

#### **App Validation Failures**
- Check required files exist in app directory
- Ensure `common/` utilities are copied to each app
- Validate app structure matches template

#### **No Apps Detected for Deployment**
- Ensure changes are in `apps/` directory
- Check file paths in commit
- Verify app directories contain `streamlit_app.py`

### Debugging Commands

```bash
# Local debugging
python scripts/ci_deploy.py --validate-only
python scripts/ci_deploy.py --mode changed --dry-run

# Check app structure
ls -la apps/your_app_name/
ls -la apps/your_app_name/common/

# Test git diff detection
git diff --name-only
git diff --name-only origin/main...HEAD
```

## 🛡️ Security Best Practices

1. **Use dedicated service account** for deployments
2. **Limit permissions** to minimum required
3. **Rotate passwords** regularly
4. **Monitor deployment logs** for suspicious activity
5. **Use branch protection** rules on main/develop
6. **Require PR reviews** before merging

## 🔄 Branching Strategy

Recommended Git flow:

```
main (production)
├── develop (development/staging)
    ├── feature/new-dashboard
    ├── feature/update-analytics
    └── hotfix/critical-bug
```

- **Feature branches** → **develop** → **main**
- **Hotfixes** → **main** (with backport to develop)
- **Development** deployments from `develop`
- **Production** deployments from `main`

## 📈 Advanced Configuration

### Custom Environments

To use GitHub Environments (requires GitHub Pro/Enterprise):

```yaml
deploy-main:
  environment: 
    name: production
    url: https://app.snowflake.com/your-account/
```

### Slack Notifications

Add Slack webhook for deployment notifications:

```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Matrix Deployments

Deploy to multiple environments:

```yaml
strategy:
  matrix:
    environment: [staging, production]
```

This setup provides a robust, automated deployment pipeline for your Streamlit applications! 🚀 