terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.primary_region
}

# VPC Network
resource "google_compute_network" "proxy_rot_vpc" {
  name                    = "proxy-rot-network"
  auto_create_subnetworks = false
  description             = "PROXY ROT - IP Rotation Network"
}

# Subnets in multiple regions for IP rotation
resource "google_compute_subnetwork" "proxy_rot_subnet" {
  for_each = var.regions
  
  name          = "proxy-rot-subnet-${each.key}"
  ip_cidr_range = each.value.cidr
  region        = each.key
  network       = google_compute_network.proxy_rot_vpc.id
  
  description = "PROXY ROT subnet for ${each.key}"
  
  private_ip_google_access = true
}

# Cloud Router for each region
resource "google_compute_router" "proxy_rot_router" {
  for_each = var.regions
  
  name    = "proxy-rot-router-${each.key}"
  region  = each.key
  network = google_compute_network.proxy_rot_vpc.id
  
  description = "PROXY ROT router for NAT in ${each.key}"
}

# Reserve multiple external IPs per region for rotation
resource "google_compute_address" "nat_ips" {
  for_each = {
    for idx, item in flatten([
      for region_key, region in var.regions : [
        for ip_idx in range(region.num_nat_ips) : {
          key       = "${region_key}-ip-${ip_idx}"
          region    = region_key
          ip_number = ip_idx
        }
      ]
    ]) : item.key => item
  }
  
  name         = "proxy-rot-nat-ip-${each.value.region}-${each.value.ip_number}"
  region       = each.value.region
  address_type = "EXTERNAL"
  
  description = "PROXY ROT NAT IP ${each.value.ip_number} for ${each.value.region}"
}

# Cloud NAT with multiple IPs for rotation
resource "google_compute_router_nat" "proxy_rot_nat" {
  for_each = var.regions
  
  name   = "proxy-rot-nat-${each.key}"
  router = google_compute_router.proxy_rot_router[each.key].name
  region = each.key
  
  nat_ip_allocate_option = "MANUAL_ONLY"
  
  # Assign multiple external IPs for this region
  nat_ips = [
    for ip in google_compute_address.nat_ips : ip.self_link
    if startswith(ip.name, "proxy-rot-nat-ip-${each.key}-")
  ]
  
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  
  # Enable dynamic port allocation for better performance
  enable_dynamic_port_allocation = true
  
  min_ports_per_vm = 64
  max_ports_per_vm = 512
  
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Firewall rules
resource "google_compute_firewall" "allow_internal" {
  name    = "proxy-rot-allow-internal"
  network = google_compute_network.proxy_rot_vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  
  allow {
    protocol = "icmp"
  }
  
  source_ranges = [for subnet in google_compute_subnetwork.proxy_rot_subnet : subnet.ip_cidr_range]
  description   = "Allow internal traffic between subnets"
}

resource "google_compute_firewall" "allow_ssh" {
  name    = "proxy-rot-allow-ssh"
  network = google_compute_network.proxy_rot_vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["proxy-rot-instance"]
  description   = "Allow SSH access to instances"
}

# Compute instances in each region for proxy rotation
resource "google_compute_instance" "proxy_rot_instance" {
  for_each = var.regions
  
  name         = "proxy-rot-instance-${each.key}"
  machine_type = var.instance_machine_type
  zone         = each.value.zone
  
  tags = ["proxy-rot-instance"]
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 20
      type  = "pd-standard"
    }
  }
  
  network_interface {
    subnetwork = google_compute_subnetwork.proxy_rot_subnet[each.key].id
    # No external IP - traffic goes through Cloud NAT
  }
  
  metadata = {
    enable-oslogin = "TRUE"
  }
  
  metadata_startup_script = file("${path.module}/startup-script.sh")
  
  service_account {
    scopes = ["cloud-platform"]
  }
  
  allow_stopping_for_update = true
  
  labels = {
    environment = "proxy-rot"
    region      = each.key
  }
}

