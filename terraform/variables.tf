variable "allowed_account_ids" {
  description = "List of allowed AWS acount ids where infrastructure will be created"
  type        = list(string)
}

variable "aws_region" {
  description = "AWS region where infrastructure will be created"
  type        = string
  default     = "eu-west-1"
}

variable "name" {
  description = "Name or prefix for many related resources"
  type        = string
  default     = "modulestf-d2c"
}

variable "zone_name" {
  description = "Zone name for ALB and ACM"
  type        = string
}

variable "subdomain" {
  description = "Route53 subdomain"
  type        = string
  default     = ""
}

variable "create_dl_bucket" {
  description = "Whether to create S3 bucket for downloads"
  type        = bool
  default     = false
}

variable "dl_bucket_name" {
  description = "Name of S3 bucket for downloads (should not include route53_zone_name)"
  type        = string
  default     = null
}

variable "dl_dir" {
  description = "Name of directory in S3 bucket"
  type        = string
  default     = ""
}

variable "email" {
  description = "Email address to receive CloudWatch alerts"
  type        = string
}
