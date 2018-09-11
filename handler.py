#!/usr/bin/env python3

from __future__ import print_function

import glob
import json
import re
import networkx as nx

import boto3
import os
import shutil
import uuid
from hashlib import md5
from pprint import pprint, pformat
import requests
import sys
import logging
from cookiecutter.exceptions import NonTemplatedInputDirException

from cookiecutter.main import cookiecutter

MODULES = {
    "alb": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-alb.git",
        "variables": json.load(open("modules-metadata/alb.json")),
    },
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
    "sns": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-sns.git",
        "variables": json.load(open("modules-metadata/sns.json")),
    },
    "sqs": {
        "source": "git::git@github.com:terraform-aws-modules/terraform-aws-sqs.git",
        "variables": json.load(open("modules-metadata/sqs.json")),
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

COOKIECUTTER_TEMPLATES_DIR = os.getcwd() + "/templates"
COOKIECUTTER_TEMPLATES_PREFIX = "terragrunt" #"terraform" # or "terragrunt"

OUTPUT_DIR = "output"
WORK_DIR = "work"
FINAL_DIR = "../final"

if os.environ.get("IS_LOCAL"):
    tmp_dir = os.getcwd()
else:
    tmp_dir = os.tmpnam() # was /tmp


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
    global surfaces
    global regions
    global G

    G = nx.Graph() # We can't trust directions of edges, so graph should be not-directional
    # MG = nx.Graph()  # converted graph to modules.tf schema

    # @todo: convert from graph (G) to modules.tf graph (MG), which can be dumped to json and passed to generator function

    surfaces = dict()
    regions = dict()
    connectors = list()

    # We don't care about these keys in json: images, icons
    data_nodes = list()
    data_edges = list()
    data_groups = list()
    data_connectors = list()
    data_text = list()
    data_surfaces = list()
    data_name = ""

    try:
        data_nodes = data["data"]["nodes"]
    except KeyError:
        pass

    try:
        data_edges = data["data"]["edges"]
    except KeyError:
        pass

    try:
        data_groups = data["data"]["groups"]
    except KeyError:
        pass

    try:
        data_connectors = data["data"]["connectors"]
    except KeyError:
        pass

    try:
        data_text = data["data"]["text"]
    except KeyError:
        pass

    try:
        data_surfaces = data["data"]["surfaces"]
    except KeyError:
        pass

    try:
        data_name = data["data"]["name"]
    except KeyError:
        pass

    ########
    # NODES
    ########
    for node in data_nodes:
        G.add_node(node["id"], data=node)

    ########
    # EDGES
    ########
    for edge in data_edges:
        G.add_edge(edge["from"], edge["to"])

    #####################
    # AUTOSCALING GROUPS
    #####################
    for group in data_groups:
        if group.get("type") == "asg":
            group_id = group.get("id")
            group_nodes = group.get("nodes")

            G.add_node(group_id, data={"group_nodes": group_nodes})

            for group_node in group_nodes:
                G.node[group_node]["data"]["asg_id"] = group_id

    #############
    # CONNECTORS
    #############
    for connector in data_connectors:
        G.add_node(connector["id"], type="connector")
        connectors.append(connector["id"])

    # Merge connectors by contracting edges
    edge = list()
    while True:
        # Find first edge which contains connector
        for edge in G.edges.data():
            edge = list(edge)

            if edge[0] in connectors or edge[1] in connectors:
                break
            else:
                edge = list()

        # No edges with connectors remaining - all done
        if len(edge) == 0:
            break

        G = nx.contracted_edge(G, (edge[0], edge[1]), self_loops=False)

    ########
    # TEXTS
    ########
    for text in data_text:
        mapPos = text.get("mapPos", {})
        if isinstance(mapPos, dict):
            relTo = mapPos.get("relTo")

            if relTo in G.nodes:
                G.nodes[relTo]["text"] = text["text"]

    ###########
    # SURFACES
    ###########
    for surface in data_surfaces:
        surfaces[surface.get("id")] = surface

        if surface.get("type") == "zone":
            region = surface.get("region")
            if region:
                if region not in regions.keys():
                    regions[region] = list()

                regions[region].append(surface)

    ########
    # SOURCE
    ########
    source = {
        "name": data_name,
        "id": data.get("id"),
    }

    # Debug - draw into file
    # import matplotlib.pyplot as plt
    # plt.rcParams["figure.figsize"] = (10, 10)
    # nx.draw(G, pos=nx.spring_layout(G), with_labels=True)
    # plt.savefig("graph.png")

    # pprint(G.edges["0820fb86-ee74-49ce-9fe5-03f610ca5e75"])
    print("NODES===")
    print(G.nodes.data())
    print("EDGES===")
    print(G.edges.data())

    # pprint(regions)
    # pprint(regions.keys())
    # pprint(nodes)
    # pprint(texts)
    # pprint(edges, indent=2)
    # pprint(edges_rev)


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

    dir_name = "_".join(path_parts)
    dir_name = re.sub(' ', '_', dir_name.strip())
    dir_name = re.sub('[^a-zA-Z0-9-_]', '', dir_name)
    dir_name = re.sub('_+', '_', dir_name)

    full_dir_name = "single_layer/%s/%s" % (region, dir_name)

    single_layer = {
        "dir_name": full_dir_name.lower(),
        "layer_name": dir_name.lower(),
        "region": region,
        "module_source": MODULES[resource["type"]]["source"],
        "module_variables": MODULES[resource["type"]]["variables"],
    }

    extra_context = resource.update(single_layer) or resource

    cookiecutter(os.path.join(COOKIECUTTER_TEMPLATES_DIR, COOKIECUTTER_TEMPLATES_PREFIX + "-single-layer"),
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

    try:
        cookiecutter(os.path.join(COOKIECUTTER_TEMPLATES_DIR, COOKIECUTTER_TEMPLATES_PREFIX + "-common-layer"),
                 config_file=os.path.join(COOKIECUTTER_TEMPLATES_DIR, "config_aws_lambda.yaml"),
                 no_input=True,
                 extra_context=common_layer)
    except NonTemplatedInputDirException:
        pass

def render_root_dir():

    root_dir = {
        "dir_name": "root_dir",
        "source": source,
    }

    cookiecutter(os.path.join(COOKIECUTTER_TEMPLATES_DIR, "root"),
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


def get_node(node_id):
    try:
        return G.nodes.get(node_id)
    except (AttributeError, KeyError):
        return None


def get_node_attr(node_id, attribute):
    try:
        return G.nodes.get(node_id).get(attribute)
    except (AttributeError, KeyError):
        return None


def get_node_data(node_id, attribute):
    try:
        return get_node_attr(node_id, "data").get(attribute)
    except (AttributeError, KeyError):
        return None


def generate_modulestf_config(data):

    logging.info(pformat(data, indent=2))

    prepare_data(data)

    resources = list()
    parsed_asg_id = set()
    parsed_rds_id = set()
    warnings = set()

    for id, node in G.nodes.items():

        node = node.get("data")

        # if node.get("type") not in ["ec2", "elb"]:
        #     print("Skipping something... {}".format(node.get("type")))
        #     continue

        logging.info("\n========================================\nID = {}".format(id))

        if node is None:
            logging.error("No node data for this node - {}".format(node))
            continue

        logging.info("Node: {}".format(node))

        edges = G.adj[id]
        logging.info("Edges: {}".format(edges))

        if node.get("type") not in ["rds", "ec2", "elb", "sns", "sqs"]:
            warnings.add("node type %s is not implemented yet" % node.get("type"))

        if node.get("type") == "rds":
            is_multi_az = False

            for edge_id in edges:
                if get_node_data(edge_id, "type") == "rds" and \
                        get_node_data(edge_id, "engine") == node.get("engine") and \
                        get_node_data(edge_id, "role") == ("master" if node.get("role") == "slave" else "slave"):
                    master_rds_id = (id if node.get("role") == "master" else edge_id)
                    is_multi_az = True

            rds_id = master_rds_id if is_multi_az else id

            if rds_id not in parsed_rds_id:
                tmp_resource = {
                    "type": "rds",
                    "ref_id": rds_id,
                    "text": node.get("text"),
                    "params": {
                        "isMultiAZ": is_multi_az
                    }
                }

                if node.get("engine") is not None:
                    tmp_resource["params"].update({"engine": node.get("engine")})

                if node.get("instanceType") is not None and node.get("instanceSize") is not None:
                    tmp_resource["params"].update(
                        {"instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", "")})

                resources.append(tmp_resource)

            parsed_rds_id.add(rds_id)

        if node.get("type") == "ec2":
            asg_id = node.get("asg_id")

            elb_id = None

            if bool(asg_id):

                if asg_id not in parsed_asg_id:
                    # Find ELB/ALB in edges from or to ASG
                    tmp_edges = G.adj[asg_id]

                    for edge_id in tmp_edges:
                        if get_node_data(edge_id, "type") == "elb":
                            elb_id = get_node_data(edge_id, "id")
                            break

                    tmp_resource = {
                        "type": "autoscaling",
                        "ref_id": asg_id,
                        "text": node.get("text"),
                        "params": {
                            "elb_id": elb_id if elb_id else None,
                            "target_group_arns": ["arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/123"]
                        }
                    }

                    if node.get("instanceType") is not None and node.get("instanceSize") is not None:
                        tmp_resource["params"].update(
                            {"instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", "")})

                    resources.append(tmp_resource)

                parsed_asg_id.add(asg_id)
            else:
                tmp_resource = {
                    "type": "ec2-instance",
                    "ref_id": id,
                    "text": node.get("text"),
                    "params": {}
                }

                if node.get("instanceType") is not None and node.get("instanceSize") is not None:
                    tmp_resource["params"].update(
                        {"instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", "")})

                resources.append(tmp_resource)

        if node.get("type") == "elb":
            is_asg = False

            for edge_id in edges:
                if get_node_data(edge_id, "group_nodes") is not None:
                    is_asg = True
                    break

            if node.get("elbType") == "application":
                resources.append({
                    "type": "alb",
                    "ref_id": id,
                    "text": node.get("text"),
                    "params": {
                        "asg_id": edge_id if is_asg else None,
                    }
                })
            else:
                resources.append({
                    "type": "elb",
                    "ref_id": id,
                    "text": node.get("text"),
                    "params": {
                        "asg_id": edge_id if is_asg else None,
                    }
                })

        if node.get("type") == "s3":
            resources.append({
                "type": "s3",
                "ref_id": id,
                "text": node.get("text"),
                "params": {
                }
            })

        if node.get("type") == "cloudfront":
            resources.append({
                "type": "cloudfront",
                "ref_id": id,
                "text": node.get("text"),
                "params": {
                }
            })

        if node.get("type") == "sns":
            resources.append({
                "type": "sns",
                "ref_id": id,
                "text": node.get("text"),
                "params": {
                }
            })

        if node.get("type") == "sqs":
            resources.append({
                "type": "sqs",
                "ref_id": id,
                "text": node.get("text"),
                "params": {
                    "fifoQueue": node.get("queueType") == "fifo",
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


def prepare_render_dirs():
    output_dir = os.path.join(tmp_dir, OUTPUT_DIR)
    try:
        os.mkdir(output_dir)
    except OSError:
        pass

    os.chdir(output_dir)

    try:
        shutil.rmtree(WORK_DIR)
    except FileNotFoundError:
        pass

    try:
        os.mkdir(WORK_DIR)
    except OSError:
        pass

    os.chdir(WORK_DIR)

    # combine_rendered_output
    try:
        shutil.rmtree(FINAL_DIR)
    except FileNotFoundError:
        pass

    try:
        os.mkdir(FINAL_DIR)
    except OSError:
        pass


def render_from_modulestf_config(config):

    resources = json.loads(config)

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

    files = glob.glob("single_layer/*") + \
            glob.glob("single_layer/.*") + \
            glob.glob("common_layer/*") + \
            glob.glob("common_layer/.*") + \
            glob.glob("root_dir/*") + \
            glob.glob("root_dir/.*")

    for file in files:
        shutil.move(file, FINAL_DIR)

    # terraform: merge all single_layers in single region into one directory
    # files = glob.glob(FINAL_DIR + "/us-east-1/*/*")
    #
    # for file in files:
    #     pprint(file)
    #     shutil.move(file, FINAL_DIR + "/us-east-1")

    print("Working directory: %s" % os.getcwd())

    # Make zip archive
    shutil.make_archive("archive", "zip", FINAL_DIR)


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

    prepare_render_dirs()

    render_from_modulestf_config(config)

    # Do not upload to S3 when working locally
    if not os.environ.get("IS_LOCAL"):
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
