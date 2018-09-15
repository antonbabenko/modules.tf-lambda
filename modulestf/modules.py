import json
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def load_local_json(relative_path):
    path = os.path.join(BASE_PATH, relative_path)
    with open(path) as file:
        return json.load(file)


MODULES = {
    "alb": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-alb.git",
        "variables": load_local_json("../modules-metadata/alb.json"),
    },
    "elb": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-elb.git",
        "variables": load_local_json("../modules-metadata/elb.json"),
    },
    "rds": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-rds.git",
        "variables": load_local_json("../modules-metadata/rds.json"),
    },
    "autoscaling": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-autoscaling.git",
        "variables": load_local_json("../modules-metadata/autoscaling.json"),
    },
    "ec2-instance": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-ec2-instance.git",
        "variables": load_local_json("../modules-metadata/ec2-instance.json"),
    },
    "sns": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-sns.git",
        "variables": load_local_json("../modules-metadata/sns.json"),
    },
    "sqs": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-sqs.git",
        "variables": load_local_json("../modules-metadata/sqs.json"),
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
