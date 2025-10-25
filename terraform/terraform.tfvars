# PROXY ROT - GCP Configuration
# Project: boring

project_id     = "boring-01"
primary_region = "us-central1"

# Customize regions and number of NAT IPs per region
# Each region will get multiple external IPs for rotation
regions = {
  "us-central1" = {
    cidr        = "10.0.1.0/24"
    zone        = "us-central1-a"
    num_nat_ips = 3  # 3 different IPs will rotate
  }
  "us-east1" = {
    cidr        = "10.0.2.0/24"
    zone        = "us-east1-b"
    num_nat_ips = 3
  }
  "us-west1" = {
    cidr        = "10.0.3.0/24"
    zone        = "us-west1-a"
    num_nat_ips = 3
  }
  "europe-west1" = {
    cidr        = "10.0.4.0/24"
    zone        = "europe-west1-b"
    num_nat_ips = 3
  }
  "asia-east1" = {
    cidr        = "10.0.5.0/24"
    zone        = "asia-east1-a"
    num_nat_ips = 3
  }
}

# Use e2-micro for free tier eligibility
instance_machine_type = "e2-micro"

enable_api_logging = false

