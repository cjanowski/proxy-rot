# PROXY ROT - AWS API Gateway Infrastructure

Terraform configuration for IP rotation using AWS API Gateway across multiple regions.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PROXY ROT - AWS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Region: us-east-1                                          │
│  └─ API Gateway: https://xxx.execute-api.us-east-1.amazonaws.com │
│                                                             │
│  Region: us-east-2                                          │
│  └─ API Gateway: https://xxx.execute-api.us-east-2.amazonaws.com │
│                                                             │
│  Region: us-west-1                                          │
│  └─ API Gateway: https://xxx.execute-api.us-west-1.amazonaws.com │
│                                                             │
│  Region: us-west-2                                          │
│  └─ API Gateway: https://xxx.execute-api.us-west-2.amazonaws.com │
│                                                             │
│  Region: eu-west-1                                          │
│  └─ API Gateway: https://xxx.execute-api.eu-west-1.amazonaws.com │
│                                                             │
│  Total: 5 regional API Gateway endpoints                    │
└─────────────────────────────────────────────────────────────┘
```

## What Gets Created

- **5 API Gateway REST APIs** - One per region
- **1 IAM Role** - For API Gateway logging
- **5 API Deployments** - Production stages
- **5 Usage Plans** - With throttling (100 req/sec)
- **HTTP Proxy Integration** - Proxies to httpbin.org

## Prerequisites

1. **AWS Account** with active credentials
2. **AWS CLI** installed and configured
3. **Terraform** installed (>= 1.0)

## Quick Start

### Step 1: Configure AWS Credentials

```bash
aws configure
```

Enter your AWS Access Key ID and Secret Access Key.

### Step 2: Deploy Infrastructure

```bash
cd terraform-aws
./deploy.sh
```

### Step 3: Get Your Endpoints

```bash
terraform output api_endpoints_flat
```

## Deployment Time

- **Initial deployment**: ~5-10 minutes
- **Per region setup**: ~1-2 minutes
- **Total resources**: 20+ AWS resources

## Cost Estimate

**Free Tier:**
- First 1 million API Gateway requests per month: FREE
- First 12 months after AWS account creation

**Paid Pricing:**
- API Gateway: $3.50 per million requests
- Data transfer: $0.09/GB (first 10TB)

**Monthly estimate (after free tier):**
- Light usage (< 1M requests): **FREE**
- Medium usage (10M requests): **~$35/month**
- Heavy usage (100M requests): **~$350/month**

## How It Works

Each regional API Gateway acts as a proxy, rotating your requests through different AWS edge locations. Each region provides different IP addresses for your requests.

## Using with PROXY ROT

The Python script automatically works with these endpoints:

```bash
cd ..
./run.sh
```

Select **[1] AWS API Gateway** and the tool will use your deployed endpoints.

## Outputs

After deployment:

```bash
# Get all endpoints
terraform output api_endpoints

# Get flat list
terraform output api_endpoints_flat

# Get API IDs
terraform output api_ids

# Get summary
terraform output rotation_summary
```

## Configuration

Edit `terraform.tfvars` to customize:

```hcl
primary_region  = "us-east-1"
target_endpoint = "https://httpbin.org"  # Change to your target
aws_profile     = "default"
```

## Testing

Test one endpoint:

```bash
# Get an endpoint
ENDPOINT=$(terraform output -raw api_endpoints_flat | jq -r '.[0]')

# Make a test request
curl -X GET "$ENDPOINT/ip"
```

Test all endpoints:

```bash
# Test each region
for region in us-east-1 us-east-2 us-west-1 us-west-2 eu-west-1; do
  echo "Testing $region..."
  ENDPOINT=$(terraform output -json api_endpoints | jq -r ".\"$region\"")
  curl -s "$ENDPOINT/ip" | grep origin
done
```

## Regions

Default regions (can be modified in `main.tf`):
- **us-east-1** - US East (N. Virginia)
- **us-east-2** - US East (Ohio)
- **us-west-1** - US West (N. California)
- **us-west-2** - US West (Oregon)
- **eu-west-1** - Europe (Ireland)

## Adding More Regions

1. Add provider in `main.tf`:
```hcl
provider "aws" {
  alias  = "ap-southeast-1"
  region = "ap-southeast-1"
}
```

2. Add module:
```hcl
module "api_gateway_ap_southeast_1" {
  source = "./modules/api-gateway"
  
  providers = {
    aws = aws.ap-southeast-1
  }
  
  region_name      = "ap-southeast-1"
  target_endpoint  = var.target_endpoint
  api_gateway_role = aws_iam_role.api_gateway_role.arn
}
```

3. Update outputs in `outputs.tf`

4. Run: `terraform apply`

## Throttling & Limits

Default usage plan limits:
- **Rate limit**: 100 requests/second
- **Burst limit**: 500 requests

Modify in `modules/api-gateway/main.tf`:

```hcl
throttle_settings {
  burst_limit = 1000  # Increase burst
  rate_limit  = 200   # Increase rate
}
```

## Destroy Infrastructure

When done:

```bash
terraform destroy
```

Type `yes` to confirm. This removes all API Gateways and stops billing.

## Troubleshooting

**Error: Credentials not configured**
```bash
aws configure
```

**Error: Region not enabled**
- Some regions require manual enabling
- Go to: AWS Console → Account → Regions
- Enable the required region

**Error: Insufficient permissions**
- Ensure your IAM user has these permissions:
  - `apigateway:*`
  - `iam:CreateRole`
  - `iam:AttachRolePolicy`

**Error: Rate limit exceeded**
- Wait a few minutes
- AWS has rate limits on API creation
- Try again

## Security Notes

- API Gateway endpoints are public (by design for proxy rotation)
- No authentication required (designed for rotation)
- Consider adding API keys if needed for production use
- Usage plans provide basic rate limiting

## Advanced: Add API Keys

To add API key authentication, modify the module:

```hcl
# In modules/api-gateway/main.tf
resource "aws_api_gateway_method" "proxy_any" {
  # ... existing config ...
  authorization = "NONE"
  api_key_required = true  # Add this
}

# Create API key
resource "aws_api_gateway_api_key" "proxy_rot" {
  name = "proxy-rot-key-${var.region_name}"
}

# Associate with usage plan
resource "aws_api_gateway_usage_plan_key" "proxy_rot" {
  key_id        = aws_api_gateway_api_key.proxy_rot.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.proxy_rot.id
}
```

## Comparison: AWS vs GCP

| Feature | AWS API Gateway | GCP Cloud NAT |
|---------|----------------|---------------|
| Setup Time | 5-10 min | 10-15 min |
| Cost | $3.50/M requests | ~$50-60/month |
| Free Tier | 1M requests/month | Limited |
| IP Rotation | Per region | Per NAT IP |
| Total IPs | 5 (regions) | 15 (3 per region) |
| Best For | API proxying | Compute workloads |

---

**PROXY ROT** - Rotate AWS Style

