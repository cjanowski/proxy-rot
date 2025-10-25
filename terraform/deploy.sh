#!/bin/bash
#
# PROXY ROT - GCP Infrastructure Deployment Script
#

set -e

PROJECT_ID="boring-01"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║                    PROXY ROT DEPLOY                        ║"
echo "║              GCP Infrastructure Setup                      ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "✗ [ERROR] gcloud CLI not found. Please install it first."
    echo "  Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "✗ [ERROR] Terraform not found. Please install it first."
    echo "  Visit: https://www.terraform.io/downloads"
    exit 1
fi

echo "✓ [SUCCESS] Prerequisites check passed"
echo ""

# Set project
echo "► [INFO] Setting GCP project: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"
echo ""

# Enable required APIs
echo "► [INFO] Enabling required GCP APIs..."
echo "         This may take a few minutes..."
echo ""

gcloud services enable compute.googleapis.com --project="$PROJECT_ID"
gcloud services enable servicenetworking.googleapis.com --project="$PROJECT_ID"

echo ""
echo "✓ [SUCCESS] APIs enabled"
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
echo "Ready to deploy PROXY ROT infrastructure!"
echo ""
echo "This will create:"
echo "  • 5 regions with Cloud NAT"
echo "  • 15 external IP addresses"
echo "  • 5 compute instances"
echo "  • VPC network and subnets"
echo ""
echo "Estimated cost: ~\$50-60/month"
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
echo "         This will take 10-15 minutes..."
echo ""

terraform apply tfplan

rm -f tfplan

echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "✓ [SUCCESS] PROXY ROT infrastructure deployed!"
echo ""
echo "Your rotating IPs:"
terraform output nat_external_ips_flat
echo ""
echo "Total NAT IPs available:"
terraform output total_nat_ips
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. SSH into an instance:"
echo "     gcloud compute ssh proxy-rot-instance-us-central1 --zone=us-central1-a"
echo ""
echo "  2. Test IP rotation:"
echo "     sudo python3 /opt/proxy_test.py"
echo ""
echo "  3. Update your PROXY ROT Python script to use these instances"
echo ""
echo "To destroy infrastructure later:"
echo "  cd terraform && terraform destroy"
echo ""

