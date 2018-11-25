provider "aws" {
  region = "{{ cookiecutter.region }}"

  # Make it faster by skipping something
  skip_get_ec2_platforms      = true
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
}

terraform {
  backend "s3" {}
}
