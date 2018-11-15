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


def render_single_layer(resource, region):

    dir_name = resource.get("dir_name")

    full_dir_name = ("single_layer/%s/%s" % (region, dir_name)).lower()

    single_layer = {
        "dir_name": full_dir_name,
        "region": region,
        "module_source": MODULES[resource["type"]]["source"],
        "module_variables": MODULES[resource["type"]]["variables"],
    }

    extra_context = resource.update(single_layer) or resource

    cookiecutter(os.path.join(COOKIECUTTER_TEMPLATES_DIR, COOKIECUTTER_TEMPLATES_PREFIX + "-single-layer"),
                 config_file=os.path.join(COOKIECUTTER_TEMPLATES_DIR, "config_aws_lambda.yaml"),
                 no_input=True,
                 extra_context=extra_context)


def render_common_layer(region):

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


def make_dir_name(type, text, appendix=""):

    path_parts = []

    if text is not None and len(text):
        path_parts.append(text)
        if appendix:
            path_parts.append(appendix)
    else:
        path_parts.append(type)
        if appendix:
            path_parts.append(appendix)

    dir_name = "_".join(path_parts)
    dir_name = re.sub(' ', '_', dir_name.strip())
    dir_name = re.sub('[^a-zA-Z0-9-_]', '', dir_name)
    dir_name = re.sub('_+', '_', dir_name)

    return dir_name


def render_from_modulestf_config(config, source, regions):

    resources = json.loads(config)

    # pprint(resources)

    types_text = get_types_text(resources)

    try:
        region = regions[0]
    except Exception:
        region = "eu-west-1"

    dirs = {}

    also_append = []

    # 1. Get list of all resources and define correct dir names for all resources
    # 3. Update dynamic params and dependencies for each resource
    for resource in resources:

        try:
            t = resource.get("type") + resource.get("text")
        except TypeError:
            t = resource.get("type")

        if types_text[t] > 1 or (types_text[t] == 1 and t in also_append):
            appendix = str(types_text[t])
            new_appendix = types_text[t] - 1
            also_append.append(t)
        else:
            appendix = ""
            new_appendix = 0

        ref_id = resource.get("ref_id")

        if ref_id:
            dirs.update({ref_id: make_dir_name(type=resource.get("type"), text=resource.get("text"), appendix=appendix)})

        types_text[t] = new_appendix

    # render single layers in a loop
    for resource in resources:

        # Update dependencies with correct dir name
        deps = []
        if resource.get("dependencies"):
            for d in resource.get("dependencies"):
                this_dir = dirs.get(d)
                if this_dir:
                    deps.append(this_dir)

        # cookiecutter does not support list values, so we join it to string here and split in template
        resource.update({"dependencies": ",".join(deps)})

        # Update dynamic parameters with correct dir name
        dynamic_params = resource.get("dynamic_params")
        if dynamic_params:
            for k in dynamic_params:

                try:
                    v = dynamic_params[k].split(".")

                    # replace second element with real directory name
                    dynamic_params.update({k: v[0] + "." + dirs[v[1]] + "." + "".join(v[2:])})
                except KeyError:
                    pass

        # Set correct dir name
        resource.update({"dir_name": dirs.get(resource.get("ref_id"))})

        # Render the layer
        logger.info("Rendering single layer resource id: %s" % resource.get("ref_id"))
        render_single_layer(resource, region)

    logger.info("Rendering common layer")
    render_common_layer(region)

    logger.info("Rendering root dir")
    render_root_dir(source)

    files = glob.glob("single_layer/*") + \
        glob.glob("single_layer/.*") + \
        glob.glob("common_layer/*") + \
        glob.glob("common_layer/.*") + \
        glob.glob("root_dir/*") + \
        glob.glob("root_dir/.*")

    logger.info("Moving files into final dir: %s" % FINAL_DIR)
    for file in files:
        shutil.move(file, FINAL_DIR)

    logger.info("Complete!")
