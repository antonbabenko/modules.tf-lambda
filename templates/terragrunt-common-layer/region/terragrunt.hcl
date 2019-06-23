terraform {
  extra_arguments "common_vars" {
    commands = get_terraform_commands_that_need_vars()

    optional_var_files = [
      "${get_parent_terragrunt_dir()}/terraform.tfvars",
    ]
  }

  extra_arguments "disable_input" {
    commands  = get_terraform_commands_that_need_input()
    arguments = ["-input=false"]
  }

  after_hook "copy_common_main_providers" {
    commands = ["init-from-module"]
    execute  = ["cp", "${get_parent_terragrunt_dir()}/../../common/main_providers.tf", "."]
  }

  after_hook "remove_useless_copy_of_main_providers" {
    commands = ["init"]
    execute  = ["rm", "-f", "${get_parent_terragrunt_dir()}/${path_relative_to_include()}/main_providers.tf"]
  }

//  # Expecting terraform.tfvars which is not required in terragrunt 0.19
//  before_hook "update_dynamic_values_in_tfvars" {
//    commands = ["apply", "import", "plan", "refresh"]
//    execute  = ["tfvars-annotations", "${get_parent_terragrunt_dir()}/${path_relative_to_include()}"]
//  }
}

remote_state {
  backend = "s3"

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
