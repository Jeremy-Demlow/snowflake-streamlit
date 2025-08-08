#!/usr/bin/env python3
"""
CI/CD Deployment Script - Local Testing for GitHub Actions
Tests the deployment logic before creating the GitHub Action
"""

import os
import sys
import subprocess
import argparse
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentError(Exception):
    """Custom exception for deployment errors"""
    pass

class CIDeployer:
    """Handles CI/CD style deployments for testing GitHub Action logic"""
    
    def __init__(self, connection: str = "streamlit_env", dry_run: bool = False):
        self.connection = connection
        self.dry_run = dry_run
        self.repo_root = Path(__file__).parent.parent
        
    def get_changed_apps(self, base_branch: str = "main") -> List[str]:
        """
        Get list of apps that have changed files
        Checks both staged and unstaged changes
        """
        try:
            changed_files = set()
            
            # Get staged changes
            result = subprocess.run([
                "git", "diff", "--name-only", "--cached"
            ], capture_output=True, text=True, cwd=self.repo_root)
            
            if result.returncode == 0 and result.stdout.strip():
                staged_files = result.stdout.strip().split('\n')
                changed_files.update(staged_files)
            
            # Get unstaged changes
            result = subprocess.run([
                "git", "diff", "--name-only"
            ], capture_output=True, text=True, cwd=self.repo_root)
            
            if result.returncode == 0 and result.stdout.strip():
                unstaged_files = result.stdout.strip().split('\n')
                changed_files.update(unstaged_files)
            
            # Get changes between branches (for PR scenarios)
            result = subprocess.run([
                "git", "diff", "--name-only", f"origin/{base_branch}...HEAD"
            ], capture_output=True, text=True, cwd=self.repo_root)
            
            if result.returncode == 0 and result.stdout.strip():
                branch_files = result.stdout.strip().split('\n')
                changed_files.update(branch_files)
            
            changed_files = list(changed_files)
            logger.info(f"Changed files: {changed_files}")
            
            # Extract app names from changed files
            changed_apps = set()
            for file_path in changed_files:
                if file_path.startswith('apps/') and '/' in file_path[5:]:
                    app_name = file_path.split('/')[1]
                    changed_apps.add(app_name)
            
            return list(changed_apps)
            
        except Exception as e:
            logger.error(f"Error getting changed apps: {e}")
            return []
    
    def get_all_apps(self) -> List[str]:
        """Get all available apps in the repository"""
        apps_dir = self.repo_root / "apps"
        if not apps_dir.exists():
            return []
        
        apps = []
        for item in apps_dir.iterdir():
            if item.is_dir() and (item / "streamlit_app.py").exists():
                apps.append(item.name)
        
        return apps
    
    def validate_app(self, app_name: str) -> bool:
        """Validate that an app is ready for deployment"""
        app_dir = self.repo_root / "apps" / app_name
        
        # Check required files
        required_files = [
            "streamlit_app.py",
            "common/__init__.py",
            "common/snowflake_utils.py",
            "common/ui_components.py",
            "common/data_utils.py"
        ]
        
        for file_path in required_files:
            if not (app_dir / file_path).exists():
                logger.error(f"App {app_name} missing required file: {file_path}")
                return False
        
        logger.info(f"App {app_name} validation passed")
        return True
    
    def deploy_app(self, app_name: str, branch: str = "main") -> bool:
        """Deploy a single app"""
        logger.info(f"Deploying app: {app_name} from branch: {branch}")
        
        if not self.validate_app(app_name):
            return False
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would deploy {app_name}")
            return True
        
        try:
            # Use our existing deployment script
            deploy_script = self.repo_root / "scripts" / "deploy_from_git.py"
            
            cmd = [
                "python", str(deploy_script),
                "--app", app_name,
                "--branch", branch,
                "--connection", self.connection
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_root)
            
            if result.returncode == 0:
                logger.info(f"Successfully deployed {app_name}")
                logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"Failed to deploy {app_name}")
                logger.error(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Exception deploying {app_name}: {e}")
            return False
    
    def sync_repository(self) -> bool:
        """Sync the git repository in Snowflake"""
        logger.info("Syncing git repository")
        
        if self.dry_run:
            logger.info("[DRY RUN] Would sync git repository")
            return True
        
        try:
            deploy_script = self.repo_root / "scripts" / "deploy_from_git.py"
            
            cmd = [
                "python", str(deploy_script),
                "--sync",
                "--connection", self.connection
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_root)
            
            if result.returncode == 0:
                logger.info("Successfully synced git repository")
                return True
            else:
                logger.error(f"Failed to sync git repository: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Exception syncing repository: {e}")
            return False
    
    def deploy_changed_apps(self, base_branch: str = "main", current_branch: str = "main") -> Dict[str, bool]:
        """Deploy all changed apps"""
        changed_apps = self.get_changed_apps(base_branch)
        
        if not changed_apps:
            logger.info("No changed apps detected")
            return {}
        
        logger.info(f"Deploying changed apps: {changed_apps}")
        
        # First sync the repository
        if not self.sync_repository():
            raise DeploymentError("Failed to sync git repository")
        
        # Deploy each changed app
        results = {}
        for app_name in changed_apps:
            results[app_name] = self.deploy_app(app_name, current_branch)
        
        return results
    
    def deploy_all_apps(self, branch: str = "main") -> Dict[str, bool]:
        """Deploy all apps"""
        all_apps = self.get_all_apps()
        
        if not all_apps:
            logger.info("No apps found")
            return {}
        
        logger.info(f"Deploying all apps: {all_apps}")
        
        # First sync the repository
        if not self.sync_repository():
            raise DeploymentError("Failed to sync git repository")
        
        # Deploy each app
        results = {}
        for app_name in all_apps:
            results[app_name] = self.deploy_app(app_name, branch)
        
        return results

def main():
    parser = argparse.ArgumentParser(description='CI/CD Deployment Script for Streamlit Apps')
    parser.add_argument('--mode', choices=['changed', 'all', 'single'], default='changed',
                        help='Deployment mode')
    parser.add_argument('--app', help='Specific app to deploy (for single mode)')
    parser.add_argument('--base-branch', default='main', help='Base branch for change detection')
    parser.add_argument('--current-branch', default='main', help='Current branch to deploy from')
    parser.add_argument('--connection', default='streamlit_env', help='Snowflake connection')
    parser.add_argument('--dry-run', action='store_true', help='Perform dry run without actual deployment')
    parser.add_argument('--validate-only', action='store_true', help='Only validate apps, no deployment')
    
    args = parser.parse_args()
    
    deployer = CIDeployer(connection=args.connection, dry_run=args.dry_run)
    
    try:
        if args.validate_only:
            logger.info("Validation mode - checking all apps")
            all_apps = deployer.get_all_apps()
            for app_name in all_apps:
                valid = deployer.validate_app(app_name)
                logger.info(f"App {app_name}: {'✅ VALID' if valid else '❌ INVALID'}")
            return
        
        if args.mode == 'single':
            if not args.app:
                logger.error("App name required for single mode")
                sys.exit(1)
            
            success = deployer.deploy_app(args.app, args.current_branch)
            if not success:
                sys.exit(1)
                
        elif args.mode == 'changed':
            results = deployer.deploy_changed_apps(args.base_branch, args.current_branch)
            
            # Check results
            failed_apps = [app for app, success in results.items() if not success]
            if failed_apps:
                logger.error(f"Failed to deploy apps: {failed_apps}")
                sys.exit(1)
            
            if results:
                logger.info(f"Successfully deployed: {list(results.keys())}")
            else:
                logger.info("No apps needed deployment")
                
        elif args.mode == 'all':
            results = deployer.deploy_all_apps(args.current_branch)
            
            # Check results
            failed_apps = [app for app, success in results.items() if not success]
            if failed_apps:
                logger.error(f"Failed to deploy apps: {failed_apps}")
                sys.exit(1)
            
            logger.info(f"Successfully deployed all apps: {list(results.keys())}")
        
        logger.info("✅ Deployment completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 