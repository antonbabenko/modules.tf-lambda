# Infrastructure code for "{{ cookiecutter.source_name }}"

This repository contains Terraform configuration files which were automatically generated from blueprint created using [Cloudcraft](https://www.cloudcraft.co).

[Terragrunt](https://terragrunt.gruntwork.io/) is used to work with Terraform configurations which allows to orchestrate dependent layers, update arguments dynamically and keep configurations [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself).

## Table of Contents

1. [Quick start](#quick-start)
1. [Configure access to AWS account](#configure-access-to-aws-account)
1. [Create and manage your infrastructure](#create-and-manage-your-infrastructure)
1. [References](#references)
1. [About d2c.modules.tf](#about-d2cmodulestf)


## Quick start

1. [Install Terraform 0.15 or newer](https://learn.hashicorp.com/tutorials/terraform/install-cli)
1. [Install Terragrunt 0.29 or newer](https://terragrunt.gruntwork.io/docs/getting-started/install/)
1. Optionally, [install pre-commit hooks](https://pre-commit.com/#install) to keep Terraform formatting and documentation up-to-date.

If you are using macOS you can install all dependencies using [Homebrew](https://brew.sh/):

    $ brew install terraform terragrunt pre-commit

## Configure access to AWS account

The recommended way to configure access credentials to AWS account is using environment variables:

```
$ export AWS_DEFAULT_REGION={{ cookiecutter.region }}
$ export AWS_ACCESS_KEY_ID=...
$ export AWS_SECRET_ACCESS_KEY=...
```

Alternatively, you can edit `terragrunt.hcl` and use another authentication mechanism as described in [AWS provider documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs#authentication).

## Create and manage your infrastructure

Infrastructure consists of multiple layers (
{%- for value in cookiecutter.dirs.values() -%}
{%- if loop.index < 4 -%}
{{ value }}{%- if loop.index < 4 and not loop.last -%}, {% endif -%}
{%- elif loop.index == 4 -%}...{%- endif -%}
{%- endfor -%}
) where each layer is described using one [Terraform module](https://www.terraform.io/docs/configuration/modules.html) with `inputs` arguments specified in `terragrunt.hcl` in respective layer's directory.

Navigate through layers to review and customize values inside `inputs` block.

There are two ways to manage infrastructure (slower&complete, or faster&granular):
- **Region as a whole (slower&complete).** Run this command to create infrastructure in all layers in a single region:

```
$ cd {{ cookiecutter.region }}
$ terragrunt run-all apply
```

- **As a single layer (faster&granular).** Run this command to create infrastructure in a single layer (eg, `{{ cookiecutter.dirs.values()|first|default("vpc") }}`):

```
$ cd {{ cookiecutter.region }}/{{ cookiecutter.dirs.values()|first|default("vpc") }}
$ terragrunt apply
```

After the confirmation your infrastructure should be created.


## References

* [Terraform documentation](https://www.terraform.io/docs/) and [Terragrunt documentation](https://terragrunt.gruntwork.io/docs/) for all available commands and features
* [Terraform AWS modules](https://github.com/terraform-aws-modules/)
* [Terraform modules registry](https://registry.terraform.io/)
* [Terraform best practices](https://www.terraform-best-practices.com/)


## About d2c.modules.tf

[modules.tf](https://github.com/antonbabenko/modules.tf-lambda) is an open-source project created by [Anton Babenko](https://github.com/antonbabenko):
1. Questions, bugs and feature-requests - [open an issue](https://github.com/antonbabenko/modules.tf-lambda).
1. [Become a sponsor to @antonbabenko](https://github.com/sponsors/antonbabenko/).
1. You are always welcome to share, star, like, tweet, follow!

[![@antonbabenko](https://img.shields.io/twitter/follow/antonbabenko.svg?style=flat&label=Follow%20@antonbabenko%20on%20Twitter)](https://twitter.com/antonbabenko) 
[![@antonbabenko](https://img.shields.io/github/followers/antonbabenko?style=flat&label=Follow%20@antonbabenko%20on%20Github)](https://github.com/antonbabenko) 
[![modules.tf-lambda](https://img.shields.io/github/stars/antonbabenko/modules.tf-lambda?style=flat&label=Star%20modules.tf-lambda%20on%20Github)](https://github.com/antonbabenko/modules.tf-lambda)

All content, including [Terraform AWS modules](https://github.com/terraform-aws-modules/) used in these configurations, is released under the MIT or Apache License.
