terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# REST API
resource "aws_api_gateway_rest_api" "proxy_rot" {
  name        = "proxy-rot-${var.region_name}"
  description = "PROXY ROT - IP Rotation API for ${var.region_name}"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Root resource proxy
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.proxy_rot.id
  parent_id   = aws_api_gateway_rest_api.proxy_rot.root_resource_id
  path_part   = "{proxy+}"
}

# ANY method for root
resource "aws_api_gateway_method" "root_any" {
  rest_api_id   = aws_api_gateway_rest_api.proxy_rot.id
  resource_id   = aws_api_gateway_rest_api.proxy_rot.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
  
  request_parameters = {
    "method.request.path.proxy" = false
  }
}

# ANY method for proxy resource
resource "aws_api_gateway_method" "proxy_any" {
  rest_api_id   = aws_api_gateway_rest_api.proxy_rot.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
  
  request_parameters = {
    "method.request.path.proxy" = true
  }
}

# HTTP Integration for root
resource "aws_api_gateway_integration" "root_integration" {
  rest_api_id = aws_api_gateway_rest_api.proxy_rot.id
  resource_id = aws_api_gateway_rest_api.proxy_rot.root_resource_id
  http_method = aws_api_gateway_method.root_any.http_method
  
  type                    = "HTTP_PROXY"
  integration_http_method = "ANY"
  uri                     = var.target_endpoint
  
  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
  }
}

# HTTP Integration for proxy
resource "aws_api_gateway_integration" "proxy_integration" {
  rest_api_id = aws_api_gateway_rest_api.proxy_rot.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy_any.http_method
  
  type                    = "HTTP_PROXY"
  integration_http_method = "ANY"
  uri                     = "${var.target_endpoint}/{proxy}"
  
  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
  }
}

# Deployment
resource "aws_api_gateway_deployment" "proxy_rot" {
  rest_api_id = aws_api_gateway_rest_api.proxy_rot.id
  
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.proxy.id,
      aws_api_gateway_method.root_any.id,
      aws_api_gateway_method.proxy_any.id,
      aws_api_gateway_integration.root_integration.id,
      aws_api_gateway_integration.proxy_integration.id,
    ]))
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# Stage
resource "aws_api_gateway_stage" "proxy_rot" {
  deployment_id = aws_api_gateway_deployment.proxy_rot.id
  rest_api_id   = aws_api_gateway_rest_api.proxy_rot.id
  stage_name    = "prod"
  
  description = "Production stage for PROXY ROT in ${var.region_name}"
}

# Usage Plan
resource "aws_api_gateway_usage_plan" "proxy_rot" {
  name        = "proxy-rot-${var.region_name}-usage-plan"
  description = "Usage plan for PROXY ROT in ${var.region_name}"
  
  api_stages {
    api_id = aws_api_gateway_rest_api.proxy_rot.id
    stage  = aws_api_gateway_stage.proxy_rot.stage_name
  }
  
  throttle_settings {
    burst_limit = 500
    rate_limit  = 100
  }
}

