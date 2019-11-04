# Infrastructure code for "{{ cookiecutter.source_name }}"

This repository contains Terraform infrastructure as Terraform code which was automatically generated from blueprint created using [cloudcraft.co](https://cloudcraft.co/app).

Infrastructure consists of multiple layers (
{%- for value in cookiecutter.dirs.values() -%}
{%- if loop.index < 4 -%}
{{ value }}{%- if loop.index < 4 -%}, {% endif -%}
{%- elif loop.index == 4 -%}...{%- endif -%}
{%- endfor -%}
) where each layer is configured using one of [Terraform AWS modules](https://github.com/terraform-aws-modules/) with arguments specified in `terraform.tfvars` in layer's directory.

[Terragrunt](https://github.com/gruntwork-io/terragrunt) is used to work with Terraform configurations which allows to orchestrate dependent layers, update arguments dynamically and keep configurations [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself).


## Pre-requirements

- [Terraform 0.12 or newer](https://www.terraform.io/)
- [Terragrunt 0.19 or newer](https://github.com/gruntwork-io/terragrunt)
- Optional: [pre-commit hooks](http://pre-commit.com) to keep Terraform formatting and documentation up-to-date

If you are using Mac you can install all dependencies using Homebrew:

    $ brew install terraform terragrunt pre-commit

By default, access credentials to AWS account should be set using environment variables:

    $ export AWS_DEFAULT_REGION={{ cookiecutter.region }}
    $ export AWS_ACCESS_KEY_ID=...
    $ export AWS_SECRET_ACCESS_KEY=...

Alternatively, you can edit `common/main_providers.tf` and use another authentication mechanism as described in [AWS provider documentation](https://www.terraform.io/docs/providers/aws/index.html#authentication).


## How to use it?

1. Configure access to AWS account
1. Create infrastructure
1. Update infrastructure


First, you should run `chmod +x common/scripts/update_dynamic_values_in_tfvars.sh`, review and specify all required arguments for each layer. Run this to see all errors:

    $ terragrunt validate-all --terragrunt-ignore-dependency-errors |& grep -C 3 "Error: "

Once all arguments are set, run this command to create infrastructure in all layers in a single region:

    $ cd {{ cookiecutter.region }}
    $ terragrunt apply-all

Alternatively, you can create infrastructure in a single layer (eg, `{{ cookiecutter.dirs.values()|first|default("vpc") }}`):

    $ cd {{ cookiecutter.region }}/{{ cookiecutter.dirs.values()|first|default("vpc") }}
    $ terragrunt apply

See [official Terragrunt documentation](https://github.com/gruntwork-io/terragrunt/blob/master/README.md) for all available commands and features.


## Found a bug? Or just want to help?

[modules.tf](https://github.com/antonbabenko/modules.tf-lambda) is an open source project.

If you found a bug - [open an issue](https://github.com/antonbabenko/modules.tf-lambda).

If you like this project, remember to share, star, like, tweet!

[![@antonbabenko](https://img.shields.io/twitter/follow/antonbabenko.svg?style=social&label=Follow%20@antonbabenko%20on%20Twitter)](https://twitter.com/antonbabenko)


## Copyrights and License

This code was generated using [modules.tf service](https://github.com/antonbabenko/modules.tf-lambda) which is maintained by [Anton Babenko](https://github.com/antonbabenko) and it uses [Terraform AWS modules](https://github.com/terraform-aws-modules/).

All content, including modules used in these configurations is released under the MIT License.
