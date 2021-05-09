terraform {
  required_version = ">= 0.15, <1.0.0"

  required_providers {
    aws = "~> 3.0"
  }

  backend "remote" {}
}

provider "aws" {
  region              = var.aws_region
  allowed_account_ids = var.allowed_account_ids
}

locals {
  zone_name   = trimsuffix(data.aws_route53_zone.this.name, ".")
  domain_name = join(".", compact([var.subdomain, local.zone_name]))

  dl_bucket_name = var.create_dl_bucket ? module.dl_bucket.s3_bucket_id : var.dl_bucket_name
  dl_dir         = trimsuffix(var.dl_dir, "/")

  tags = {
    Name = var.name
  }
}

data "aws_route53_zone" "this" {
  name         = var.zone_name
  private_zone = false
}

module "api_gateway" {
  source  = "terraform-aws-modules/apigateway-v2/aws"
  version = "~> 1.0"

  name          = var.name
  description   = "HTTP API Gateway"
  protocol_type = "HTTP"

  cors_configuration = {
    allow_headers = ["content-type", "x-amz-date", "authorization", "x-api-key", "x-amz-security-token", "x-amz-user-agent"]
    allow_methods = ["*"]
    allow_origins = ["*"]
  }

  domain_name                  = local.domain_name
  domain_name_certificate_arn  = module.acm.acm_certificate_arn
  disable_execute_api_endpoint = true

  integrations = {
    "GET /" = {
      lambda_arn             = module.lambda.lambda_function_arn
      payload_format_version = "2.0"
    }

    "POST /" = {
      lambda_arn             = module.lambda.lambda_function_arn
      payload_format_version = "2.0"
    }
  }

  tags = local.tags
}

module "lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 2.0"

  function_name = "${var.name}-lambda"
  description   = "Lambda function which converts blueprint into Terraform code"
  handler       = "handler.handler"
  runtime       = "python3.8"
  memory_size   = 3072
  timeout       = 30
  publish       = true

  source_path = "../src"

  environment_variables = {
    S3_BUCKET    = local.dl_bucket_name
    S3_DIR       = local.dl_dir
    UPLOAD_TO_S3 = true
  }

  attach_tracing_policy = true
  tracing_mode          = "Active"

  attach_policy_statements = true
  policy_statements = {
    s3 = {
      effect  = "Allow",
      actions = ["s3:PutObject*"],
      resources = [
        "arn:aws:s3:::${local.dl_bucket_name}/${local.dl_dir}",
        "arn:aws:s3:::${local.dl_bucket_name}/${local.dl_dir}/*",
      ]
    }
  }

  allowed_triggers = {
    AllowExecutionFromAPIGateway = {
      service    = "apigateway"
      source_arn = "${module.api_gateway.apigatewayv2_api_execution_arn}/*/*/"
    }
  }

  tags = local.tags
}

module "acm" {
  source  = "terraform-aws-modules/acm/aws"
  version = "~> 3.0"

  domain_name = local.zone_name
  # subject_alternative_names = ["${var.subdomain}.${local.zone_name}"]
  zone_id = data.aws_route53_zone.this.id

  tags = local.tags
}

module "dl_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 2.0"

  create_bucket = var.create_dl_bucket

  bucket              = var.dl_bucket_name
  acl                 = "private"
  force_destroy       = true
  block_public_policy = true

  cors_rule = [{
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
    allowed_headers = ["*"]
    max_age_seconds = 3000
  }]

  lifecycle_rule = [
    {
      id      = "delete-all-ancient"
      enabled = true

      expiration = {
        days = 365
      }
    }
  ]

  tags = local.tags
}

module "records" {
  source  = "terraform-aws-modules/route53/aws//modules/records"
  version = "~> 2.0"

  zone_id = data.aws_route53_zone.this.zone_id

  records = [
    {
      name = var.subdomain
      type = "A"
      alias = {
        name    = module.api_gateway.apigatewayv2_domain_name_configuration[0].target_domain_name
        zone_id = module.api_gateway.apigatewayv2_domain_name_configuration[0].hosted_zone_id
      }
    },
  ]
}
