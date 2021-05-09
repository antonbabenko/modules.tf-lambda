#!/usr/bin/env python3

import json
import os
import pathlib
import shutil
from pprint import pformat, pprint
from typing import Any, Dict

import requests
from aws_lambda_powertools import Metrics, Tracer
from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext
from modulestf.cloudcraft.graph import populate_graph
from modulestf.const import FINAL_DIR
from modulestf.convert import convert_graph_to_modulestf_config
from modulestf.logger import setup_logging
from modulestf.render import prepare_render_dirs, render_from_modulestf_config
from modulestf.upload import upload_file_to_s3

# logger = setup_logging()

os.environ["POWERTOOLS_TRACE_DISABLED"] = "1"

logger = Logger(service="modulestf-d2c")
tracer = Tracer(service="modulestf-d2c")
metrics = Metrics(namespace="modulestf-d2c", service="modulestf-d2c")


def load_data(event):
    body = event.body
    logger.info(f"body = {body}")

    qs = event.query_string_parameters
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
                             " on https://app.cloudcraft.co", 403)

        elif r.status_code >= 500:
            raise ValueError("Something went wrong on cloudcraft side. Can't fetch specified blueprint." +
                             " Check URL and try again later.", 404)

    elif localfile:
        file = open(localfile, 'r')
        data = json.load(file)
    else:
        raise ValueError("'cloudcraft' or 'localfile' query string parameter should be defined", 400)

    return data


@metrics.log_metrics
@logger.inject_lambda_context
@tracer.capture_lambda_handler
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:  # noqa: WPS110

    event: APIGatewayProxyEventV2 = APIGatewayProxyEventV2(event)

    logger.info("Processing event: {}".format(json.dumps(event.body)))

    link = ""

    try:
        data = load_data(event)
    except ValueError as error:
        logger.error(error)

        return {
            "body": str(error),
            "isBase64Encoded": False,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            "statusCode": 400,
        }

    # logger.info(pformat(data, indent=2))

    graph = populate_graph(data)

    config = convert_graph_to_modulestf_config(graph)

    prepare_render_dirs()

    render_from_modulestf_config(config, source=graph.source, regions=graph.regions)

    # Do not upload to S3 when working locally
    if os.environ.get("UPLOAD_TO_S3", False):
        shutil.make_archive("archive", "zip", FINAL_DIR)

        link = upload_file_to_s3(filename="archive.zip")

    metrics.add_metric(name="Request", unit=MetricUnit.Count, value=1)

    return {
        "body": "",
        "headers": {
            "Location": link,
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True
        },
        "statusCode": 302,
    }


if __name__ == "__main__":
    api_gateway = pathlib.Path(__file__).parent.absolute() / "../test_fixtures/api_gateway_request.json"
    event = json.loads(api_gateway.read_text())

    # fixture = pathlib.Path(__file__).parent.absolute() / "../test_fixtures/input_cloudcraft.json"
    fixture = pathlib.Path(__file__).parent.absolute() / "../test_fixtures/input_localfile.json"
    # fixture = pathlib.Path(__file__).parent.absolute() / "../test_fixtures/input_data.json"

    fixture_json = json.loads(fixture.read_text())

    event.update(fixture_json)

    context = LambdaContext()
    context._function_name = "_function_name"
    context._function_version = "_function_version"
    context._invoked_function_arn = "_invoked_function_arn"
    context._memory_limit_in_mb = "_memory_limit_in_mb"
    context._aws_request_id = "_aws_request_id"
    context._log_group_name = "_log_group_name"
    context._log_stream_name = "_log_stream_name"

    handler(event, context)
