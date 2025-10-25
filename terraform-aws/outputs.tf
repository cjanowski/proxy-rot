output "api_endpoints" {
  description = "All API Gateway endpoints for IP rotation"
  value = {
    us-east-1 = module.api_gateway_us_east_1.api_endpoint
    us-east-2 = module.api_gateway_us_east_2.api_endpoint
    us-west-1 = module.api_gateway_us_west_1.api_endpoint
    us-west-2 = module.api_gateway_us_west_2.api_endpoint
    eu-west-1 = module.api_gateway_eu_west_1.api_endpoint
  }
}

output "api_endpoints_flat" {
  description = "All API Gateway endpoints (flat list)"
  value = [
    module.api_gateway_us_east_1.api_endpoint,
    module.api_gateway_us_east_2.api_endpoint,
    module.api_gateway_us_west_1.api_endpoint,
    module.api_gateway_us_west_2.api_endpoint,
    module.api_gateway_eu_west_1.api_endpoint,
  ]
}

output "api_ids" {
  description = "API Gateway IDs by region"
  value = {
    us-east-1 = module.api_gateway_us_east_1.api_id
    us-east-2 = module.api_gateway_us_east_2.api_id
    us-west-1 = module.api_gateway_us_west_1.api_id
    us-west-2 = module.api_gateway_us_west_2.api_id
    eu-west-1 = module.api_gateway_eu_west_1.api_id
  }
}

output "total_endpoints" {
  description = "Total number of API Gateway endpoints"
  value       = 5
}

output "rotation_summary" {
  description = "Summary of AWS API Gateway setup"
  value = {
    total_regions  = 5
    total_endpoints = 5
    regions_active = ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "eu-west-1"]
    target_endpoint = var.target_endpoint
  }
}

