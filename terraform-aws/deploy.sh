#!/bin/bash
#
# PROXY ROT - AWS API Gateway Deployment Script
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║                PROXY ROT DEPLOY - AWS                      ║"
echo "║            API Gateway Infrastructure Setup                ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "✗ [ERROR] Terraform not found. Please install it first."
    echo "  Visit: https://www.terraform.io/downloads"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "✗ [ERROR] AWS CLI not found. Please install it first."
    echo "  Install: brew install awscli"
    echo "  Or visit: https://aws.amazon.com/cli/"
    exit 1
fi

echo "✓ [SUCCESS] Prerequisites check passed"
echo ""

# Check AWS credentials
echo "► [INFO] Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "✗ [ERROR] AWS credentials not configured"
    echo "  Run: aws configure"
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_USER=$(aws sts get-caller-identity --query Arn --output text)
echo "✓ [SUCCESS] Authenticated as: $AWS_USER"
echo "            Account: $AWS_ACCOUNT"
echo ""

# Initialize Terraform
cd "$SCRIPT_DIR"

if [ ! -d ".terraform" ]; then
    echo "► [INFO] Initializing Terraform..."
    terraform init
    echo ""
fi

echo "✓ [SUCCESS] Terraform initialized"
echo ""

# Terraform plan
echo "► [INFO] Generating Terraform plan..."
echo ""
terraform plan -out=tfplan
echo ""

# Prompt for confirmation
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Ready to deploy PROXY ROT AWS infrastructure!"
echo ""
echo "This will create:"
echo "  • 5 API Gateway endpoints (one per region)"
echo "  • IAM roles for API Gateway"
echo "  • Usage plans and throttling"
echo ""
echo "Regions:"
echo "  • us-east-1"
echo "  • us-east-2"
echo "  • us-west-1"
echo "  • us-west-2"
echo "  • eu-west-1"
echo ""
echo "Estimated cost: ~\$3.50 per million requests"
echo "                (Free tier: 1 million requests/month)"
echo ""
read -p "→ Deploy infrastructure? [y/N]: " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "✗ [INFO] Deployment cancelled"
    rm -f tfplan
    exit 0
fi

echo ""
echo "► [INFO] Deploying infrastructure..."
echo "         This will take 5-10 minutes..."
echo ""

terraform apply tfplan

rm -f tfplan

echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "✓ [SUCCESS] PROXY ROT AWS infrastructure deployed!"
echo ""
echo "Your API Gateway endpoints:"
terraform output api_endpoints_flat
echo ""
echo "Total endpoints:"
terraform output total_endpoints
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Run PROXY ROT:"
echo "     cd .. && ./run.sh"
echo ""
echo "  2. Select AWS (option 1)"
echo ""
echo "  3. The tool will automatically use these endpoints"
echo ""
echo "To destroy infrastructure later:"
echo "  cd terraform-aws && terraform destroy"
echo ""

