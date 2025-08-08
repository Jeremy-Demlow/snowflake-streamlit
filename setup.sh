#!/bin/bash
# Setup script for Multi-App Streamlit Repository

set -e  # Exit on any error

echo "🚀 Setting up Multi-App Streamlit Repository..."

# Function to print colored output
print_status() {
    echo -e "\033[36m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

# Check if we're in the right directory
if [[ ! -f "README.md" ]] || [[ ! -d "apps" ]]; then
    print_error "Please run this script from the repository root"
    exit 1
fi

# Check if Snowflake CLI is installed
print_status "Checking Snowflake CLI installation..."
if ! command -v snow &> /dev/null; then
    print_error "Snowflake CLI not found. Please install it first:"
    echo "  pip install snowflake-cli"
    exit 1
fi
print_success "Snowflake CLI found"

# Check if Git is initialized
print_status "Checking Git setup..."
if [[ ! -d ".git" ]]; then
    print_status "Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Multi-app Streamlit repository"
fi
print_success "Git repository ready"

# Install Python dependencies
print_status "Installing Python dependencies..."
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found"
fi

# Test Snowflake connection
print_status "Testing Snowflake connection..."
if snow connection test streamlit_env &> /dev/null; then
    print_success "Snowflake connection successful"
else
    print_error "Snowflake connection failed. Please check your connection configuration:"
    echo "  snow configure"
    echo "  Or verify ~/.snowflake/config.toml"
fi

# Make scripts executable
print_status "Setting up deployment scripts..."
chmod +x scripts/*.py
print_success "Scripts are now executable"

# Create develop branch if it doesn't exist
print_status "Setting up Git branches..."
if ! git show-ref --verify --quiet refs/heads/develop; then
    git checkout -b develop
    git checkout main
    print_success "Created develop branch"
fi

# Display next steps
echo ""
echo "🎉 Setup complete! Here's what you can do next:"
echo ""
echo "📋 Available Commands:"
echo "  • List available apps:     python scripts/deploy.py --list"
echo "  • Create new app:          python scripts/create_app.py --name my_app --template dashboard"
echo "  • Deploy an app:           python scripts/deploy.py --app sales_dashboard"
echo "  • Deploy all apps:         python scripts/deploy.py --all"
echo ""
echo "📖 Documentation:"
echo "  • README.md - Overview and quick start"
echo "  • docs/git_workflow.md - Git workflow guide"
echo "  • docs/developer_guide.md - Developer documentation"
echo ""
echo "🏗️ Example Apps:"
echo "  • sales_dashboard - Comprehensive sales analytics"
echo "  • apps/ directory - Add your own apps here"
echo ""
echo "🔧 Configuration:"
echo "  • ~/.snowflake/config.toml - Snowflake connections"
echo "  • global_config/ - Shared configurations"
echo "  • shared/ - Common utilities and components"
echo ""

# Optional: Create initial apps if they don't exist
read -p "Would you like to create example apps? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Creating example applications..."
    
    # Only create if they don't exist
    if [[ ! -d "apps/financial_reports" ]]; then
        python scripts/create_app.py --name financial_reports --template analytics
        print_success "Created financial_reports app"
    fi
    
    if [[ ! -d "apps/data_explorer" ]]; then
        python scripts/create_app.py --name data_explorer --template basic
        print_success "Created data_explorer app"
    fi
fi

print_success "🚀 Multi-App Streamlit Repository is ready!"
echo "Happy coding! 🎯" 