# Infrastructure as code for "{{ cookiecutter.source["name"] }}"

This directory contains automatically generated Terraform infrastructure as code for the blueprint which was created using [cloudcraft.co](https://cloudcraft.co/app).

## Table of content

- Getting started
- How it works?
- Found a bug? Or just want to help?
- Copyrights and License

## Getting started

These configurations are **potentially** working out of the box but it is very likely that you will want to customize parameters.

Make sure that you install these tools:

- [Terraform 0.11.7 or newer](https://www.terraform.io/)
- [Terragrunt 0.14.7 or newer](https://github.com/gruntwork-io/terragrunt)

Optional dependencies:

- [pre-commit hooks](http://pre-commit.com) - keeps formatting and documentation up-to-date

@todo: describe how to use this and provide helper script:
1. Install all deps based on OS (Mac)
1. Verify that all deps are installed (incl. AWS credentials)
1. Verify that all values were set in all layers?
1. Ask which command user wants to run: single layer or all layers (apply-all)?
1. Run it
1. Exit (ask to tweet)

## How it works?

Infrastructure consists of multiple layers (eg, autoscaling, rds, s3) where each layer is configured using exactly one [Terraform AWS modules](https://github.com/terraform-aws-modules/) with the values specified in `terraform.tfvars` located in layer's directory.

Run this command to create or update infrastructure in all layers in single region (`eu-west-1`, for eg):

    $ cd eu-west-1
    $ terragrunt apply-all

Alternatively you can work on a single layer at the time:

    $ cd eu-west-1/elb   # for example
    $ terragrunt apply

See [Terragrunt documentation](https://github.com/gruntwork-io/terragrunt/blob/master/README.md) for more details about commands and workflow.


## Found a bug? Or just want to help?

[modules.tf](https://github.com/antonbabenko/modules.tf-lambda) is a new and open source project which benefits from users like you!

If you find a bug - [open an issue](https://github.com/antonbabenko/modules.tf-lambda).


## Copyrights and License

This code was generated using [modules.tf service](https://github.com/antonbabenko/modules.tf-lambda) which is maintained by [Anton Babenko](https://github.com/antonbabenko) and it uses [Terraform AWS modules](https://github.com/terraform-aws-modules/).

All content, including modules used in these configurations is released under the MIT License.
