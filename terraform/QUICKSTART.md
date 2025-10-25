# PROXY ROT - Terraform Quick Reference

## One-Line Deploy

```bash
cd terraform && ./deploy.sh
```

## Manual Deploy

```bash
# Authenticate
gcloud auth application-default login
gcloud config set project boring-01

# Enable APIs
gcloud services enable compute.googleapis.com
gcloud services enable servicenetworking.googleapis.com

# Deploy
terraform init
terraform plan
terraform apply
```

## Get Your IPs

```bash
# All IPs in one list
terraform output nat_external_ips_flat

# IPs grouped by region
terraform output nat_external_ips

# Summary
terraform output rotation_summary
```

## Test Rotation

```bash
# Automated test across all regions
./test_rotation.sh

# Manual test on one instance
gcloud compute ssh proxy-rot-instance-us-central1 --zone=us-central1-a
sudo python3 /opt/proxy_test.py
```

## Common Commands

```bash
# Check what's deployed
terraform show

# List all resources
terraform state list

# Refresh outputs
terraform refresh

# Modify infrastructure
# Edit terraform.tfvars, then:
terraform apply

# Destroy everything
terraform destroy
```

## Cost Management

```bash
# Stop all instances (keeps IPs, lowers cost)
for region in us-central1 us-east1 us-west1 europe-west1 asia-east1; do
  gcloud compute instances stop proxy-rot-instance-$region --zone=${region}-a
done

# Start instances when needed
for region in us-central1 us-east1 us-west1 europe-west1 asia-east1; do
  gcloud compute instances start proxy-rot-instance-$region --zone=${region}-a
done

# Delete everything
terraform destroy
```

## Customization

### Use Fewer Regions (Lower Cost)

Edit `terraform.tfvars`:

```hcl
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

Then: `terraform apply`

### Change Instance Size

Edit `terraform.tfvars`:

```hcl
instance_machine_type = "e2-small"  # or e2-medium
```

Then: `terraform apply`

## Troubleshooting

**Error: Project not found**
```bash
gcloud config set project boring-01
```

**Error: API not enabled**
```bash
gcloud services enable compute.googleapis.com
```

**Error: Quota exceeded**
```bash
# Check quotas
gcloud compute project-info describe --project=boring-01

# Request increase via GCP Console
```

**Can't SSH into instance**
```bash
# Use IAP tunnel
gcloud compute ssh proxy-rot-instance-us-central1 \
  --zone=us-central1-a \
  --tunnel-through-iap
```

## Architecture Summary

```
15 External IPs
    ↓
5 Cloud NAT Gateways (3 IPs each)
    ↓
5 Cloud Routers
    ↓
5 Regional Subnets
    ↓
1 Global VPC
    ↓
5 Compute Instances
```

## Outputs Explained

| Output | Description |
|--------|-------------|
| `nat_external_ips` | IPs grouped by region |
| `nat_external_ips_flat` | All IPs in one list |
| `total_nat_ips` | Total number of IPs |
| `instance_names` | Instance names by region |
| `instance_zones` | Instance zones |
| `rotation_summary` | Quick summary |

---

**PROXY ROT** - Deploy, Rotate, Dominate

