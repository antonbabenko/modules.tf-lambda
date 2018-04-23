# modules.tf-lambda

This repository contains AWS Lambda function which accepts URL to blueprint json file from Cloudcraft and returns zip-archive with infrastructure as code.

Input:
 * URL: https://cloudcraft.co/api/blueprint/bf0ad2c6-168f-4452-9add-cc4c869f910b
 * local file: blueprint.json

## High level picture

Sources:

 - A. Cloudcraft Blueprint (json)
 - B. Lucidchart API (if exists)
 - C. AWS API (Describe AWS-API or python script similar to the one by Lucidchart can generate json)
 - D. Custom json/hcl files
 - E. modules.tf UI produces json, which is sent to MTG endpoint

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
 - [ ] Improve config generator to follow links/edges/etc
 - [ ] Get connections between (using data-sources):
    - [ ] ELB & ASG (target_group_arns)
    - [ ] S3 & Cloudfront
    - [ ] ELB or ALB
 - [x] Generate real meta data from modules (or hardcode some)
 - [ ] Add basic S3 and Cloudfront modules

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

# Run locally:

serverless invoke local --function generate --path input.json

Or:

python3 handler.py

# Deploy to prod

serverless deploy --stage prod