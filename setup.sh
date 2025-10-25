#!/bin/bash
#
# PROXY ROT - Quick Setup Script
#

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║                  PROXY ROT SETUP                           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
echo "► Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3 first."
    echo "  Visit: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Found: $PYTHON_VERSION"
echo ""

# Check pip
echo "► Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo "✗ pip3 not found. Installing..."
    python3 -m ensurepip --upgrade
fi
echo "✓ pip3 is available"
echo ""

# Create virtual environment
echo "► Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment and install packages
echo "► Installing Python packages in virtual environment..."
echo "  This may take a minute..."
echo ""

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✓ All Python packages installed in virtual environment!"
echo ""

# Check AWS CLI (optional)
echo "► Checking AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version)
    echo "✓ Found: $AWS_VERSION"
else
    echo "⚠ AWS CLI not found (needed for AWS rotation mode)"
    echo "  Install with: brew install awscli"
    echo "  Or visit: https://aws.amazon.com/cli/"
fi
echo ""

# Check gcloud CLI (optional)
echo "► Checking gcloud CLI..."
if command -v gcloud &> /dev/null; then
    GCLOUD_VERSION=$(gcloud version --format="value(version)")
    echo "✓ Found: gcloud $GCLOUD_VERSION"
else
    echo "⚠ gcloud CLI not found (needed for GCP rotation mode)"
    echo "  Install with: brew install --cask google-cloud-sdk"
    echo "  Or visit: https://cloud.google.com/sdk/docs/install"
fi
echo ""

# Check Terraform (optional)
echo "► Checking Terraform..."
if command -v terraform &> /dev/null; then
    TF_VERSION=$(terraform version -json | python3 -c "import sys, json; print(json.load(sys.stdin)['terraform_version'])")
    echo "✓ Found: Terraform $TF_VERSION"
else
    echo "⚠ Terraform not found (needed for GCP infrastructure deployment)"
    echo "  Install with: brew install terraform"
    echo "  Or visit: https://www.terraform.io/downloads"
fi
echo ""

echo "════════════════════════════════════════════════════════════"
echo ""
echo "✓ PROXY ROT setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "  1. Run PROXY ROT:"
echo "     ./run.sh"
echo ""
echo "     Or manually:"
echo "     source venv/bin/activate"
echo "     python ip_rotator.py"
echo ""
echo "  2. For AWS rotation:"
echo "     - Install AWS CLI: brew install awscli"
echo "     - Configure: aws configure"
echo ""
echo "  3. For GCP rotation:"
echo "     - Install gcloud: brew install --cask google-cloud-sdk"
echo "     - Authenticate: gcloud auth application-default login"
echo "     - Deploy infra: cd terraform && ./deploy.sh"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

