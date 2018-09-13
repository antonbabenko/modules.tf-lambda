#!/usr/bin/env python3

import glob
import json
import re
import tempfile

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

from modulestf.terraform import *
from modulestf.converter import *
from modulestf.modules import MODULES
from modulestf.cloudcraft.graph import *

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

pprint(MODULES)

COOKIECUTTER_TEMPLATES_DIR = os.path.join(BASE_PATH, "templates")
COOKIECUTTER_TEMPLATES_PREFIX = "terragrunt" #"terraform" # or "terragrunt"

OUTPUT_DIR = "output"
WORK_DIR = "work"
FINAL_DIR = "../final"

if os.environ.get("IS_LOCAL"):
    tmp_dir = os.getcwd()
else:
    tmp_dir = tempfile.gettempdir() # was /tmp


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


logger = setup_logging()


def render_single_layer(resource, regions, append_id=False):

    try:
        region = list(regions.keys())[0]
    except Exception:
        region = "eu-west-1"

    path_parts = []

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


def render_common_layer(regions):

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


def render_root_dir(source):

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


# Count unique combination of type and text to decide if to append unique resource id
def get_types_text(resources):
    types_text = {}
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


def render_from_modulestf_config(config, source, regions):

    resources = json.loads(config)

    # pprint(resources)

    types_text = get_types_text(resources)

    # render single layers in a loop
    for resource in resources:

        try:
            t = resource.get("type") + resource.get("text")
        except TypeError:
            t = resource.get("type")

        render_single_layer(resource, regions, append_id=(types_text[t] > 1))

    render_common_layer(regions)
    render_root_dir(source)

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

    try:
        data = load_data(event)
    except ValueError as error:
        logger.error(error)

        return {
            "body": error.args[0],
            "statusCode": error.args[1],
        }

    logging.info(pformat(data, indent=2))

    graph = populate_graph(data)

    config = convert_graph_to_modulestf_config(graph)

    prepare_render_dirs()

    render_from_modulestf_config(config, source=graph.source, regions=graph.regions)

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
