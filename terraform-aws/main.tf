terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Default provider (primary region)
provider "aws" {
  region = var.primary_region
  
  default_tags {
    tags = {
      Project     = "proxy-rot"
      Environment = "production"
      ManagedBy   = "terraform"
    }
  }
}

# Additional providers for each region
provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
}

provider "aws" {
  alias  = "us-east-2"
  region = "us-east-2"
}

provider "aws" {
  alias  = "us-west-1"
  region = "us-west-1"
}

provider "aws" {
  alias  = "us-west-2"
  region = "us-west-2"
}

provider "aws" {
  alias  = "eu-west-1"
  region = "eu-west-1"
}

# IAM Role for API Gateway
resource "aws_iam_role" "api_gateway_role" {
  name = "proxy-rot-api-gateway-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for API Gateway CloudWatch Logs
resource "aws_iam_role_policy" "api_gateway_policy" {
  name = "proxy-rot-api-gateway-policy"
  role = aws_iam_role.api_gateway_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# API Gateway in us-east-1
module "api_gateway_us_east_1" {
  source = "./modules/api-gateway"
  
  providers = {
    aws = aws.us-east-1
  }
  
  region_name      = "us-east-1"
  target_endpoint  = var.target_endpoint
  api_gateway_role = aws_iam_role.api_gateway_role.arn
}

# API Gateway in us-east-2
module "api_gateway_us_east_2" {
  source = "./modules/api-gateway"
  
  providers = {
    aws = aws.us-east-2
  }
  
  region_name      = "us-east-2"
  target_endpoint  = var.target_endpoint
  api_gateway_role = aws_iam_role.api_gateway_role.arn
}

# API Gateway in us-west-1
module "api_gateway_us_west_1" {
  source = "./modules/api-gateway"
  
  providers = {
    aws = aws.us-west-1
  }
  
  region_name      = "us-west-1"
  target_endpoint  = var.target_endpoint
  api_gateway_role = aws_iam_role.api_gateway_role.arn
}

# API Gateway in us-west-2
module "api_gateway_us_west_2" {
  source = "./modules/api-gateway"
  
  providers = {
    aws = aws.us-west-2
  }
  
  region_name      = "us-west-2"
  target_endpoint  = var.target_endpoint
  api_gateway_role = aws_iam_role.api_gateway_role.arn
}

# API Gateway in eu-west-1
module "api_gateway_eu_west_1" {
  source = "./modules/api-gateway"
  
  providers = {
    aws = aws.eu-west-1
  }
  
  region_name      = "eu-west-1"
  target_endpoint  = var.target_endpoint
  api_gateway_role = aws_iam_role.api_gateway_role.arn
}

