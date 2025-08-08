-- Setup script for Snowflake Git Integration
-- This script creates the necessary git repository and API integration for Streamlit apps

-- 1. Create API Integration for GitHub OAuth (when available)
CREATE OR REPLACE API INTEGRATION github_oauth
    API_USER_AUTHENTICATION = (TYPE = SNOWFLAKE_GITHUB_APP)
    API_PROVIDER = GIT_HTTPS_API
    API_ALLOWED_PREFIXES = ('https://github.com/')
    ENABLED = TRUE
    COMMENT = 'GitHub OAuth integration for Streamlit git repos';

-- 2. Alternative: Create API Integration with allowed secrets (for PAT authentication)
CREATE OR REPLACE API INTEGRATION github_pat_integration
    API_PROVIDER = GIT_HTTPS_API
    API_ALLOWED_PREFIXES = ('https://github.com/')
    ALLOWED_AUTHENTICATION_SECRETS = ALL
    ENABLED = TRUE
    COMMENT = 'GitHub PAT integration for Streamlit git repos';

-- 3. Create a secret for PAT authentication (replace YOUR_GITHUB_PAT with actual token)
-- CREATE OR REPLACE SECRET github_pat
--     TYPE = PASSWORD
--     USERNAME = 'your-github-username'
--     PASSWORD = 'YOUR_GITHUB_PAT'
--     COMMENT = 'GitHub Personal Access Token for repository access';

-- 4. Create git repository pointing to your GitHub repo
-- Note: Replace 'https://github.com/your-org/snowflake-streamlit.git' with your actual repo URL
CREATE OR REPLACE GIT REPOSITORY streamlit_apps_repo
    API_INTEGRATION = github_oauth  -- Use github_pat_integration if using PAT
    -- GIT_CREDENTIALS = github_pat  -- Uncomment if using PAT authentication
    ORIGIN = 'https://github.com/your-org/snowflake-streamlit.git'
    COMMENT = 'Git repository for multiple Streamlit applications';

-- 5. Grant usage on the git repository to appropriate roles
GRANT USAGE ON GIT REPOSITORY streamlit_apps_repo TO ROLE ACCOUNTADMIN;
GRANT USAGE ON GIT REPOSITORY streamlit_apps_repo TO ROLE DATA_SCIENTIST;

-- 6. Create schema for Streamlit apps if it doesn't exist
CREATE SCHEMA IF NOT EXISTS STREAMLIT.APPS;

-- Show the created resources
SHOW API INTEGRATIONS LIKE 'github%';
SHOW GIT REPOSITORIES;
SHOW SECRETS; 