import json
import os
from pprint import pprint

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_version(relative_path, remove_v=False):
    path = os.path.join(BASE_PATH, relative_path)
    with open(path) as file:
        if remove_v:
            return file.read().replace("v", "")
        else:
            return file.read()


def load_local_json(relative_path):
    path = os.path.join(BASE_PATH, relative_path)
    with open(path) as file:
        return json.load(file)


# @todo: Verify support for tuple, object and any.
# Ref: https://www.terraform.io/docs/configuration/variables.html#type-constraints
def update_template_variables(var):
    for key, value in var.items():

        # Guess type from default value
        if value.get("default", None) is not None:
            if str(value.get("default")).lower() in ["true", "false"]:
                value_type = value.get("type", "bool")
            elif type(value.get("default")) is map:
                value_type = value.get("type", "map")
            elif type(value.get("default")) is str:
                value_type = value.get("type", "string")
            elif type(value.get("default")) is int:
                value_type = value.get("type", "integer")
            else:
                value_type = value.get("type", "list")
        else:
            value_type = value.get("type", "string")

        variable_value_format_function = ""

        if value_type == "string":
            variable_default = ''
            variable_value_format = '"%s"'
        elif value_type == "number":
            variable_default = ''
            variable_value_format = '%s'
        elif value_type == "bool":
            variable_default = ''
            variable_value_format = '%s'
            variable_value_format_function = "lower"
        elif value_type.startswith("list") or value_type.startswith("set"):
            variable_default = []
            variable_value_format = '%s'
        elif value_type.startswith("map"):
            variable_default = {}
            variable_value_format = '"%s"'
        else:
            variable_default = '""'
            variable_value_format = "%s"

        value.update({
            "value_type": value_type,
            "variable_default": variable_default,
            "variable_value_format": variable_value_format,
            "variable_value_format_function": variable_value_format_function,
        })

    return var


MODULES = {
    "alb": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-alb.git?ref=" + get_version("../terraform-aws-modules-metadata/alb_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/" + get_version("../terraform-aws-modules-metadata/alb_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/alb.json")),
    },
    "nlb": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-alb.git?ref=" + get_version("../terraform-aws-modules-metadata/alb_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/alb/aws/" + get_version("../terraform-aws-modules-metadata/alb_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/alb.json")),
    },
    "elb": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-elb.git?ref=" + get_version("../terraform-aws-modules-metadata/elb_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/elb/aws/" + get_version("../terraform-aws-modules-metadata/elb_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/elb.json")),
    },
    "rds": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-rds.git?ref=" + get_version("../terraform-aws-modules-metadata/rds_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/" + get_version("../terraform-aws-modules-metadata/rds_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/rds.json")),
    },
    "rds-aurora": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-rds-aurora.git?ref=" + get_version("../terraform-aws-modules-metadata/rds-aurora_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/rds-aurora/aws/" + get_version("../terraform-aws-modules-metadata/rds-aurora_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/rds-aurora.json")),
    },
    "autoscaling": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-autoscaling.git?ref=" + get_version("../terraform-aws-modules-metadata/autoscaling_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/autoscaling/aws/" + get_version("../terraform-aws-modules-metadata/autoscaling_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/autoscaling.json")),
    },
    "ec2-instance": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-ec2-instance.git?ref=" + get_version("../terraform-aws-modules-metadata/ec2-instance_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/ec2-instance/aws/" + get_version("../terraform-aws-modules-metadata/ec2-instance_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/ec2-instance.json")),
    },
    "sns": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-sns.git?ref=" + get_version("../terraform-aws-modules-metadata/sns_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/sns/aws/" + get_version("../terraform-aws-modules-metadata/sns_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/sns.json")),
    },
    "sqs": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-sqs.git?ref=" + get_version("../terraform-aws-modules-metadata/sqs_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/sqs/aws/" + get_version("../terraform-aws-modules-metadata/sqs_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/sqs.json")),
    },
    "security-group": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-security-group.git?ref=" + get_version("../terraform-aws-modules-metadata/security-group_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/" + get_version("../terraform-aws-modules-metadata/security-group_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/security-group.json")),
    },
    "vpc": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-vpc.git?ref=" + get_version("../terraform-aws-modules-metadata/vpc_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/" + get_version("../terraform-aws-modules-metadata/vpc_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/vpc.json")),
    },
    "s3-bucket": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-s3-bucket.git?ref=" + get_version("../terraform-aws-modules-metadata/s3-bucket_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/s3-bucket/aws/" + get_version("../terraform-aws-modules-metadata/s3-bucket_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/s3-bucket.json")),
    },
    "redshift": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-redshift.git?ref=" + get_version("../terraform-aws-modules-metadata/redshift_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/redshift/aws/" + get_version("../terraform-aws-modules-metadata/redshift_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/redshift.json")),
    },
    "dynamodb-table": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-dynamodb-table.git?ref=" + get_version("../terraform-aws-modules-metadata/dynamodb-table_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/dynamodb-table/aws/" + get_version("../terraform-aws-modules-metadata/dynamodb-table_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/dynamodb-table.json")),
    },
    "cloudfront": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-cloudfront.git?ref=" + get_version("../terraform-aws-modules-metadata/cloudfront_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/cloudfront/aws/" + get_version("../terraform-aws-modules-metadata/cloudfront_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/cloudfront.json")),
    },
    "lambda": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-lambda.git?ref=" + get_version("../terraform-aws-modules-metadata/lambda_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/" + get_version("../terraform-aws-modules-metadata/lambda_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/lambda.json")),
    },
    "apigateway-v2": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-apigateway-v2.git?ref=" + get_version("../terraform-aws-modules-metadata/apigateway-v2_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/apigateway-v2/aws/" + get_version("../terraform-aws-modules-metadata/apigateway-v2_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/apigateway-v2.json")),
    },
    "vpn-gateway": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-vpn-gateway.git?ref=" + get_version("../terraform-aws-modules-metadata/vpn-gateway_version.txt"),
        "registry_url": "https://registry.terraform.io/modules/terraform-aws-modules/vpn-gateway/aws/" + get_version("../terraform-aws-modules-metadata/vpn-gateway_version.txt", True),
        "variables": update_template_variables(load_local_json("../terraform-aws-modules-metadata/vpn-gateway.json")),
    },

    # Data sources for aws_region and aws_availability_zones
    "aws-data": {
        "source": "${get_parent_terragrunt_dir()}/../../modules/aws-data",
        "registry_url": "",
        "variables": {},
    },
}

# pprint(MODULES["rds-aurora"])
