terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "fraude-bcp-terraform-state-khael" # <--- TU BUCKET S3 AQUÍ
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" { region = "us-east-1" }

# 1. Repositorio ECR 
resource "aws_ecr_repository" "repo" {
  name         = "fraude-bcp-repo"
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
  service_name = "fraude-detector-api"

  source_configuration {
    authentication_configuration { access_role_arn = aws_iam_role.app_runner_role.arn }
    
    auto_deployments_enabled = true 

    image_repository {
      image_identifier      = "${aws_ecr_repository.repo.repository_url}:latest"
      image_repository_type = "ECR"
      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          ENVIRONMENT = "production"
        }
      }
    }
  }
  depends_on = [aws_ecr_repository.repo]
}

output "ecr_url" { value = aws_ecr_repository.repo.repository_url }
output "app_url" { value = aws_apprunner_service.app.service_url }