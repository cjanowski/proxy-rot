variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "boring-01"
}

variable "primary_region" {
  description = "Primary GCP region"
  type        = string
  default     = "us-central1"
}

variable "regions" {
  description = "Map of regions with their configuration for IP rotation"
  type = map(object({
    cidr        = string
    zone        = string
    num_nat_ips = number
  }))
  
  default = {
    "us-central1" = {
      cidr        = "10.0.1.0/24"
      zone        = "us-central1-a"
      num_nat_ips = 3  # 3 external IPs for rotation
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
}

variable "instance_machine_type" {
  description = "Machine type for proxy instances"
  type        = string
  default     = "e2-micro"  # Free tier eligible
}

variable "enable_api_logging" {
  description = "Enable detailed API logging"
  type        = bool
  default     = false
}

