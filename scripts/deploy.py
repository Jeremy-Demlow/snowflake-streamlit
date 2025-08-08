#!/usr/bin/env python3
"""
Deployment script for multiple Streamlit applications.

This script handles deployment of individual apps or all apps
to Snowflake using the Snowflake CLI.
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

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StreamlitDeployer:
    """Handles deployment of Streamlit applications to Snowflake."""
    
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
            if item.is_dir() and (item / "snowflake.yml").exists():
                apps.append(item.name)
                
        return sorted(apps)
    
    def validate_app(self, app_name: str) -> bool:
        """Validate that an app has required files."""
        app_dir = self.apps_dir / app_name
        
        if not app_dir.exists():
            logger.error(f"App directory not found: {app_dir}")
            return False
            
        required_files = ["snowflake.yml", "streamlit_app.py"]
        missing_files = []
        
        for file in required_files:
            if not (app_dir / file).exists():
                missing_files.append(file)
                
        if missing_files:
            logger.error(f"App {app_name} missing required files: {missing_files}")
            return False
            
        return True
    
    def deploy_app(self, app_name: str, environment: str = "dev") -> bool:
        """Deploy a single Streamlit app."""
        logger.info(f"Deploying app: {app_name}")
        
        if not self.validate_app(app_name):
            return False
            
        app_dir = self.apps_dir / app_name
        
        try:
            # Change to app directory
            os.chdir(app_dir)
            
            # Run snow streamlit deploy
            cmd = [
                "snow", "streamlit", "deploy",
                "--connection", self.connection,
                "--replace"
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Deployment successful for {app_name}")
            logger.info(f"Output: {result.stdout}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Deployment failed for {app_name}: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deploying {app_name}: {e}")
            return False
        finally:
            # Change back to project root
            os.chdir(self.project_root)
    
    def deploy_all_apps(self, environment: str = "dev") -> Dict[str, bool]:
        """Deploy all available apps."""
        apps = self.get_available_apps()
        results = {}
        
        logger.info(f"Deploying {len(apps)} apps: {apps}")
        
        for app in apps:
            results[app] = self.deploy_app(app, environment)
            
        return results
    
    def list_deployed_apps(self) -> List[Dict[str, Any]]:
        """List currently deployed Streamlit apps."""
        try:
            cmd = [
                "snow", "streamlit", "list",
                "--connection", self.connection,
                "--format", "json"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return json.loads(result.stdout) if result.stdout else []
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list apps: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse app list: {e}")
            return []
    
    def delete_app(self, app_name: str) -> bool:
        """Delete a deployed Streamlit app."""
        try:
            cmd = [
                "snow", "streamlit", "drop",
                app_name,
                "--connection", self.connection
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Successfully deleted app: {app_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete app {app_name}: {e}")
            return False
    
    def get_app_status(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific app."""
        deployed_apps = self.list_deployed_apps()
        
        for app in deployed_apps:
            if app.get('name', '').lower() == app_name.lower():
                return app
                
        return None
    
    def sync_from_git(self, app_name: Optional[str] = None) -> bool:
        """Sync apps from git repository."""
        try:
            # For now, this is a simple git pull
            # In the future, this could integrate with Snowflake's git features
            cmd = ["git", "pull", "origin", "main"]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Successfully synced from git")
            logger.info(f"Output: {result.stdout}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to sync from git: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Streamlit applications to Snowflake"
    )
    
    parser.add_argument(
        "--app",
        type=str,
        help="Name of specific app to deploy"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Deploy all available apps"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available apps"
    )
    
    parser.add_argument(
        "--deployed",
        action="store_true",
        help="List deployed apps"
    )
    
    parser.add_argument(
        "--delete",
        type=str,
        help="Delete a deployed app"
    )
    
    parser.add_argument(
        "--status",
        type=str,
        help="Get status of a specific app"
    )
    
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sync from git repository"
    )
    
    parser.add_argument(
        "--connection",
        type=str,
        default="streamlit_env",
        help="Snowflake connection to use (default: streamlit_env)"
    )
    
    parser.add_argument(
        "--environment",
        type=str,
        default="dev",
        help="Deployment environment (default: dev)"
    )
    
    args = parser.parse_args()
    
    # Initialize deployer
    deployer = StreamlitDeployer(
        project_root=Path(__file__).parent.parent,
        connection=args.connection
    )
    
    # Handle different commands
    if args.list:
        apps = deployer.get_available_apps()
        print(f"Available apps ({len(apps)}):")
        for app in apps:
            print(f"  - {app}")
            
    elif args.deployed:
        apps = deployer.list_deployed_apps()
        print(f"Deployed apps ({len(apps)}):")
        for app in apps:
            print(f"  - {app.get('name', 'Unknown')} (Status: {app.get('status', 'Unknown')})")
            
    elif args.delete:
        success = deployer.delete_app(args.delete)
        sys.exit(0 if success else 1)
        
    elif args.status:
        status = deployer.get_app_status(args.status)
        if status:
            print(f"App: {args.status}")
            for key, value in status.items():
                print(f"  {key}: {value}")
        else:
            print(f"App {args.status} not found or not deployed")
            
    elif args.sync:
        success = deployer.sync_from_git()
        sys.exit(0 if success else 1)
        
    elif args.all:
        results = deployer.deploy_all_apps(args.environment)
        
        successful = [app for app, success in results.items() if success]
        failed = [app for app, success in results.items() if not success]
        
        print(f"\nDeployment Results:")
        print(f"  Successful ({len(successful)}): {successful}")
        print(f"  Failed ({len(failed)}): {failed}")
        
        sys.exit(0 if not failed else 1)
        
    elif args.app:
        success = deployer.deploy_app(args.app, args.environment)
        sys.exit(0 if success else 1)
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 