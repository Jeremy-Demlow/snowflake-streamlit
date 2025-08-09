# Git Workflow Guide

This document outlines the recommended git workflow for managing multiple Streamlit applications in this repository using Snowflake's native git integration.

## Branching Strategy

We use a **Git Flow** inspired approach adapted for Streamlit application development:

### Branch Types

1. **`main`** - Production-ready code
   - Always deployable
   - Protected branch requiring pull request reviews
   - Deployed to production Snowflake environment
   - Use: `python scripts/deploy_from_git.py --update <app> --branch main`

2. **`develop`** - Integration branch
   - Latest development changes
   - Used for staging deployments
   - All feature branches merge here first
   - Use: `python scripts/deploy_from_git.py --update <app> --branch develop`

3. **`feature/app-name/feature-description`** - Feature development
   - Format: `feature/sales-dashboard/add-filters`
   - Created from `develop`
   - Merged back to `develop` via pull request

4. **`hotfix/app-name/issue-description`** - Critical fixes
   - Format: `hotfix/sales-dashboard/fix-chart-error`
   - Created from `main`
   - Merged to both `main` and `develop`

5. **`release/version`** - Release preparation
   - Format: `release/v1.2.0`
   - Created from `develop`
   - Merged to `main` and tagged

## Workflow Steps

### Starting New Development

```bash
# 1. Start from develop branch
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/sales-dashboard/new-chart

# 3. Work on your changes
# ... make changes ...

# 4. Test locally (optional)
cd apps/sales-dashboard
streamlit run streamlit_app.py

# 5. Deploy to staging for testing
cd ../..
python scripts/deploy_from_git.py --update sales-dashboard --branch feature/sales-dashboard/new-chart

# 6. Commit changes
git add .
git commit -m "feat(sales-dashboard): add new revenue chart"

# 7. Push feature branch
git push origin feature/sales-dashboard/new-chart

# 8. Create pull request to develop
```

### Pull Request Guidelines

#### Title Format
- `feat(app-name): description` - New features
- `fix(app-name): description` - Bug fixes
- `docs(app-name): description` - Documentation updates
- `refactor(app-name): description` - Code refactoring
- `test(app-name): description` - Test additions/updates

#### Pull Request Template
```markdown
## Description
Brief description of changes

## App(s) Affected
- [ ] sales_dashboard
- [ ] customer_analytics  
- [ ] finance_dashboard
- [ ] shared utilities

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] Deployed to staging
- [ ] All validations pass

## Deployment Commands Used
```bash
# Commands used for testing
python scripts/deploy_from_git.py --update app_name --branch feature/branch-name
```

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No merge conflicts
```

## Deployment Workflow

### 🎯 **Recommended Deployment Commands**

#### **For Latest Code (Recommended)**
```bash
# Deploy with automatic git sync
python scripts/deploy_from_git.py --update <app-name> --branch <branch>
```

#### **Quick Deploy (Cached Version)**
```bash
# Deploy without syncing (uses cached version in Snowflake)
python scripts/deploy_from_git.py --app <app-name>
```

#### **Manual Sync + Deploy**
```bash
# Sync first, then deploy
python scripts/deploy_from_git.py --sync
python scripts/deploy_from_git.py --app <app-name>
```

### Development/Staging Deployment
```bash
# Deploy feature branch to staging
git checkout feature/sales-dashboard/new-feature
python scripts/deploy_from_git.py --update sales-dashboard --branch feature/sales-dashboard/new-feature

# Or deploy develop branch to staging
python scripts/deploy_from_git.py --update sales-dashboard --branch develop
```

### Production Deployment
```bash
# Deploy to production from main branch
git checkout main
git pull origin main
python scripts/deploy_from_git.py --update sales-dashboard --branch main

# Or deploy all apps to production
python scripts/deploy_from_git.py --all --branch main
```

## Working with Snowflake Git Integration

### Current Setup
- ✅ **HTTPS Git Integration** with PAT authentication
- ✅ **Multi-branch deployment** support
- ✅ **Automatic sync** with `--update` command
- ✅ **CI/CD pipeline** with GitHub Actions

### Deployment Command Reference

| Command | Auto-Sync | Use Case | Example |
|---------|-----------|----------|---------|
| `--update <app>` | ✅ Yes | **Recommended** for latest code | `--update sales-dashboard` |
| `--app <app>` | ❌ No | Quick deploy from cache | `--app sales-dashboard` |
| `--all` | ✅ Yes | Deploy all apps | `--all --branch main` |
| `--sync` | ✅ Yes | Just sync git repository | `--sync` |

### Management Commands
```bash
# List available apps
python scripts/deploy_from_git.py --list

# List deployed apps
python scripts/deploy_from_git.py --deployed

# Check git repository status
python scripts/deploy_from_git.py --status

# Delete deployed app
python scripts/deploy_from_git.py --delete app-name
```

## App-Specific Workflows

### Individual App Development

```bash
# 1. Create app-specific feature branch
git checkout develop
git checkout -b feature/sales-dashboard/add-forecasting

# 2. Work in the app directory
cd apps/sales_dashboard

# 3. Test locally (optional)
streamlit run streamlit_app.py

# 4. Deploy to staging for testing
cd ../..
python scripts/deploy_from_git.py --update sales-dashboard --branch feature/sales-dashboard/add-forecasting

# 5. Commit and push
git add .
git commit -m "feat(sales-dashboard): add forecasting module"
git push origin feature/sales-dashboard/add-forecasting

# 6. Create pull request when ready
```

### Multi-App Changes

```bash
# 1. Create feature branch for shared changes
git checkout develop
git checkout -b feature/shared/update-ui-components

# 2. Make changes to shared utilities (copied to each app)
# Note: Changes need to be made in each app's common/ directory
# Or use create_app.py to regenerate apps with updated utilities

# 3. Test all affected apps
python scripts/deploy_from_git.py --update sales-dashboard --branch feature/shared/update-ui-components
python scripts/deploy_from_git.py --update customer-analytics --branch feature/shared/update-ui-components
python scripts/deploy_from_git.py --update finance-dashboard --branch feature/shared/update-ui-components

# 4. Or deploy all apps at once
python scripts/deploy_from_git.py --all --branch feature/shared/update-ui-components

# 5. Document which apps are affected in PR
```

## Conflict Resolution

### Merge Conflicts
```bash
# 1. Fetch latest changes
git fetch origin

# 2. Rebase your feature branch
git checkout feature/your-feature
git rebase origin/develop

# 3. Resolve conflicts in your editor
# ... resolve conflicts ...

# 4. Continue rebase
git add .
git rebase --continue

# 5. Force push (if necessary)
git push origin feature/your-feature --force-with-lease

# 6. Redeploy after resolving conflicts
python scripts/deploy_from_git.py --update your-app --branch feature/your-feature
```

### Snowflake Deployment Issues
```bash
# If deployment fails:

# 1. Check current deployed apps
python scripts/deploy_from_git.py --deployed

# 2. Check git repository status
python scripts/deploy_from_git.py --status

# 3. Force sync and redeploy
python scripts/deploy_from_git.py --sync
python scripts/deploy_from_git.py --update app-name

# 4. If still failing, delete and recreate
python scripts/deploy_from_git.py --delete app-name
python scripts/deploy_from_git.py --update app-name
```

## Best Practices

### Commit Messages
- Use conventional commit format
- Include app name in scope
- Keep first line under 50 characters
- Use imperative mood

```bash
# Good examples
git commit -m "feat(sales-dashboard): add quarterly revenue chart"
git commit -m "fix(shared): resolve connection timeout issue"
git commit -m "docs(finance-dashboard): update API documentation"

# Bad examples
git commit -m "fixed stuff"
git commit -m "WIP: working on dashboard"
```

### Branch Naming
- Use descriptive names
- Include app name for app-specific changes
- Use kebab-case

```bash
# Good examples
feature/sales-dashboard/add-filters
hotfix/finance-dashboard/fix-calculation
feature/shared/improve-caching

# Bad examples
feature/new-stuff
fix-bug
john-working-branch
```

### Deployment Best Practices

1. **Always use `--update`** for production deployments
   ```bash
   # Recommended for production
   python scripts/deploy_from_git.py --update app-name --branch main
   ```

2. **Test in staging first**
   ```bash
   # Deploy feature branch to staging
   python scripts/deploy_from_git.py --update app-name --branch feature/my-feature
   ```

3. **Use branch-specific deployments**
   ```bash
   # Deploy specific branch
   python scripts/deploy_from_git.py --update app-name --branch develop
   ```

4. **Verify deployment success**
   ```bash
   # Check deployed apps
   python scripts/deploy_from_git.py --deployed
   ```

### Code Reviews

#### What to Review
- [ ] Code quality and style
- [ ] Performance implications
- [ ] Security considerations
- [ ] Impact on other apps
- [ ] Documentation updates
- [ ] Proper deployment commands used

#### Review Checklist
- [ ] Does the code work as expected?
- [ ] Are there any obvious bugs?
- [ ] Is the code readable and maintainable?
- [ ] Are naming conventions followed?
- [ ] Is error handling appropriate?
- [ ] Are imports using `from common.* import ...`?
- [ ] Does the app have required files (streamlit_app.py, environment.yml)?

## CI/CD Integration

### Automated Workflows
The GitHub Action automatically:
- Validates all apps before deployment
- Detects changed apps and deploys only those
- Uses `--update` command for latest code
- Deploys to production from `main` branch
- Deploys to development from `develop` branch

### Manual GitHub Actions
Use workflow dispatch for:
- Emergency deployments
- Deploying specific apps
- Deploying from any branch

### Local CI Testing
```bash
# Test CI logic locally
python scripts/ci_deploy.py --validate-only
python scripts/ci_deploy.py --mode changed --dry-run
python scripts/ci_deploy.py --mode single --app finance-dashboard
```

## Troubleshooting

### Common Issues

1. **"Stage does not exist" Error**
   ```bash
   # Ensure git integration is set up
   python scripts/ensure_git_setup.py
   ```

2. **Deployment Failures**
   ```bash
   # Test connection
   snow connection test --connection streamlit_env
   
   # Check git repository status
   python scripts/deploy_from_git.py --status
   
   # Force sync and retry
   python scripts/deploy_from_git.py --sync
   python scripts/deploy_from_git.py --update app-name
   ```

3. **Import Errors in Apps**
   - Ensure `common/` directory exists in each app
   - Use relative imports: `from common.snowflake_utils import ...`
   - Recreate app if needed: `python scripts/create_app.py`

### Recovery Procedures

```bash
# Reset to last known good state
git checkout main
git pull origin main
python scripts/deploy_from_git.py --sync
python scripts/deploy_from_git.py --all

# Rollback specific app
python scripts/deploy_from_git.py --delete app-name
git checkout previous-commit -- apps/app-name
git add . && git commit -m "revert(app-name): rollback to working version"
python scripts/deploy_from_git.py --update app-name
```

## Future Improvements

### Planned Features
- [ ] Automated testing in CI/CD
- [ ] Branch protection rules enforcement
- [ ] Automatic dependency updates
- [ ] Enhanced monitoring and alerting
- [ ] Multi-environment configuration

### Development Roadmap
- Enhanced error handling in deployment scripts
- Improved local development experience
- Better integration with Snowflake's native git features
- Advanced deployment strategies (blue-green, canary)

---

**Remember**: Always use `--update` for production deployments to ensure you're deploying the latest code, and test in staging before deploying to production! 