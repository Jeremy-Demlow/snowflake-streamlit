#!/usr/bin/env python3
"""
Ensure Git Setup Script
Ensures that all necessary components for git integration are set up before deployment.
"""

import subprocess
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_sql_command(sql_command: str, connection: str = "streamlit_env") -> bool:
    """Execute a SQL command using Snowflake CLI."""
    try:
        cmd = [
            "snow", "sql", "-q", sql_command,
            "--connection", connection
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"SQL executed successfully")
        logger.debug(f"Output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"SQL execution failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def check_api_integration(integration_name: str, connection: str = "streamlit_env") -> bool:
    """Check if an API integration exists."""
    try:
        cmd = [
            "snow", "sql", "-q", f"SHOW API INTEGRATIONS LIKE '{integration_name}';",
            "--connection", connection
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        return integration_name.upper() in result.stdout
        
    except subprocess.CalledProcessError:
        return False

def check_git_repository(repo_name: str, connection: str = "streamlit_env") -> bool:
    """Check if a git repository exists."""
    try:
        cmd = [
            "snow", "sql", "-q", f"SHOW GIT REPOSITORIES LIKE '{repo_name}';",
            "--connection", connection
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        return repo_name.upper() in result.stdout
        
    except subprocess.CalledProcessError:
        return False

def check_database_schema(connection: str = "streamlit_env") -> bool:
    """Ensure STREAMLIT.APPS schema exists."""
    logger.info("Checking STREAMLIT.APPS schema...")
    
    # Create database if needed
    if not run_sql_command("CREATE DATABASE IF NOT EXISTS STREAMLIT;", connection):
        return False
    
    # Create schema if needed
    if not run_sql_command("CREATE SCHEMA IF NOT EXISTS STREAMLIT.APPS;", connection):
        return False
    
    logger.info("✅ STREAMLIT.APPS schema is ready")
    return True

def setup_api_integration(connection: str = "streamlit_env") -> bool:
    """Set up API integration for GitHub."""
    logger.info("Setting up GitHub API integration...")
    
    # Check if GitHub PAT integration exists
    if check_api_integration("github_pat_integration", connection):
        logger.info("✅ GitHub PAT integration already exists")
        return True
    
    # Create PAT integration
    create_integration_sql = """
    CREATE OR REPLACE API INTEGRATION github_pat_integration
        API_PROVIDER = GIT_HTTPS_API
        API_ALLOWED_PREFIXES = ('https://github.com/')
        ALLOWED_AUTHENTICATION_SECRETS = ALL
        ENABLED = TRUE
        COMMENT = 'GitHub PAT integration for Streamlit git repos';
    """
    
    if run_sql_command(create_integration_sql, connection):
        logger.info("✅ GitHub PAT integration created")
        return True
    else:
        logger.error("❌ Failed to create GitHub PAT integration")
        return False

def setup_git_repository(repo_url: str, connection: str = "streamlit_env") -> bool:
    """Set up git repository."""
    repo_name = "streamlit_apps_repo"
    logger.info(f"Setting up git repository: {repo_name}")
    
    # Check if git repository exists
    if check_git_repository(repo_name, connection):
        logger.info("✅ Git repository already exists")
        
        # Test if we can fetch from it
        fetch_sql = f"ALTER GIT REPOSITORY STREAMLIT.PUBLIC.{repo_name} FETCH;"
        if run_sql_command(fetch_sql, connection):
            logger.info("✅ Git repository is accessible")
            return True
        else:
            logger.warning("⚠️ Git repository exists but fetch failed - may need authentication")
    
    # Create git repository
    create_repo_sql = f"""
    CREATE OR REPLACE GIT REPOSITORY STREAMLIT.PUBLIC.{repo_name}
        API_INTEGRATION = github_pat_integration
        ORIGIN = '{repo_url}'
        COMMENT = 'Git repository for multiple Streamlit applications';
    """
    
    if run_sql_command(create_repo_sql, connection):
        logger.info("✅ Git repository created")
        
        # Try to fetch
        fetch_sql = f"ALTER GIT REPOSITORY STREAMLIT.PUBLIC.{repo_name} FETCH;"
        if run_sql_command(fetch_sql, connection):
            logger.info("✅ Git repository fetch successful")
            return True
        else:
            logger.warning("⚠️ Git repository created but fetch failed")
            logger.info("This might be because:")
            logger.info("1. Repository is private and needs authentication")
            logger.info("2. Repository URL is incorrect")
            logger.info("3. API integration needs additional setup")
            return False
    else:
        logger.error("❌ Failed to create git repository")
        return False

def setup_permissions(connection: str = "streamlit_env") -> bool:
    """Set up necessary permissions."""
    logger.info("Setting up permissions...")
    
    permissions_sql = [
        "GRANT USAGE ON GIT REPOSITORY STREAMLIT.PUBLIC.streamlit_apps_repo TO ROLE ACCOUNTADMIN;",
        "GRANT USAGE ON DATABASE STREAMLIT TO ROLE ACCOUNTADMIN;",
        "GRANT ALL ON SCHEMA STREAMLIT.APPS TO ROLE ACCOUNTADMIN;"
    ]
    
    for sql in permissions_sql:
        if not run_sql_command(sql, connection):
            logger.warning(f"⚠️ Permission command failed (might already exist): {sql}")
    
    logger.info("✅ Permissions configured")
    return True

def main():
    """Main setup function."""
    connection = "streamlit_env"
    repo_url = "https://github.com/Jeremy-Demlow/snowflake-streamlit.git"
    
    logger.info("🚀 Starting Git Integration Setup for Streamlit")
    logger.info("=" * 60)
    
    success = True
    
    # Step 1: Database and Schema
    if not check_database_schema(connection):
        logger.error("❌ Database/Schema setup failed")
        success = False
    
    # Step 2: API Integration
    if not setup_api_integration(connection):
        logger.error("❌ API Integration setup failed")
        success = False
    
    # Step 3: Git Repository
    if not setup_git_repository(repo_url, connection):
        logger.error("❌ Git Repository setup failed")
        success = False
    
    # Step 4: Permissions
    if not setup_permissions(connection):
        logger.error("❌ Permissions setup failed")
        success = False
    
    logger.info("=" * 60)
    if success:
        logger.info("✅ Git Integration Setup Complete!")
        logger.info("You can now deploy Streamlit apps from git repository")
    else:
        logger.error("❌ Git Integration Setup Failed!")
        logger.info("Please check the errors above and resolve them")
        sys.exit(1)

if __name__ == "__main__":
    main() 