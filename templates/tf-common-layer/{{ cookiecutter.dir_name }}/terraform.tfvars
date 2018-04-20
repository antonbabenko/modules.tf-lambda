terragrunt = {
  terraform {
    extra_arguments "common_vars" {
      commands = ["${get_terraform_commands_that_need_vars()}"]

      required_var_files = [
        "${get_parent_tfvars_dir()}/${path_relative_to_include()}/${find_in_parent_folders("regional.tfvars")}",
        "${get_parent_tfvars_dir()}/common.tfvars",
        "${get_env("TF_VAR_local_environment", "terraform")}.tfvars",
      ]
    }

    extra_arguments "disable_input" {
      commands  = ["${get_terraform_commands_that_need_input()}"]
      arguments = ["-input=false"]
    }

    extra_arguments "reconfigure_backend_on_init" {
      commands  = ["init"]
      arguments = ["-reconfigure"]
    }

    after_hook "copy_common_main_variables" {
      commands = ["init"]
      execute  = ["cp", "${get_parent_tfvars_dir()}/../common/main_variables.tf", "."]
    }

    after_hook "copy_common_main_providers" {
      commands = ["init"]
      execute  = ["${get_parent_tfvars_dir()}/../common/scripts/cp.sh", "${get_parent_tfvars_dir()}/../common/main_providers.tf"]
    }
  }

  remote_state {
    backend = "s3"

    config {
      encrypt        = true
      region         = "eu-west-1"
      key            = "${path_relative_to_include()}/${get_env("TF_VAR_local_environment", "terraform")}.tfstate"
      bucket         = "terraform-states-${get_aws_account_id()}"
      dynamodb_table = "terraform-locks-${get_aws_account_id()}"

      skip_requesting_account_id  = "true"
      skip_get_ec2_platforms      = "true"
      skip_metadata_api_check     = "true"
      skip_region_validation      = "true"
      skip_credentials_validation = "true"
    }
  }
}
