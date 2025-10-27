# PROXY ROT

> IP Rotation Arsenal - A tactical CLI tool for AWS & GCP proxy rotation.

<img width="1512" height="982" alt="Screenshot 2025-10-27 at 8 16 46 AM" src="https://github.com/user-attachments/assets/57ec3855-3e0f-40b4-87db-329a9809f5c4" />

---

## Quick Start

### Step 1: Run Setup

```bash
./setup.sh
```

This creates a virtual environment and installs all dependencies automatically.

### Step 2: Configure Cloud Provider

**Option A: AWS (Recommended)**

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
```

Enter your AWS Access Key ID and Secret when prompted.

**Option B: GCP**

```bash
# Install gcloud CLI (if not already installed)
# Visit: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login
```

### Step 3: Run the Tool

```bash
./run.sh
```

Or manually:
```bash
source venv/bin/activate
python ip_rotator.py
```

### Step 4: Select Your Provider

```
  → Select provider [1/2/Q]:
```

- Press **1** for AWS API Gateway
- Press **2** for Google Cloud Platform  
- Press **Q** to quit

---

## What It Does

1. Rotates your IP address through different cloud endpoints
2. Makes 5 test requests to demonstrate IP rotation
3. Optionally exports all proxy IPs to `proxies.txt`
4. Displays response times and status codes with progress bar

---

## Export Option

After rotation completes, you'll be prompted to export your IPs:

**proxies.txt** - Clean IP list:
```
35.229.177.44
34.73.183.123
34.69.221.230
52.123.78.90
```

Features:
- One IP per line
- Perfect for importing into other tools
- No headers, just clean IP addresses
- Optional - you choose whether to export

---

## AWS Credentials

Get your AWS credentials:

1. Log into AWS Console
2. Go to **IAM** → **Users** → **Your User** → **Security Credentials**
3. Click **Create Access Key**
4. Choose **Command Line Interface (CLI)**
5. Copy the **Access Key ID** and **Secret Access Key**
6. Run `aws configure` and paste them when prompted

---

## GCP True IP Rotation (Terraform)

Want TRUE IP rotation on GCP with Cloud NAT? Got you covered!

### Quick Deploy

```bash
cd terraform
./deploy.sh
```

This creates:
- **15 rotating external IPs** across 5 regions
- **Cloud NAT gateways** for automatic rotation
- **Compute instances** ready for proxy work
- **Complete VPC infrastructure**

### Details

See `terraform/README.md` for full documentation including:
- Architecture diagram
- Cost estimates (~$50-60/month)
- Customization options
- Testing procedures

---

## Troubleshooting

**Error: AWS credentials not found**
- Run `aws configure` and enter your credentials

**Error: Module not found**
- Run `pip install -r requirements.txt`

**AWS Permission denied**
- Your IAM user needs API Gateway permissions

**AWS regions disabled**
- Go to AWS Console → Account → Regions
- Enable: us-east-1, us-west-2, or eu-west-1

**Connection timeout**
- Check your internet connection
- Try again (AWS API Gateway takes a moment to spin up)

**GCP infrastructure issues**
- See `terraform/README.md` for GCP-specific troubleshooting

---

## Cost Information

**AWS**: Free tier includes 1 million requests/month  
**GCP**: Variable costs based on compute usage

The tool automatically cleans up AWS resources when done.

---

## Support

For issues or questions, check the error messages in the terminal - they include helpful troubleshooting tips.
