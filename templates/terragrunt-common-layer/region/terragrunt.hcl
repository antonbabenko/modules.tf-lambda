terraform {
  extra_arguments "common_vars" {
    commands = get_terraform_commands_that_need_vars()

    optional_var_files = [
      "${get_parent_terragrunt_dir()}/${path_relative_to_include()}/${find_in_parent_folders("regional.tfvars")}",
    ]
  }

  extra_arguments "disable_input" {
    commands  = get_terraform_commands_that_need_input()
    arguments = ["-input=false"]
  }

  after_hook "copy_common_main_providers" {
    commands = ["init-from-module"]
    execute  = ["cp", "${get_parent_terragrunt_dir()}/../common/main_providers.tf", "."]
  }

  //  Do not delete the copied file because of the odd behavior described in this related issue - https://github.com/gruntwork-io/terragrunt/issues/785
  //  after_hook "remove_useless_copy_of_main_providers" {
  //    commands = ["init"]
  //    execute  = ["rm", "-f", "${get_parent_terragrunt_dir()}/${path_relative_to_include()}/main_providers.tf"]
  //  }
}

remote_state {
  backend = "s3"
  disable_init = tobool(get_env("TERRAGRUNT_DISABLE_INIT", "false"))

  config = {
    encrypt        = true
    region         = "{{ cookiecutter.region }}"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    bucket         = "terraform-states-${get_aws_account_id()}"
    dynamodb_table = "terraform-locks-${get_aws_account_id()}"

    skip_metadata_api_check     = true
    skip_credentials_validation = true
  }
}
