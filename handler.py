#!/usr/bin/env python3

from __future__ import print_function

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
import logging

from cookiecutter.main import cookiecutter

MODULES = {
    "elb": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-elb.git",
        "variables": json.load(open("modules-metadata/elb.json")),
    },
    "rds": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-rds.git",
        "variables": json.load(open("modules-metadata/rds.json")),
    },
    "autoscaling": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-autoscaling.git",
        "variables": json.load(open("modules-metadata/autoscaling.json")),
    },
    "ec2-instance": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-ec2-instance.git",
        "variables": json.load(open("modules-metadata/ec2-instance.json")),
    },
    "s3": {
        # "source": "terraform-aws-modules/s3/aws",
        "source": "terraform-aws-modules/security-group/aws",
        "variables": {},
    },
    "cloudfront": {
        # "source": "terraform-aws-modules/cloudfront/aws",
        "source": "terraform-aws-modules/security-group/aws",
        "variables": {},
    },
}

COOKIECUTTER_TEMPLATES_DIR = os.getcwd() + "/templates"

if os.environ.get("IS_LOCAL"):
    tmp_dir = os.getcwd()
else:
    tmp_dir = "/tmp"


# Logging snippet was from https://gist.github.com/niranjv/fb95e716151642e8ca553b0e38dd152e
def setup_logging():
    logger = logging.getLogger()
    for h in logger.handlers:
        logger.removeHandler(h)

    h = logging.StreamHandler(sys.stdout)

    # use whatever format you want here
    FORMAT = "[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(name)s\t%(message)s\n"
    h.setFormatter(logging.Formatter(FORMAT))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

    return logger


def prepare_data(data):
    global source
    global nodes
    global asg_groups
    global edges      # edges are uni-directional (from => to)
    global edges_rev  # edges_rev are reversed (to => from). Used by RDS nodes (master/slave).
    global texts
    global surfaces
    global regions

    nodes = dict()
    asg_groups = dict()
    edges = dict()      # edges are uni-directional (from => to)
    edges_rev = dict()  # edges_rev are reversed (to => from). Used by RDS nodes (master/slave).
    texts = dict()
    surfaces = dict()
    regions = dict()

    # We don't care about these keys in json: connectors, images, icons
    data_nodes = data["data"]["nodes"]
    data_edges = data["data"]["edges"]
    data_groups = data["data"]["groups"]
    data_text = data["data"]["text"]
    data_surfaces = data["data"]["surfaces"]

    for node in data_nodes:
        nodes[node["id"]] = node

    for group in data_groups:
        if group["type"] == "asg":
            asg_groups[group["id"]] = group["nodes"]

    for edge in data_edges:
        if edge["from"] not in edges:
            edges[edge["from"]] = set()
        edges[edge["from"]].add(edge["to"])

        if edge["to"] not in edges_rev:
            edges_rev[edge["to"]] = set()
        edges_rev[edge["to"]].add(edge["from"])

    for text in data_text:
        texts[text["id"]] = text

        mapPos = text.get("mapPos", {})
        if isinstance(mapPos, dict):
            relTo = mapPos.get("relTo", "")

            if relTo:
                if relTo in nodes.keys():
                    nodes[relTo].update({"text": text["text"]})

    for surface in data_surfaces:
        surfaces[surface["id"]] = surface

        if surface["type"] == "zone":
            region = surface.get("region")
            if region:
                if region not in regions.keys():
                    regions[region] = list()

                regions[region].append(surface)

    source = {
        "name": data["data"]["name"],
        "id": data["id"],
    }

    # pprint(regions)
    # pprint(regions.keys())
    # pprint(nodes)
    # pprint(texts)
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

#
# def convert_params_into_module_values(type, params):
#     values = dict()
#     for key, value in params.items():
#         if "rds" == type:
#             if key == "isMultiAZ":
#                 values["multi_az"] = value
#
#     return values


def render_single_layer(resource, append_id=False):

    try:
        region = list(regions.keys())[0]
    except Exception:
        region = "eu-west-1"

    path_parts = list()

    text = resource.get("text")

    if text is not None and len(text):
        path_parts.append(text)
        if append_id:
            path_parts.append(resource["ref_id"])
    else:
        path_parts.append(resource["type"])
        if append_id:
            path_parts.append(resource["ref_id"])

    dir_name = "single_layer/%s/%s" % (region, "_".join(path_parts))

    single_layer = {
        "dir_name": dir_name.lower(),
        "module_source": MODULES[resource["type"]]["source"],
        "module_variables": MODULES[resource["type"]]["variables"],
    }

    extra_context = resource.update(single_layer) or resource

    cookiecutter(os.path.join(COOKIECUTTER_TEMPLATES_DIR, "tf-single-layer"),
                 config_file=os.path.join(COOKIECUTTER_TEMPLATES_DIR, "config_aws_lambda.yaml"),
                 no_input=True,
                 extra_context=extra_context)


def render_common_layer():

    try:
        region = list(regions.keys())[0]
    except Exception:
        region = "eu-west-1"

    common_layer = {
        "dir_name": "common_layer",
        "region": region,
    }

    cookiecutter(os.path.join(COOKIECUTTER_TEMPLATES_DIR, "tf-common-layer"),
                 config_file=os.path.join(COOKIECUTTER_TEMPLATES_DIR, "config_aws_lambda.yaml"),
                 no_input=True,
                 extra_context=common_layer)


def render_root_dir():

    root_dir = {
        "dir_name": "root_dir",
        "source": source,
    }

    cookiecutter(os.path.join(COOKIECUTTER_TEMPLATES_DIR, "tf-root"),
                 config_file=os.path.join(COOKIECUTTER_TEMPLATES_DIR, "config_aws_lambda.yaml"),
                 no_input=True,
                 extra_context=root_dir)


def load_data(event):
    qs = event.get("queryStringParameters")

    if qs is None:
        raise ValueError("Some query string parameters should be defined", 400)

    blueprint_url = qs.get("cloudcraft")
    localfile = qs.get("localfile")

    if blueprint_url:
        r = requests.get(blueprint_url)
        data = r.json()

        logging.info("Blueprint url: %s, response code: %s" % (blueprint_url, r.status_code))

        if 403 == r.status_code:
            raise ValueError("Sharing has been disabled for this blueprint. You have to enable it by clicking 'Export' -> 'Get shareable link' on https://cloudcraft.co/app/", 403)
        elif r.status_code >= 500:
            raise ValueError("Something went wrong on cloudcraft side. Can't fetch specified blueprint. Check URL and try again later.", 404)
    elif localfile:
        file = open(localfile, 'r')
        data = json.load(file)
    else:
        raise ValueError("'cloudcraft' or 'localfile' query string parameter should be defined", 400)

    print("event = %s" % json.dumps(event))

    return data


def generate_modulestf_config(data):

    pprint(data)

    prepare_data(data)

    resources = list()
    parsed_asg_id = set()
    parsed_rds_id = set()
    warnings = set()

    for id, node in nodes.items():

        # if node["type"] not in ["elb"]:
        #     continue

        print("------------------")
        # print(id)
        pprint(node, indent=2)

        edge_nodes = get_edge_nodes_by_id(id)
        edge_rev_nodes = get_edge_rev_nodes_by_id(id)
        # pprint(edge_nodes)
        # pprint(edge_rev_nodes)

        if node["type"] not in ["rds", "ec2", "elb", "s3", "cloudfront"]:
            warnings.add("node type %s is not implemented yet" % node["type"])

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

            # pprint(rds_id)

            if rds_id not in parsed_rds_id:
                resources.append({
                    "type": "rds",
                    "ref_id": rds_id,
                    "text": node.get("text"),
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
                        "text": node.get("text"),
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
                    "text": node.get("text"),
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
                "text": node.get("text"),
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
                "text": node.get("text"),
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
                "text": node.get("text"),
                "params": {
                }
            })

    print("-START------------------------------------")
    pprint(resources)
    print("-END------------------------------------")

    if len(warnings):
        logging.warning("; ".join(warnings))

    return json.dumps(resources)


# Count unique combination of type and text to decide if to append unique resource id
def get_types_text(resources):
    types_text = dict()
    for r in resources:
        try:
            t = r.get("type") + r.get("text")
        except TypeError:
            t = r.get("type")

        if t not in types_text.keys():
            types_text[t] = 1
        else:
            types_text[t] = types_text[t] + 1

    return types_text


def render_from_modulestf_config(config):

    resources = json.loads(config)

    output_dir = os.path.join(tmp_dir, "output")
    try:
        os.mkdir(output_dir)
    except OSError:
        pass

    os.chdir(output_dir)

    # create output directory
    working_dir = "work"

    try:
        shutil.rmtree(working_dir)
    except FileNotFoundError:
        pass

    try:
        os.mkdir(working_dir)
    except OSError:
        pass

    os.chdir(working_dir)

    # pprint(resources)

    types_text = get_types_text(resources)

    # render single layers in a loop
    for resource in resources:

        try:
            t = resource.get("type") + resource.get("text")
        except TypeError:
            t = resource.get("type")

        render_single_layer(resource, append_id=(types_text[t] > 1))

    render_common_layer()
    render_root_dir()

    # combine_rendered_output
    final_dir = "../final"

    try:
        shutil.rmtree(final_dir)
    except FileNotFoundError:
        pass

    try:
        os.mkdir(final_dir)
    except OSError:
        pass

    for file in glob.iglob("single_layer/*"):
        shutil.move(file, final_dir)

    for file in glob.iglob("single_layer/.*"):
        shutil.move(file, final_dir)

    for file in glob.iglob("common_layer/*"):
        shutil.move(file, final_dir)

    for file in glob.iglob("common_layer/.*"):
        shutil.move(file, final_dir)

    for file in glob.iglob("root_dir/*"):
        shutil.move(file, final_dir)

    for file in glob.iglob("root_dir/.*"):
        shutil.move(file, final_dir)

    print("Working directory: %s" % os.getcwd())

    # Make zip archive
    shutil.make_archive("archive", "zip", final_dir)


def upload_result():

    s3_bucket = os.environ.get("S3_BUCKET", "dl.modules.tf")
    s3_dir = os.environ.get("S3_DIR", "local")

    s3 = boto3.client("s3", region_name="eu-west-1")
    s3_key = s3_dir + "/" + md5(bytes(uuid.uuid4().hex, "ascii")).hexdigest() + ".zip"
    s3.upload_file("archive.zip", s3_bucket, s3_key, ExtraArgs={'ACL': 'public-read'})

    link = "https://" + s3_bucket + "/" + s3_key

    print("LINK=" + link)

    return link


def handler(event, context):
    link = ""
    logger = setup_logging()

    try:
        data = load_data(event)
    except ValueError as error:
        logger.error(error)

        return {
            "body": error.args[0],
            "statusCode": error.args[1],
        }

    config = generate_modulestf_config(data)

    render_from_modulestf_config(config)

    link = upload_result()

    return {
        "body": "",
        "headers": {
            "Location": link
        },
        "statusCode": 302,
    }


if __name__ == "__main__":
    test_event = {}

    # test_event = {
    #     "queryStringParameters":
    #         {
    #             "cloudcraft": "https://cloudcraft.co/api/blueprint/cd5294fb-0aab-4475-bbcc-196f12738eac?key=5c3EuqRadKOJm3Xkkx-yeQ",
    #         }
    # }

    test_event = {
        "queryStringParameters":
            {
                "localfile": "input/blueprint_default.json",
            }
    }

    handler(test_event, None)
