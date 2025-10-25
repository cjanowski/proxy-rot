variable "region_name" {
  description = "AWS region name for this API Gateway"
  type        = string
}

variable "target_endpoint" {
  description = "Target endpoint to proxy requests to"
  type        = string
}

variable "api_gateway_role" {
  description = "IAM role ARN for API Gateway"
  type        = string
}

