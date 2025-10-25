variable "primary_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "target_endpoint" {
  description = "Target endpoint to proxy through API Gateway"
  type        = string
  default     = "https://httpbin.org"
}

variable "aws_profile" {
  description = "AWS CLI profile to use (optional)"
  type        = string
  default     = "default"
}

