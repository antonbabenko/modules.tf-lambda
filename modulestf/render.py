import glob
import json
import os
import re
import shutil
from pprint import pformat, pprint

from cookiecutter.exceptions import NonTemplatedInputDirException
from cookiecutter.main import cookiecutter
from modulestf.const import *
from modulestf.logger import setup_logging
from modulestf.modules import *

logger = setup_logging()


def mkdir_safely(dir):
    try:
        shutil.rmtree(dir)
    except FileNotFoundError:
        pass

    try:
        os.mkdir(dir)
    except OSError:
        pass


def prepare_render_dirs():
    output_dir = os.path.join(tmp_dir, OUTPUT_DIR)

    mkdir_safely(output_dir)
    os.chdir(output_dir)

    mkdir_safely(WORK_DIR)
    os.chdir(WORK_DIR)

    mkdir_safely(FINAL_DIR)


def render_single_layer(resource, regions, append_id=False):

    # logger.info("...")

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
        # "dependencies": ["..."] # @todo: get correct dir_name when there are several items (eg, multiple vpcs)
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
