#!/usr/bin/env python3
"""
Git-based deployment script for Streamlit applications.

This script uses Snowflake's native git integration to deploy
Streamlit apps directly from git repositories.
"""

import argparse
import os
import sys
import subprocess
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GitStreamlitDeployer:
    """Handles git-based deployment of Streamlit applications to Snowflake."""
    
    def __init__(self, project_root: Path, connection: str = "streamlit_env"):
        self.project_root = project_root
        self.apps_dir = project_root / "apps"
        self.connection = connection
        
    def get_available_apps(self) -> List[str]:
        """Get list of available Streamlit apps."""
        if not self.apps_dir.exists():
            logger.error(f"Apps directory not found: {self.apps_dir}")
            return []
            
        apps = []
        for item in self.apps_dir.iterdir():
            if item.is_dir() and (item / "streamlit_app.py").exists():
                apps.append(item.name)
                
        return sorted(apps)
    
    def create_streamlit_from_git(self, app_name: str, branch: str = "main", 
                                 git_repo: str = "streamlit_apps_repo") -> bool:
        """Create a Streamlit app from git repository."""
        logger.info(f"Creating Streamlit app '{app_name}' from git branch '{branch}'")
        
        # Construct the SQL command
        sql_command = f"""
        CREATE OR REPLACE STREAMLIT STREAMLIT.APPS.{app_name.upper()}
        ROOT_LOCATION = '@{git_repo}/branches/{branch}/apps/{app_name}/'
        MAIN_FILE = 'streamlit_app.py'
        QUERY_WAREHOUSE = 'COMPUTE_WH'
        COMMENT = 'Streamlit app deployed from git repository';
        """
        
        try:
            # Execute the SQL command
            cmd = [
                "snow", "sql", "-q", sql_command,
                "--connection", self.connection
            ]
            
            logger.info(f"Executing SQL command for {app_name}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Successfully created Streamlit app: {app_name}")
            logger.info(f"Output: {result.stdout}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create Streamlit app {app_name}: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
    
    def update_streamlit_from_git(self, app_name: str, branch: str = "main") -> bool:
        """Update an existing Streamlit app from git."""
        logger.info(f"Updating Streamlit app '{app_name}' from git branch '{branch}'")
        
        # First, refresh the git repository
        refresh_sql = "ALTER GIT REPOSITORY streamlit_apps_repo FETCH;"
        
        try:
            # Refresh the git repository
            cmd = [
                "snow", "sql", "-q", refresh_sql,
                "--connection", self.connection
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Git repository refreshed successfully")
            
            # Now recreate the Streamlit app to pick up changes
            return self.create_streamlit_from_git(app_name, branch)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to refresh git repository: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
    
    def list_git_streamlit_apps(self) -> List[Dict[str, Any]]:
        """List Streamlit apps created from git."""
        sql_command = """
        SHOW STREAMLITS IN SCHEMA STREAMLIT.APPS;
        """
        
        try:
            cmd = [
                "snow", "sql", "-q", sql_command,
                "--connection", self.connection,
                "--format", "json"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                return json.loads(result.stdout)
            return []
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list Streamlit apps: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse app list: {e}")
            return []
    
    def delete_streamlit_app(self, app_name: str) -> bool:
        """Delete a Streamlit app."""
        sql_command = f"DROP STREAMLIT IF EXISTS STREAMLIT.APPS.{app_name.upper()};"
        
        try:
            cmd = [
                "snow", "sql", "-q", sql_command,
                "--connection", self.connection
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Successfully deleted Streamlit app: {app_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete app {app_name}: {e}")
            return False
    
    def get_git_repository_status(self) -> Dict[str, Any]:
        """Get the status of the git repository."""
        sql_command = "SHOW GIT REPOSITORIES LIKE 'streamlit_apps_repo';"
        
        try:
            cmd = [
                "snow", "sql", "-q", sql_command,
                "--connection", self.connection,
                "--format", "json"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout:
                repos = json.loads(result.stdout)
                if repos:
                    return repos[0]
            return {}
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get git repository status: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse repository status: {e}")
            return {}
    
    def sync_from_git(self) -> bool:
        """Sync the git repository to get latest changes."""
        sql_command = "ALTER GIT REPOSITORY streamlit_apps_repo FETCH;"
        
        try:
            cmd = [
                "snow", "sql", "-q", sql_command,
                "--connection", self.connection
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Successfully synced from git repository")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to sync from git: {e}")
            return False
    
    def deploy_all_apps(self, branch: str = "main") -> Dict[str, bool]:
        """Deploy all available apps from git."""
        apps = self.get_available_apps()
        results = {}
        
        logger.info(f"Deploying {len(apps)} apps from git branch '{branch}': {apps}")
        
        # First sync from git
        if not self.sync_from_git():
            logger.error("Failed to sync from git, aborting deployment")
            return {app: False for app in apps}
        
        for app in apps:
            results[app] = self.create_streamlit_from_git(app, branch)
            
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Streamlit applications from git repository"
    )
    
    parser.add_argument(
        "--app",
        type=str,
        help="Name of specific app to deploy from git"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Deploy all available apps from git"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available apps in repository"
    )
    
    parser.add_argument(
        "--deployed",
        action="store_true",
        help="List deployed Streamlit apps"
    )
    
    parser.add_argument(
        "--delete",
        type=str,
        help="Delete a deployed Streamlit app"
    )
    
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sync from git repository"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show git repository status"
    )
    
    parser.add_argument(
        "--update",
        type=str,
        help="Update specific app from git"
    )
    
    parser.add_argument(
        "--branch",
        type=str,
        default="main",
        help="Git branch to deploy from (default: main)"
    )
    
    parser.add_argument(
        "--connection",
        type=str,
        default="streamlit_env",
        help="Snowflake connection to use (default: streamlit_env)"
    )
    
    args = parser.parse_args()
    
    # Initialize deployer
    deployer = GitStreamlitDeployer(
        project_root=Path(__file__).parent.parent,
        connection=args.connection
    )
    
    # Handle different commands
    if args.list:
        apps = deployer.get_available_apps()
        print(f"Available apps in repository ({len(apps)}):")
        for app in apps:
            print(f"  - {app}")
            
    elif args.deployed:
        apps = deployer.list_git_streamlit_apps()
        print(f"Deployed Streamlit apps ({len(apps)}):")
        for app in apps:
            name = app.get('name', 'Unknown')
            print(f"  - {name}")
            
    elif args.delete:
        success = deployer.delete_streamlit_app(args.delete)
        sys.exit(0 if success else 1)
        
    elif args.sync:
        success = deployer.sync_from_git()
        sys.exit(0 if success else 1)
        
    elif args.status:
        status = deployer.get_git_repository_status()
        if status:
            print("Git Repository Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
        else:
            print("Git repository not found or not accessible")
            
    elif args.update:
        success = deployer.update_streamlit_from_git(args.update, args.branch)
        sys.exit(0 if success else 1)
        
    elif args.all:
        results = deployer.deploy_all_apps(args.branch)
        
        successful = [app for app, success in results.items() if success]
        failed = [app for app, success in results.items() if not success]
        
        print(f"\nGit Deployment Results (branch: {args.branch}):")
        print(f"  Successful ({len(successful)}): {successful}")
        print(f"  Failed ({len(failed)}): {failed}")
        
        sys.exit(0 if not failed else 1)
        
    elif args.app:
        success = deployer.create_streamlit_from_git(args.app, args.branch)
        sys.exit(0 if success else 1)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 