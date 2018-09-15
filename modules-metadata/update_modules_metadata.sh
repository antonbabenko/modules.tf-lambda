#!/usr/bin/env bash

declare -a MODULES=(rds
ec2-instance
elb
alb
autoscaling
sns
sqs
vpc)

MODULES_DIR=/Users/Bob/Sites/terraform-aws-modules

for module in "${MODULES[@]}"; do
    # hcltool comes from https://github.com/virtuald/pyhcl/blob/master/scripts/hcltool
    hcltool ${MODULES_DIR}/terraform-aws-${module}/variables.tf | jq -r '.variable' > ${module}_variables.json

    jq -s '.[0] * .[1]' ${module}_variables.json ${module}_cloudcraft.json > ${module}.json
done
