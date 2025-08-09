# GitHub Actions Setup for Streamlit Deployment

This guide walks you through setting up automated deployments of your Streamlit apps using GitHub Actions with Snowflake's native git integration.

## 🚀 Overview

The GitHub Action workflow automatically:
- **Validates** all apps before deployment
- **Detects changes** and deploys only modified apps
- **Supports multiple environments** (main → production, develop → development)
- **Provides manual deployment** options via workflow dispatch
- **Dry run testing** for pull requests
- **Uses git sync** to ensure latest code deployment

## 📋 Prerequisites

1. **Snowflake Account** with proper permissions
2. **GitHub Repository** with admin access
3. **Snowflake CLI access** (for initial setup)
4. **Git repository integrated** with Snowflake (use `python scripts/ensure_git_setup.py`)

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
GRANT USAGE ON GIT REPOSITORY STREAMLIT.PUBLIC.streamlit_apps_repo TO ROLE STREAMLIT_DEPLOYER;

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
# Test git integration setup
python scripts/ensure_git_setup.py

# Test validation
python scripts/ci_deploy.py --validate-only

# Test change detection (dry run)
python scripts/ci_deploy.py --mode changed --dry-run

# Test single app deployment
python scripts/ci_deploy.py --mode single --app finance_dashboard --dry-run

# Actual deployment test
python scripts/ci_deploy.py --mode single --app finance_dashboard

# Test git-based deployment directly
python scripts/deploy_from_git.py --update finance_dashboard
```

### 4. Workflow Triggers

The GitHub Action triggers on:

#### **Automatic Triggers:**
- **Push to `main`**: Deploys changed apps to production using `--update` command
- **Push to `develop`**: Deploys changed apps to development using `--update` command
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
4. **Apps are deployed** to Snowflake using latest git code

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
- Checks all apps for required files (`streamlit_app.py`, `environment.yml`, `common/`)
- Detects which apps have changed
- Sets outputs for downstream jobs

### 2. **Deploy for PR** (Pull Requests only)
- Runs dry run validation
- Shows what would be deployed
- No actual deployment occurs

### 3. **Deploy to Production** (`main` branch)
- Deploys changed apps to production
- Uses `python scripts/deploy_from_git.py --update <app> --branch main`
- Requires all validations to pass

### 4. **Deploy to Development** (`develop` branch)
- Deploys changed apps to development
- Uses `python scripts/deploy_from_git.py --update <app> --branch develop`
- Great for testing before production

### 5. **Manual Deployment** (Workflow Dispatch)
- Flexible manual deployment options
- Can deploy specific apps or all apps
- Can deploy from any branch
- Uses appropriate `--update` or `--all` commands

### 6. **Notify**
- Provides deployment summary
- Shows success/failure status
- Lists deployed apps

## 🔧 Deployment Commands Used

The GitHub Action uses these deployment commands:

| Scenario | Command Used | Auto-Sync |
|----------|-------------|-----------|
| Changed apps | `python scripts/deploy_from_git.py --update <app> --branch <branch>` | ✅ Yes |
| All apps | `python scripts/deploy_from_git.py --all --branch <branch>` | ✅ Yes |
| Single app | `python scripts/deploy_from_git.py --update <app> --branch <branch>` | ✅ Yes |
| Dry run | `python scripts/ci_deploy.py --mode <mode> --dry-run` | N/A |

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
```bash
# Debug locally
python scripts/deploy_from_git.py --status
python scripts/ensure_git_setup.py
```

#### **App Validation Failures**
- Check required files exist in app directory:
  - `streamlit_app.py` (required)
  - `environment.yml` (required)
  - `common/` directory with utilities (auto-created by `create_app.py`)

#### **"Stage does not exist" Errors**
```bash
# Fix git integration
python scripts/ensure_git_setup.py
```

#### **No Apps Detected for Deployment**
- Ensure changes are in `apps/` directory
- Check file paths in commit
- Verify app directories contain required files

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

# Test git integration
python scripts/deploy_from_git.py --status
python scripts/deploy_from_git.py --list

# Test deployment
python scripts/deploy_from_git.py --update your_app_name --branch main
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
- **Development** deployments from `develop` using `--update` with develop branch
- **Production** deployments from `main` using `--update` with main branch

## 📈 Advanced Configuration

### Environment-Specific Deployments

The GitHub Action automatically deploys to different environments based on branch:

```yaml
# Automatic environment detection
- name: Deploy to Production
  if: github.ref == 'refs/heads/main'
  run: python scripts/deploy_from_git.py --update ${{ app }} --branch main

- name: Deploy to Development  
  if: github.ref == 'refs/heads/develop'
  run: python scripts/deploy_from_git.py --update ${{ app }} --branch develop
```

### Custom App Templates

Create new apps with proper structure:

```bash
# Interactive app creation
python scripts/create_app.py

# Automatically creates:
# - streamlit_app.py
# - environment.yml  
# - common/ directory with utilities
```

### Slack Notifications (Optional)

Add Slack webhook for deployment notifications:

```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## 🚨 Emergency Procedures

### Emergency Deployment
```bash
# Use GitHub Actions workflow dispatch for emergency deployments
# Or deploy directly:
python scripts/deploy_from_git.py --update critical_app --branch hotfix/emergency-fix
```

### Rollback Procedure
```bash
# Delete problematic deployment
python scripts/deploy_from_git.py --delete app_name

# Deploy previous version
git checkout previous-working-commit
python scripts/deploy_from_git.py --update app_name --branch main
```

### Recovery Commands
```bash
# Reset git integration
python scripts/ensure_git_setup.py

# Force sync and redeploy all
python scripts/deploy_from_git.py --sync
python scripts/deploy_from_git.py --all --branch main
```

## 📚 Related Documentation

- **[Git Workflow Guide](git_workflow.md)** - Branching strategy and deployment commands
- **[Repository README](../README.md)** - Complete setup and usage guide
- **[Git Integration Setup](../setup_git_integration.sql)** - Snowflake SQL setup

---

This setup provides a robust, automated deployment pipeline that ensures your Streamlit applications are always deployed with the latest code using Snowflake's native git integration! 🚀 