#!/usr/bin/env python3

from __future__ import print_function

import base64
import glob
import json
import boto3
import os
import shutil
import uuid
from hashlib import md5
from pprint import pprint
import requests

import sys
from cookiecutter.main import cookiecutter


# @todo: generate variables and outputs arrays from real modules

MODULES = {
    "elb": {
        "source": "terraform-aws-modules/elb/aws",
        "variables": {
            "name": {
                "description": "The name of the ELB",
            },
            "security_groups": {
                "description": "A list of security group IDs to assign to the ELB",
                "type": "list",
            },
            "subnets": {
                "description": "A list of subnet IDs to attach to the ELB",
                "type": "list",
            },
            "internal": {
                "description": "If true, ELB will be an internal ELB"
            }
        },
        "outputs": {},
    },
    "rds": {
        "source": "terraform-aws-modules/rds/aws",
        "variables": {},
        "outputs": {},
    },
    "autoscaling": {
        "source": "terraform-aws-modules/autoscaling/aws",
        "variables": {},
        "outputs": {},
    },
    "ec2-instance": {
        "source": "terraform-aws-modules/ec2-instance/aws",
        "variables": {},
        "outputs": {},
    },
    "s3": {
        # "source": "terraform-aws-modules/s3/aws",
        "source": "terraform-aws-modules/security-group/aws",
        "variables": {},
        "outputs": {},
    },
    "cloudfront": {
        # "source": "terraform-aws-modules/cloudfront/aws",
        "source": "terraform-aws-modules/security-group/aws",
        "variables": {},
        "outputs": {},
    },
}

COOKIECUTTER_DIR_SINGLE_LAYER = os.getcwd() + "/cookiecutter/tf-single-layer"
COOKIECUTTER_DIR_COMMON_LAYER = os.getcwd() + "/cookiecutter/tf-common-layer"
COOKIECUTTER_DIR_ROOT = os.getcwd() + "/cookiecutter/tf-root"

# >>>>>> This ---> 1. blueprint json TO modules.tf array    + cookiecutter
# 2. modules.tf json TO complete zip
# or: blueprint json to complete zip

try:
    if os.environ['IS_LOCAL']:
        cookiecutter_root = os.getcwd()
except KeyError:
    cookiecutter_root = sys.path[0]

tmp_dir = "/tmp"

blueprint_file = "input/blueprint.json"
# blueprint_file = "real-examples/example1.json"

def scan_data(data):
    # We don't care about these keys in json: connectors, surfaces, images, icons, text
    data_nodes = data["data"]["nodes"]
    data_edges = data["data"]["edges"]
    data_groups = data["data"]["groups"]

    global nodes
    nodes = dict()
    for node in data_nodes:
        nodes[node["id"]] = node

    global asg_groups
    asg_groups = dict()
    for group in data_groups:
        if group["type"] == "asg":
            asg_groups[group["id"]] = group["nodes"]

    global edges      # edges are uni-directional (from => to)
    edges = dict()      # edges are uni-directional (from => to)

    global edges_rev  # edges_rev are reversed (to => from). Used by RDS nodes (master/slave).
    edges_rev = dict()  # edges_rev are reversed (to => from). Used by RDS nodes (master/slave).
    for edge in data_edges:
        if edge["from"] not in edges:
            edges[edge["from"]] = set()
        edges[edge["from"]].add(edge["to"])

        if edge["to"] not in edges_rev:
            edges_rev[edge["to"]] = set()
        edges_rev[edge["to"]].add(edge["from"])

    # pprint(edges)
    # pprint(edges_rev)


# Get nodes or ASG id which has edges TO other nodes
def get_edge_nodes_by_id(id):
    tmp_nodes = dict()

    if id not in edges:
        # pprint("NOT in SET %s" % (id))
        return tmp_nodes

    for edge_id in edges[id]:
        if edge_id in nodes:
            tmp_nodes[edge_id] = nodes[edge_id]

        if edge_id in asg_groups:
            tmp_nodes[edge_id] = asg_groups[edge_id]

    return tmp_nodes


# Get nodes which has edges FROM other nodes
def get_edge_rev_nodes_by_id(id):

    tmp_nodes = dict()

    if id not in edges_rev:
        # pprint("EDGES_REV NOT in SET %s" % (id))
        return tmp_nodes

    for edge_id in edges_rev[id]:
        if edge_id in nodes:
            tmp_nodes[edge_id] = nodes[edge_id]

    return tmp_nodes


def render_single_layer(resource):

    single_layer = {
        "dir_name": "single_layer/eu-west-1/" + resource["type"] + "_" + resource["ref_id"],
        "module_source": MODULES[resource["type"]]["source"],
    }

    extra_context = resource.update(single_layer) or resource

    cookiecutter(COOKIECUTTER_DIR_SINGLE_LAYER,
                 config_file=os.path.join(cookiecutter_root,"cookiecutter/config_aws_lambda.yaml"),
                 no_input=True,
                 extra_context=extra_context)


def render_common_layer():

    common_layer = {
        "dir_name": "common_layer",
    }

    cookiecutter(COOKIECUTTER_DIR_COMMON_LAYER,
                 config_file=os.path.join(cookiecutter_root,"cookiecutter/config_aws_lambda.yaml"),
                 no_input=True,
                 extra_context=common_layer)


def render_root_dir():

    root_dir = {
        "dir_name": "root_dir",
    }

    cookiecutter(COOKIECUTTER_DIR_ROOT,
                 config_file=os.path.join(cookiecutter_root,"cookiecutter/config_aws_lambda.yaml"),
                 no_input=True,
                 extra_context=root_dir)


def generate_from_cloudcraft(event, context):
    qs = event.get("queryStringParameters")

    blueprint_url = qs.get("cloudcraft")
    localfile = qs.get("localfile")

    if blueprint_url:
        r = requests.get(blueprint_url)
        data = r.json()
    elif localfile:
        file = open(localfile, 'r')
        data = json.load(file)
    else:
        raise ValueError("'cloudcraft' or 'localfile' query string parameter should be defined")

    print("event = ")
    print(json.dumps(event))

    scan_data(data)

    resources = list()
    parsed_asg_id = set()
    parsed_rds_id = set()
    for id, node in nodes.items():

        # if node["type"] not in ["elb"]:
        #     continue

        # print(id)
        pprint("-------")
        print(node["type"])

        edge_nodes = get_edge_nodes_by_id(id)
        edge_rev_nodes = get_edge_rev_nodes_by_id(id)
        pprint(edge_nodes)
        pprint(edge_rev_nodes)

        if node["type"] == "rds":
            is_multi_az = False
            z = edge_nodes.update(edge_rev_nodes) or edge_nodes
            for connected_id, connected_node in z.items():
                if connected_node["type"] == "rds" and \
                        connected_node["engine"] == node["engine"] and \
                        connected_node["role"] == ("master" if node["role"] == "slave" else "slave"):
                    master_rds_id = (id if node["role"] == "master" else connected_id)
                    is_multi_az = True

            rds_id = master_rds_id if is_multi_az else id

            pprint(rds_id)

            if rds_id not in parsed_rds_id:
                resources.append({
                    "type": "rds",
                    "ref_id": rds_id,
                    "params": {
                        "engine": node["engine"],
                        "instanceType": node["instanceType"]+"."+node["instanceSize"],
                        "isMultiAZ": is_multi_az
                    }
                })
            parsed_rds_id.add(rds_id)

        if node["type"] == "ec2":
            is_asg = False
            for asg_id, asg_nodes in asg_groups.items():
                if id in asg_nodes:
                    is_asg = True
                    break

            if is_asg:
                if asg_id not in parsed_asg_id:
                    resources.append({
                        "type": "autoscaling",
                        "ref_id": asg_id,
                        "params": {
                            "instanceType": node["instanceType"]+"."+node["instanceSize"],
                        }
                    })
                parsed_asg_id.add(asg_id)
            else:
                # @todo: verify when instances without ASG are used
                resources.append({
                    "type": "ec2-instance",
                    "ref_id": id,
                    "params": {
                        "instanceType": node["instanceType"]+"."+node["instanceSize"],
                    }
                })

        if node["type"] == "elb":
            is_alb = node["elbType"] == "application"
            is_asg = False

            for asg_id in edge_nodes.keys():
                if asg_id in asg_groups.keys():
                    is_asg = True
                    break

            resources.append({
                "type": "elb",
                "ref_id": id,
                "params": {
                    "alb": is_alb,
                    "asg_id": asg_id if is_asg else None,
                }
            })

        if node["type"] == "s3":
            # pprint(node)

            resources.append({
                "type": "s3",
                "ref_id": id,
                "params": {
                }
            })

        if node["type"] == "cloudfront":
            # @todo: go through graph of connections towards S3
            # pprint(id)
            # pprint(edge_nodes)
            # pprint(edge_rev_nodes)

            resources.append({
                "type": "s3",
                "ref_id": id,
                "params": {
                }
            })

    pprint("-START------------------------------------")
    pprint(resources)
    pprint("-END------------------------------------")

    output_dir = os.path.join(tmp_dir, "output")
    try:
        os.mkdir(output_dir)
    except OSError:
        pass

    os.chdir(output_dir)

    # create output directory
    working_dir = blueprint_file.replace("/", "_")

    try:
        shutil.rmtree(working_dir)
    except FileNotFoundError:
        pass

    try:
        os.mkdir(working_dir)
    except OSError:
        pass

    os.chdir(working_dir)

    with open('output.json', 'w') as f:
        f.write(json.dumps(resources))


    # render single layers in a loop
    for resource in resources:
        render_single_layer(resource)

    render_common_layer()
    render_root_dir()

    # combine_rendered_output
    final_dir = "final"

    try:
        os.mkdir(final_dir)
    except OSError:
        pass

    for file in glob.glob("single_layer/*"):
        shutil.move(file, "final")

    for file in glob.glob("common_layer/*"):
        shutil.move(file, "final")

    for file in glob.glob("root_dir/*"):
        shutil.move(file, "final")

    # Make zip archive
    shutil.make_archive("archive", "zip", "final")

    # Upload it to S3
    s3 = boto3.client('s3')
    s3_key = "staging/" + md5(bytes(uuid.uuid4().hex, "ascii")).hexdigest() + ".zip"
    s3.upload_file("archive.zip", "dl.modules.tf", s3_key, ExtraArgs={'ACL': 'public-read'})

    # return link to user
    link = "https://dl.modules.tf/" + s3_key

    print("LINK=" + link)

    if True:
        myfile = open("archive.zip", "rb")
        body = base64.b64encode(myfile.read()).decode("ascii")

        return {
            "body": body,
            "headers": {
                "Content-Type": "application/zip",
                "Content-Disposition": "attachment; filename=\"infra.zip\""
            },
            "statusCode": 200,
            "isBase64Encoded": True,
        }
    else:
        return {
            "body": json.dumps(link),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT",
                "Access-Control-Allow-Origin": "*",
            },
            "statusCode": 200
        }


if __name__ == "__main__":
    test_event = {
        "queryStringParameters":
            {
                "cloudcraft": "https://cloudcraft.co/api/blueprint/cd5294fb-0aab-4475-bbcc-196f12738eac?key=5c3EuqRadKOJm3Xkkx-yeQ",
                "localfile": "input/blueprint.json"
            }
    }

    generate_from_cloudcraft(test_event, None)
    # generate_from_cloudcraft(None, None)
