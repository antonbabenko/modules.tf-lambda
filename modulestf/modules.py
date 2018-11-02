import json
import os
from pprint import pprint

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def load_local_json(relative_path):
    path = os.path.join(BASE_PATH, relative_path)
    with open(path) as file:
        return json.load(file)


def update_template_variables(var):
    for key, value in var.items():
        if value.get("default", None) is not None:
            if str(value.get("default")).lower() in ["true", "false"]:
                value_type = value.get("type", "bool")
            elif type(value.get("default")) is map:
                value_type = value.get("type", "map")
            elif type(value.get("default")) is str:
                value_type = value.get("type", "string")
            elif type(value.get("default")) is int:
                value_type = value.get("type", "string")
            else:
                value_type = value.get("type", "list")
        else:
            value_type = value.get("type", "string")

        variable_value_format_function = ""

        if value_type == "string":
            variable_default = ''
            variable_value_format = '"%s"'
        elif value_type == "int":
            variable_default = ''
            variable_value_format = '%s'
        elif value_type == "bool":
            variable_default = ''
            variable_value_format = '%s'
            variable_value_format_function = "lower"
        elif value_type in ["list", "set"]:
            variable_default = []
            variable_value_format = '%s'
        elif value_type == "map":
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
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-alb.git",
        "variables": update_template_variables(load_local_json("../modules-metadata/alb.json")),
    },
    "elb": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-elb.git",
        "variables": update_template_variables(load_local_json("../modules-metadata/elb.json")),
    },
    "rds": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-rds.git",
        "variables": update_template_variables(load_local_json("../modules-metadata/rds.json")),
    },
    "autoscaling": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-autoscaling.git",
        "variables": update_template_variables(load_local_json("../modules-metadata/autoscaling.json")),
    },
    "ec2-instance": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-ec2-instance.git",
        "variables": update_template_variables(load_local_json("../modules-metadata/ec2-instance.json")),
    },
    "sns": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-sns.git",
        "variables": update_template_variables(load_local_json("../modules-metadata/sns.json")),
    },
    "sqs": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-sqs.git",
        "variables": update_template_variables(load_local_json("../modules-metadata/sqs.json")),
    },
    "security-group": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-security-group.git",
        "variables": update_template_variables(load_local_json("../modules-metadata/security-group.json")),
    },
    "vpc": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-vpc.git",
        "variables": update_template_variables(load_local_json("../modules-metadata/vpc.json")),
    },
    "s3": {
        "source": "terraform-aws-modules/s3/aws",
        "variables": {},
    },
    "cloudfront": {
        "source": "terraform-aws-modules/cloudfront/aws",
        "variables": {},
    },
}
