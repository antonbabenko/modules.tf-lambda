#!/usr/bin/env bash

# Locate the directory in which this script is located
readonly script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd $script_path

declare -a MODULES=(rds
rds-aurora
ec2-instance
elb
alb
autoscaling
security-group
sns
sqs
vpc
redshift
s3-bucket)
#cloudfront

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

    # Write module version
    pushd ${MODULES_DIR}/terraform-aws-${module} > /dev/null
    latest_tag=$(git describe --tags --abbrev=0)
    echo "$module => $latest_tag"
    popd > /dev/null

    echo -n $latest_tag > ${module}_version.txt

    echo "*********"
done
