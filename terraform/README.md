# PROXY ROT - GCP Infrastructure

Terraform configuration for true IP rotation using GCP Cloud NAT with multiple external IPs.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PROXY ROT - GCP                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Region: us-central1                                        │
│  ├─ Cloud NAT                                               │
│  │  ├─ External IP #1: xxx.xxx.xxx.xxx                      │
│  │  ├─ External IP #2: xxx.xxx.xxx.xxx                      │
│  │  └─ External IP #3: xxx.xxx.xxx.xxx                      │
│  └─ Compute Instance (no external IP)                       │
│                                                             │
│  Region: us-east1                                           │
│  ├─ Cloud NAT                                               │
│  │  ├─ External IP #1: xxx.xxx.xxx.xxx                      │
│  │  ├─ External IP #2: xxx.xxx.xxx.xxx                      │
│  │  └─ External IP #3: xxx.xxx.xxx.xxx                      │
│  └─ Compute Instance (no external IP)                       │
│                                                             │
│  ... and 3 more regions                                     │
│                                                             │
│  Total: 5 regions × 3 IPs = 15 rotating IPs                 │
└─────────────────────────────────────────────────────────────┘
```

## What Gets Created

- **1 VPC Network** - Global network for proxy rotation
- **5 Regional Subnets** - One per region
- **5 Cloud Routers** - One per region for NAT
- **5 Cloud NAT Gateways** - With multiple IPs each
- **15 External IPs** - Reserved for rotation (3 per region)
- **5 Compute Instances** - e2-micro instances (free tier eligible)
- **Firewall Rules** - Internal traffic and SSH access

## Prerequisites

1. **GCP Account** with billing enabled
2. **Project ID**: `boring-01`
3. **gcloud CLI** installed and authenticated
4. **Terraform** installed (>= 1.0)

## Quick Start

### Step 1: Authenticate with GCP

```bash
gcloud auth application-default login
gcloud config set project boring-01
```

### Step 2: Enable Required APIs

```bash
gcloud services enable compute.googleapis.com
gcloud services enable servicenetworking.googleapis.com
```

### Step 3: Initialize Terraform

```bash
cd terraform
terraform init
```

### Step 4: Review the Plan

```bash
terraform plan
```

### Step 5: Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted.

## Deployment Time

- **Initial deployment**: ~10-15 minutes
- **Per region setup**: ~2-3 minutes
- **Total resources**: 30+ GCP resources

## Outputs

After deployment, you'll see:

```
nat_external_ips_flat = [
  "35.123.45.67",
  "35.123.45.68",
  "35.123.45.69",
  "34.234.56.78",
  ...
]

total_nat_ips = 15
```

All 15 IPs are now available for rotation!

## Using with PROXY ROT

The Python script will automatically use these NAT IPs when making requests from GCP instances.

To SSH into an instance and test:

```bash
# Get instance name
terraform output instance_names

# SSH into instance
gcloud compute ssh proxy-rot-instance-us-central1 --zone=us-central1-a

# Run test script
sudo python3 /opt/proxy_test.py
```

## Cost Estimate

**Free Tier Eligible:**
- e2-micro instances (1 per region in US regions)
- 1 GB egress per month

**Paid Resources:**
- Cloud NAT: ~$0.045/hour per gateway = ~$5.40/month (5 gateways)
- External IPs: $0.004/hour per IP = ~$43/month (15 IPs)
- Egress traffic: $0.12/GB after free tier

**Estimated Total: ~$50-60/month**

To reduce costs:
- Use fewer regions (modify `terraform.tfvars`)
- Use fewer NAT IPs per region
- Delete when not in use: `terraform destroy`

## Configuration

Edit `terraform.tfvars` to customize:

```hcl
# Use only 2 regions with 2 IPs each = 4 rotating IPs
regions = {
  "us-central1" = {
    cidr        = "10.0.1.0/24"
    zone        = "us-central1-a"
    num_nat_ips = 2
  }
  "us-east1" = {
    cidr        = "10.0.2.0/24"
    zone        = "us-east1-b"
    num_nat_ips = 2
  }
}
```

## Testing IP Rotation

From any instance:

```bash
# Test 1: Check your external IP
curl https://httpbin.org/ip

# Test 2: Run multiple requests (IPs will rotate)
for i in {1..10}; do
  echo "Request $i:"
  curl -s https://httpbin.org/ip | grep origin
  sleep 1
done
```

Cloud NAT automatically rotates through your assigned IPs!

## Destroy Infrastructure

When done:

```bash
terraform destroy
```

Type `yes` to confirm. This removes all resources and stops billing.

## Troubleshooting

**Error: API not enabled**
```bash
gcloud services enable compute.googleapis.com
```

**Error: Quota exceeded**
- Check GCP quotas in Console → IAM → Quotas
- Request quota increase if needed

**Error: Permission denied**
- Ensure your account has Compute Admin role
- Check project ID is correct: `boring-01`

## Security Notes

- Instances have no external IPs (more secure)
- All traffic goes through Cloud NAT
- SSH access via IAP (Identity-Aware Proxy)
- Firewall rules restrict access

## Advanced: Add More Regions

Edit `terraform.tfvars` and add:

```hcl
"southamerica-east1" = {
  cidr        = "10.0.6.0/24"
  zone        = "southamerica-east1-a"
  num_nat_ips = 3
}
```

Then run: `terraform apply`

---

**PROXY ROT** - Rotate or Die

