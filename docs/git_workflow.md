# Git Workflow Guide

This document outlines the recommended git workflow for managing multiple Streamlit applications in this repository.

## Branching Strategy

We use a **Git Flow** inspired approach adapted for Streamlit application development:

### Branch Types

1. **`main`** - Production-ready code
   - Always deployable
   - Protected branch requiring pull request reviews
   - Deployed to production Snowflake environment

2. **`develop`** - Integration branch
   - Latest development changes
   - Used for staging deployments
   - All feature branches merge here first

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

# 4. Commit changes
git add .
git commit -m "feat(sales-dashboard): add new revenue chart"

# 5. Push feature branch
git push origin feature/sales-dashboard/new-chart

# 6. Create pull request to develop
# Use GitHub/GitLab interface
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
- [ ] financial_reports
- [ ] data_explorer
- [ ] shared utilities

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] Deployed to staging
- [ ] All tests pass

## Screenshots (if applicable)
[Add screenshots here]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No merge conflicts
```

### Deployment Workflow

#### Development/Staging
```bash
# Deploy to staging from develop branch
git checkout develop
python scripts/deploy.py --app sales_dashboard --environment staging
```

#### Production
```bash
# Deploy to production from main branch
git checkout main
python scripts/deploy.py --app sales_dashboard --environment production
```

## Working with Snowflake Git Integration

### Current Limitations (Q4 2024)
- SSH not supported (HTTPS only)
- Limited branching support in Snowflake UI
- Manual sync required

### Recommended Approach

1. **Use PAT for Initial Setup**
   ```sql
   CREATE OR REPLACE API INTEGRATION github_oauth
       API_USER_AUTHENTICATION = (TYPE = SNOWFLAKE_GITHUB_APP)
       API_PROVIDER = GIT_HTTPS_API
       API_ALLOWED_PREFIXES = ('https://github.com/your-org')
       ENABLED = TRUE;
   ```

2. **Deploy from Specific Branches**
   ```bash
   # Ensure you're on the right branch before deploying
   git checkout main  # or develop for staging
   python scripts/deploy.py --app sales_dashboard
   ```

3. **Use Scripts for Sync**
   ```bash
   # Pull latest changes and redeploy
   python scripts/deploy.py --sync
   python scripts/deploy.py --all
   ```

## App-Specific Workflows

### Individual App Development

```bash
# 1. Create app-specific feature branch
git checkout -b feature/sales-dashboard/add-forecasting

# 2. Work in the app directory
cd apps/sales_dashboard

# 3. Test locally (if possible)
streamlit run streamlit_app.py

# 4. Deploy to staging for testing
cd ../..
python scripts/deploy.py --app sales_dashboard --environment staging

# 5. Create pull request when ready
```

### Multi-App Changes

```bash
# 1. Create feature branch for shared changes
git checkout -b feature/shared/update-ui-components

# 2. Make changes to shared utilities
# ... edit shared/common/ui_components.py ...

# 3. Test all affected apps
python scripts/deploy.py --all --environment staging

# 4. Document which apps are affected in PR
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
```

### Snowflake Deployment Conflicts
```bash
# If deployment fails due to conflicts:

# 1. Check current deployed version
python scripts/deploy.py --deployed

# 2. Sync from git
python scripts/deploy.py --sync

# 3. Redeploy with replace flag
python scripts/deploy.py --app sales_dashboard --replace
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
git commit -m "docs(financial-reports): update API documentation"

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
hotfix/financial-reports/fix-calculation
feature/shared/improve-caching

# Bad examples
feature/new-stuff
fix-bug
john-working-branch
```

### Code Reviews

#### What to Review
- [ ] Code quality and style
- [ ] Performance implications
- [ ] Security considerations
- [ ] Impact on other apps
- [ ] Documentation updates
- [ ] Test coverage

#### Review Checklist
- [ ] Does the code work as expected?
- [ ] Are there any obvious bugs?
- [ ] Is the code readable and maintainable?
- [ ] Are naming conventions followed?
- [ ] Is error handling appropriate?
- [ ] Are shared utilities used properly?

## Git Hooks (Optional)

### Pre-commit Hook
Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run basic checks before commit

# Check for large files
git diff --cached --name-only | xargs ls -la | awk '$5 > 1000000 { print $9 ": " $5 " bytes" }'

# Check for secrets (basic)
if git diff --cached | grep -E "(password|secret|key)" | grep -v "# password"; then
    echo "Warning: Potential secret detected"
    exit 1
fi

# Run basic linting (if tools available)
if command -v flake8 &> /dev/null; then
    flake8 --max-line-length=100 $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
fi
```

### Pre-push Hook
Create `.git/hooks/pre-push`:

```bash
#!/bin/bash
# Validate before pushing

protected_branch='main'
current_branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

if [ $protected_branch = $current_branch ]; then
    echo "Direct push to main branch is not allowed"
    exit 1
fi
```

## Troubleshooting

### Common Issues

1. **Merge Conflicts in snowflake.yml**
   - Usually safe to accept both changes
   - Each app has its own configuration

2. **Deployment Failures**
   - Check connection: `snow connection test`
   - Verify permissions: Check role and warehouse access
   - Look at error logs in deployment output

3. **Shared Utility Conflicts**
   - Test all apps after changes to shared code
   - Use feature flags for breaking changes
   - Version shared utilities if needed

### Recovery Procedures

```bash
# Reset to last known good state
git checkout main
git pull origin main
python scripts/deploy.py --all

# Rollback specific app
python scripts/deploy.py --delete app_name
git checkout previous_commit -- apps/app_name
python scripts/deploy.py --app app_name
```

## Future Improvements

### When SSH Support is Added
- Update API integration to use SSH
- Implement automatic branch-based deployments
- Add webhook integrations

### Planned Features
- [ ] Automated testing in CI/CD
- [ ] Branch protection rules
- [ ] Automatic dependency updates
- [ ] Integration with Snowflake's native git features

---

**Remember**: Always test your changes in a staging environment before merging to `main` and deploying to production. 