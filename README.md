# modules.tf - Infrastructure as code generator - from visual diagrams to Terraform

This repository contains code for AWS Lambda function which accepts URL to blueprint json file from Cloudcraft and returns zip-archive with Terraform infrastructure as code.

This code is deployed and available for everyone:
* [Sign up for free](https://cloudcraft.co/signup) or [login](https://cloudcraft.co/app) to [Cloudcraft](https://cloudcraft.co/app)
* Visualize your cloud architecture (like a pro)
* Click "Export" and "Export as code (modules.tf)"
* Unzip archive which you have just downloaded and read `README.md` file in it


to:
 * [lambda.modules.tf - production environment](https://lambda.modules.tf/)
 * [dev-lambda.modules.tf - dev environment](https://dev-lambda.modules.tf/)

Example input:
 * URL: https://cloudcraft.co/api/blueprint/bf0ad2c6-168f-4452-9add-cc4c869f910b
 * local file: blueprint.json

## High level picture

Sources:

 - A. Cloudcraft Blueprint (json)
 - B. Lucidchart API (if exists)
 - C. AWS API (Describe AWS-API or python script similar to the one by Lucidchart can generate json)
 - D. Custom json/hcl files
 - E. modules.tf UI produces json, which is sent to MTG endpoint
 - F. Cloudformation json/yaml
 - G. draw.io (can be self-hosted, and used by financial institutions)

All gets into modules.tf's generator (MTG) which creates "infrastructure as code (terragrunt + docs)"

# Mapping

Cloudcraft and modules.tf mapping of variables is defined in `modules-metadata/{module}.json` and updated by shell script `update_modules_metadata.sh`

isMultiAZ (cloudcraft) ==> multi_az (modules.tf) ==> multi_az (terraform-aws-modules)


## To-do

 - [x] Convert blueprint.json (cloudcraft) into generic json config for cookiecutter (output.json)
 - [x] Cookiecutter should render one directory with all content as specified in json config
 - [x] Create zip archive, upload it to S3
 - [x] Return content of zip file back to the user to initiate download
 - [x] Make content of archive real and usable
 - [x] Print only required key/values into terraform.tfvars
 - [x] Improve config generator to follow links/edges/etc
 - [ ] Get connections between (using data-sources):
    - [ ] ELB & ASG target_group_arns (Figure out how to pass dynamic value of target_group_arns (eg, ${data.terraform_remote_state.elb.arn}) to autoscaling group terraform module. Maybe using "locals", "overrides", etc)
    - [ ] S3 & Cloudfront
    - [x] ELB or ALB
 - [x] Generate real meta data from modules (or hardcode some)
 - [ ] Add basic S3 and Cloudfront modules

Before IPEXPO (19.8.2018):

 - [ ] Generate Terraform code instead of Terragrunt

Extract data from "nodes" and convert it into single "terraform-aws-module" + available arguments (instanceType, instanceSize, elbType)

## Notes

"A" get concept of "area/zone", which means it can be grouped into single "infrastructure module" before passing to modules.tf web-site and populate the forms or to modules.tf converter (MTC) before sending to MTG.


### Output structure

```
project/
  eu-west-1/
    layer1/
      terraform.tfvars
    layer2/
      terraform.tfvars
    common.tfvars
    terraform.tfvars
  .gitignore
  LICENSE
  README.md
  ...
```

### Run pre-commit after code was rendered:

cd final

// iterate through all files:
pre-commit run -c $(pwd)/.pre-commit-config.yaml --files $(pwd)/eu-west-1/rds/terraform.tfvars
pre-commit run -c $(pwd)/.pre-commit-config.yaml --files $(pwd)/....

## I am developer - show me the code & let's ship it!

Ok, if you are a developer and want to contribute, this is really great because [I](https://github.com/antonbabenko) need your help:

- Report, triage and fix bugs
- Refactor code
- Improve documentation
- Implement new sources and workflows (now only [Cloudcraft](https://cloudcraft.co/app) is partially supported)
- Consider contributing to [Terraform AWS modules](https://github.com/terraform-aws-modules) if you familiar with Terraform already

### Getting started

[AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html) supports Python 3.6, so you should use it also. Run this to install all required packages:

```
$ pip install -r requirements.txt
```

[Serverless framework](https://serverless.com) is used to do heavy-lifting by packaging dependencies required for AWS Lambda function (`requirements-lambda.txt`) and updating the code there. Read through [Quick Start guide](https://serverless.com/framework/docs/providers/aws/guide/quick-start/), as well as [installation](https://serverless.com/framework/docs/providers/aws/guide/installation/), [various AWS functions](https://serverless.com/framework/docs/providers/aws/guide/functions/), [serverless.yml reference](https://serverless.com/framework/docs/providers/aws/guide/serverless.yml/) to familiarise yourself with the usage of the framework.

As a short cheatsheet, you will need to use these commands:

* Invoke function locally providing `input.json`:

```
$ serverless invoke local --function generate-cloudcraft --path test_fixtures/input_localfile.json
```

* Deploy all functions to `prod` environment:

```
$ serverless deploy --stage prod
```

* Deploy single function to `dev` environment:

```
$ serverless deploy function --function generate-cloudcraft --stage dev
```

* Deploy single function to `prod` environment:

```
$ serverless deploy function --function generate-cloudcraft --stage prod
```

## Authors

This project is created and maintained by [Anton Babenko](https://github.com/antonbabenko) with the help from different contributors.

Remember to sign up for [Cloudcraft](https://cloudcraft.co/app) account and visualize your cloud architecture like a pro! This project would probably not exist without it.

The authors and contributors to this content cannot guarantee the validity of the information found here. Please make sure that you understand that the information provided here is being provided freely, and that no kind of agreement or contract is created between you and any persons associated with this content or project. The authors and contributors do not assume and hereby disclaim any liability to any party for any loss, damage, or disruption caused by errors or omissions in the information contained in, associated with, or linked from this content, whether such errors or omissions result from negligence, accident, or any other cause.

## License

This work is licensed under MIT License. See LICENSE for full details.

Copyright (c) 2018 Anton Babenko