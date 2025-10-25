output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "vpc_network_name" {
  description = "VPC Network name"
  value       = google_compute_network.proxy_rot_vpc.name
}

output "nat_external_ips" {
  description = "All external NAT IPs for rotation (by region)"
  value = {
    for region_key in keys(var.regions) : region_key => [
      for ip_key, ip in google_compute_address.nat_ips : ip.address
      if startswith(ip.name, "proxy-rot-nat-ip-${region_key}-")
    ]
  }
}

output "nat_external_ips_flat" {
  description = "All external NAT IPs (flat list)"
  value       = [for ip in google_compute_address.nat_ips : ip.address]
}

output "instance_names" {
  description = "Names of proxy rotation instances"
  value       = { for k, v in google_compute_instance.proxy_rot_instance : k => v.name }
}

output "instance_zones" {
  description = "Zones of proxy rotation instances"
  value       = { for k, v in google_compute_instance.proxy_rot_instance : k => v.zone }
}

output "instance_internal_ips" {
  description = "Internal IPs of proxy rotation instances"
  value = {
    for k, v in google_compute_instance.proxy_rot_instance : k => v.network_interface[0].network_ip
  }
}

output "total_nat_ips" {
  description = "Total number of NAT IPs available for rotation"
  value       = length(google_compute_address.nat_ips)
}

output "rotation_summary" {
  description = "Summary of IP rotation setup"
  value = {
    total_regions  = length(var.regions)
    total_nat_ips  = length(google_compute_address.nat_ips)
    regions_active = keys(var.regions)
  }
}

