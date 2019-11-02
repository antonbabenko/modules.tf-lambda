#!/usr/bin/env bash

declare -a MODULES=(rds
ec2-instance
elb
alb
autoscaling
security-group
sns
sqs
vpc
s3-bucket)

MODULES_DIR=/Users/Bob/Sites/terraform-aws-modules

for module in "${MODULES[@]}"; do

    # Can't append extension for mktemp, so renaming instead
    tmp_file=$(mktemp "${TMPDIR:-/tmp}/terraform-hcl2-XXXXXXXXXX")
    mv "$tmp_file" "$tmp_file.tf"
    tmp_file_tf="$tmp_file.tf"

    # GNU AWK is required
    awk -f "terraform_hcl2.awk" ${MODULES_DIR}/terraform-aws-${module}/*.tf > "$tmp_file_tf"

    # hcltool comes from https://github.com/virtuald/pyhcl/blob/master/scripts/hcltool
    hcltool "$tmp_file_tf" | jq -r '.variable' > ${module}_variables.json

    jq -s '.[0] * .[1]' ${module}_variables.json ${module}_cloudcraft.json > ${module}.json

    rm -f "$tmp_file_tf"
done
