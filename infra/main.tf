terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "buckets3-fraud-detection-system"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" { region = "us-east-1" }

variable "openai_api_key" {
  type      = string
  sensitive = true
}
variable "langsmith_project" {
  type      = string
  sensitive = true
}
variable "langsmith_api_key" {
  type      = string
  sensitive = true
}
variable "langchain_tracing_v2" {
  type      = string
  sensitive = true
}

# 1. Repositorio ECR 
resource "aws_ecr_repository" "repo" {
  name         = "fraud-detection-system"
  force_delete = true
}

# 2. Rol IAM para App Runner
resource "aws_iam_role" "app_runner_role" {
  name = "AppRunnerECRAccessRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "build.apprunner.amazonaws.com" }
    }]
  })
}
resource "aws_iam_role_policy_attachment" "attach" {
  role       = aws_iam_role.app_runner_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

# 3. App Runner
resource "aws_apprunner_service" "app" {
  service_name = "fraud-detection-system-service-v1"

  source_configuration {
    authentication_configuration { access_role_arn = aws_iam_role.app_runner_role.arn }
    
    auto_deployments_enabled = false 

    image_repository {
      image_identifier      = "${aws_ecr_repository.repo.repository_url}:latest"
      image_repository_type = "ECR"
      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          ENVIRONMENT = "production"
          OPENAI_API_KEY    = var.openai_api_key
          LANGSMITH_PROJECT    = var.langsmith_project
          LANGSMITH_API_KEY    = var.langsmith_api_key
          LANGCHAIN_TRACING_V2 = var.langchain_tracing_v2
        }
      }
    }
  }
  depends_on = [aws_ecr_repository.repo]
}

# 4. ECR para Frontend
resource "aws_ecr_repository" "frontend_repo" {
  name         = "fraud-detection-frontend"
  force_delete = true
}

resource "aws_apprunner_service" "frontend" {
  service_name = "fraud-detection-frontend-v1"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.app_runner_role.arn
    }

    auto_deployments_enabled = false

    image_repository {
      image_identifier      = "${aws_ecr_repository.frontend_repo.repository_url}:latest"
      image_repository_type = "ECR"

      image_configuration {
        port = "8501"

        runtime_environment_variables = {
          ENVIRONMENT       = "production"
          BACKEND_BASE_URL  = "https://${aws_apprunner_service.app.service_url}"
          STREAMLIT_SERVER_PORT                 = "8501"
          STREAMLIT_SERVER_ADDRESS              = "0.0.0.0"
          STREAMLIT_SERVER_HEADLESS             = "true"
          STREAMLIT_SERVER_ENABLE_CORS          = "false"
          STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION = "false"
          STREAMLIT_BROWSER_GATHER_USAGE_STATS  = "false"
          STREAMLIT_SERVER_ENABLE_WEBSOCKET_COMPRESSION = "false"
        }
      }
    }
  }

  network_configuration {
    ingress_configuration {
      is_publicly_accessible = true
    }
  }

  health_check_configuration {
    protocol = "HTTP"
    path     = "/_stcore/health"
  }

  depends_on = [
    aws_ecr_repository.frontend_repo,
    aws_apprunner_service.app
  ]
}


output "ecr_url" { value = aws_ecr_repository.repo.repository_url }
output "app_url" { value = aws_apprunner_service.app.service_url }
output "frontend_url" {
  value = aws_apprunner_service.frontend.service_url
}