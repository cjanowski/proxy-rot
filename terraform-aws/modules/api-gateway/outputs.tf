output "api_id" {
  description = "ID of the API Gateway REST API"
  value       = aws_api_gateway_rest_api.proxy_rot.id
}

output "api_endpoint" {
  description = "Invoke URL for the API Gateway"
  value       = aws_api_gateway_stage.proxy_rot.invoke_url
}

output "api_name" {
  description = "Name of the API Gateway"
  value       = aws_api_gateway_rest_api.proxy_rot.name
}

output "stage_name" {
  description = "Stage name"
  value       = aws_api_gateway_stage.proxy_rot.stage_name
}

