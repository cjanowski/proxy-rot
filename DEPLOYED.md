# 🎉 PROXY ROT - DEPLOYED!

Your GCP infrastructure is LIVE and ready to rotate IPs!

## 🌐 Your Rotating IP Pool (15 IPs)

```
35.229.177.44      (us-central1)
35.221.175.117     (us-central1)
35.189.167.51      (us-central1)
34.79.246.226      (europe-west1)
35.205.253.176     (europe-west1)
34.52.150.103      (europe-west1)
34.69.221.230      (us-west1)
34.172.211.197     (us-west1)
34.45.209.48       (us-west1)
34.73.183.123      (us-east1)
34.75.13.49        (us-east1)
34.139.98.229      (us-east1)
34.82.203.161      (asia-east1)
136.118.39.154     (asia-east1)
34.182.24.207      (asia-east1)
```

## ⚡ Quick Test

### Option 1: Use PROXY ROT Python Script

```bash
python ip_rotator.py
```

Select **[2] Google Cloud Platform**

The script will automatically:
- Detect your deployed infrastructure
- Route requests through your GCP instances
- Rotate through all 15 IPs across 5 regions

### Option 2: Manual Test Script

```bash
./test_live_rotation.sh
```

This runs 15 requests showing TRUE IP rotation.

### Option 3: Test One Region

```bash
gcloud compute ssh proxy-rot-instance-us-central1 --zone=us-central1-a
sudo python3 /opt/proxy_test.py
```

## 🎯 How It Works

```
Your Request
    ↓
Python Script (ip_rotator.py)
    ↓
gcloud ssh → GCP Instance in Region X
    ↓
Cloud NAT (rotates through 3 IPs)
    ↓
Target Website (sees rotating IP)
```

Each region has **3 NAT IPs** that automatically rotate!

## 📊 Infrastructure Details

| Region | Zone | Instance | NAT IPs |
|--------|------|----------|---------|
| us-central1 | us-central1-a | proxy-rot-instance-us-central1 | 3 |
| us-east1 | us-east1-b | proxy-rot-instance-us-east1 | 3 |
| us-west1 | us-west1-a | proxy-rot-instance-us-west1 | 3 |
| europe-west1 | europe-west1-b | proxy-rot-instance-europe-west1 | 3 |
| asia-east1 | asia-east1-a | proxy-rot-instance-asia-east1 | 3 |

**Total: 5 regions × 3 IPs = 15 rotating IPs**

## 💰 Cost Breakdown

- **Cloud NAT**: ~$5.40/month (5 gateways @ $0.045/hr)
- **Static IPs**: ~$43/month (15 IPs @ $0.004/hr)
- **Compute**: ~$3-5/month (e2-micro instances)
- **Egress**: Variable (first 1GB free/month)

**Total: ~$50-60/month**

## 🛠️ Management Commands

### Check Infrastructure Status

```bash
cd terraform
terraform show
```

### Get All IPs Again

```bash
cd terraform
terraform output nat_external_ips_flat
```

### Stop Instances (Save Money)

```bash
# Stop all instances (keeps IPs, reduces cost)
for region in us-central1 us-east1 us-west1 europe-west1 asia-east1; do
  gcloud compute instances stop proxy-rot-instance-$region --zone=${region}-a
done
```

### Start Instances

```bash
# Start when needed
for region in us-central1 us-east1 us-west1 europe-west1 asia-east1; do
  gcloud compute instances start proxy-rot-instance-$region --zone=${region}-a
done
```

### Destroy Everything

```bash
cd terraform
terraform destroy
```

## 🔥 Usage Examples

### Example 1: Python Script with GCP

```bash
python ip_rotator.py
```

Output shows different IPs from your pool:
```
→ Request #1/5 - Region: us-central1
  IP Address: 35.229.177.44

→ Request #2/5 - Region: us-east1
  IP Address: 34.73.183.123

→ Request #3/5 - Region: us-west1
  IP Address: 34.69.221.230
```

### Example 2: Direct SSH Test

```bash
# Test us-central1
gcloud compute ssh proxy-rot-instance-us-central1 --zone=us-central1-a \
  --command="curl -s https://httpbin.org/ip"

# Test europe-west1
gcloud compute ssh proxy-rot-instance-europe-west1 --zone=europe-west1-b \
  --command="curl -s https://httpbin.org/ip"
```

### Example 3: Bulk Testing

```bash
# Make 10 requests to see rotation
for i in {1..10}; do
  echo "Request $i:"
  gcloud compute ssh proxy-rot-instance-us-central1 --zone=us-central1-a \
    --command="curl -s https://httpbin.org/ip | grep origin"
  sleep 1
done
```

Watch the IPs rotate through: 35.229.177.44 → 35.221.175.117 → 35.189.167.51 → repeat

## 🎨 Customization

Want different configuration? Edit `terraform/terraform.tfvars`:

### Use Only 2 Regions (Lower Cost)

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

Then: `cd terraform && terraform apply`

### Add More IPs Per Region

```hcl
"us-central1" = {
  cidr        = "10.0.1.0/24"
  zone        = "us-central1-a"
  num_nat_ips = 5  # Instead of 3
}
```

## 📝 Next Steps

1. **Test it**: Run `./test_live_rotation.sh`
2. **Use it**: Run `python ip_rotator.py` and select GCP
3. **Export IPs**: When prompted, export to CSV or TXT
4. **Monitor costs**: Check GCP Console → Billing

## 🛡️ Security Notes

- All instances have **no external IPs** (more secure)
- Traffic goes through **Cloud NAT** only
- SSH access via **IAP** (Identity-Aware Proxy)
- Firewall rules restrict internal traffic

## 🚨 Troubleshooting

**Can't SSH into instances?**
```bash
gcloud compute config-ssh
```

**gcloud not authenticated?**
```bash
gcloud auth login
gcloud config set project boring-01
```

**Python script not using GCP instances?**
- Ensure gcloud CLI is installed
- Ensure you're authenticated
- The script auto-detects gcloud availability

---

**PROXY ROT** - Deployed, Locked, Loaded! 🔥

