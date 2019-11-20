#!/usr/bin/env python3

import json
import os
import shutil
from pprint import pformat, pprint

import requests
from modulestf.cloudcraft.graph import populate_graph
from modulestf.const import FINAL_DIR
from modulestf.convert import convert_graph_to_modulestf_config
from modulestf.logger import setup_logging
from modulestf.render import prepare_render_dirs, render_from_modulestf_config
from modulestf.upload import upload_file_to_s3

logger = setup_logging()


def load_data(event):
    body = event.get("body")
    logger.info("body = %s" % body)

    qs = event.get("queryStringParameters")
    logger.info("queryStringParameters = %s" % qs)

    if body is None and qs is None:
        raise ValueError("Some query string parameters should be defined or use HTTP POST method", 400)

    if qs is None:
        blueprint_url = localfile = None
    else:
        blueprint_url = qs.get("cloudcraft")
        localfile = qs.get("localfile")

    if body:
        data = json.loads(body)
    elif blueprint_url:
        r = requests.get(blueprint_url)
        data = r.json()

        logger.info("Blueprint url: %s, response code: %s" % (blueprint_url, r.status_code))

        if 403 == r.status_code:
            raise ValueError("Sharing has been disabled for this blueprint." +
                             " You have to enable it by clicking 'Export' -> 'Get shareable link'" +
                             " on https://cloudcraft.co/app/", 403)

        elif r.status_code >= 500:
            raise ValueError("Something went wrong on cloudcraft side. Can't fetch specified blueprint." +
                             " Check URL and try again later.", 404)

    elif localfile:
        file = open(localfile, 'r')
        data = json.load(file)
    else:
        raise ValueError("'cloudcraft' or 'localfile' query string parameter should be defined", 400)

    print("event = %s" % json.dumps(event))

    return data


def handler(event, context):
    link = ""

    # ALB response are different:
    # https://docs.aws.amazon.com/elasticloadbalancing/latest/application/lambda-functions.html#respond-to-load-balancer
    request_from_lb = bool(event.get("requestContext", {}).get("elb"))

    if request_from_lb and event.get("path") == "/healthz":
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "statusDescription": "200 OK",
            "headers": {
                "Content-Type": "text/html"
            },
            "body": "Health OK"
        }

    try:
        data = load_data(event)
    except ValueError as error:
        logger.error(error)

        if request_from_lb:
            return {
                "isBase64Encoded": False,
                "statusCode": error.args[1],
                "statusDescription": str(error.args[1]) + " Server Error",
                "headers": {
                    "Content-Type": "text/html",
                },
                "body": error.args[0],
            }
        else:
            return {
                "body": error.args[0],
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                },
                "statusCode": error.args[1],
            }

    # logger.info(pformat(data, indent=2))

    graph = populate_graph(data)

    config = convert_graph_to_modulestf_config(graph)

    prepare_render_dirs()

    render_from_modulestf_config(config, source=graph.source, regions=graph.regions)

    # Do not upload to S3 when working locally
    if not os.environ.get("IS_LOCAL"):
        shutil.make_archive("archive", "zip", FINAL_DIR)

        link = upload_file_to_s3(filename="archive.zip")

    if request_from_lb:
        return {
            "isBase64Encoded": False,
            "headers": {
                "Location": link,
            },
            "statusCode": 302,
            "statusDescription": "302 Found",
        }
    else:
        return {
            "body": "",
            "headers": {
                "Location": link,
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            "statusCode": 302,
        }
