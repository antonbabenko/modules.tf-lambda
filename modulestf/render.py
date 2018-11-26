import glob
import json
import pathlib
import re
import shutil
from os import chdir, getcwd, makedirs, mkdir, path
from pprint import pformat, pprint

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
        mkdir(dir)
    except OSError:
        pass


def prepare_render_dirs():
    # return
    output_dir = path.join(tmp_dir, OUTPUT_DIR)

    mkdir_safely(output_dir)
    chdir(output_dir)

    mkdir_safely(WORK_DIR)
    chdir(WORK_DIR)

    # mkdir_safely(FINAL_DIR)

    mkdir(WORK_DIR_FOR_COOKIECUTTER)


def find_templates_files(dir):
    pprint("DIR = %s" % dir)

    files = glob.glob(dir + "/*") + \
        glob.glob(dir + "/.*")

    return files


def prepare_single_layer(resource, region, templates_dir, templates_files):

    dir_name = resource.get("dir_name")

    full_dir_name = ("%s/%s" % (region, dir_name)).lower()

    single_layer = {
        "module_type": resource["type"]
    }

    extra_context = resource.update(single_layer) or resource

    data = '{%- set this = ' + str(extra_context) + ' -%}'

    dst_dir = path.join(getcwd(), WORK_DIR_FOR_COOKIECUTTER, full_dir_name)

    for file in templates_files:
        # pprint("original = %s" % file)
        part_of_path_to_keep = "".join(file[len(templates_dir):])

        # pprint("just relative file = %s" % part_file)
        # pprint("getcwd = %s" % getcwd())

        dst_file = dst_dir + part_of_path_to_keep
        # pprint("new file = %s" % dst_file)

        with open(file, "r") as original:
            original_data = original.read()
            original.close()

        makedirs(path.dirname(dst_file), exist_ok=True)

        with open(dst_file, "w") as modified:
            modified.write(data + "\n" + original_data)
            modified.close()

    return resource["type"]


# Copy all files and subdirectories into working directory
def copy_to_working_dir(templates_dir):

    dst_dir = path.realpath(WORK_DIR_FOR_COOKIECUTTER)

    files = find_templates_files(templates_dir)

    for file in files:
        pprint("FILE == %s" % file)
        pprint("dst_dir == %s" % dst_dir)
        if path.isdir(file):
            dst = path.join(dst_dir, path.basename(file))
            shutil.copytree(file, dst)
        else:
            shutil.copy(file, dst_dir)


def render_all(extra_context):

    output_dir = path.join(tmp_dir, OUTPUT_DIR, WORK_DIR)

    cookiecutter(output_dir,
                 config_file=path.join(COOKIECUTTER_TEMPLATES_DIR, "config_aws_lambda.yaml"),
                 no_input=True,
                 extra_context=extra_context)


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

    # Find all templates for single layer once
    templates_dir = path.realpath(path.join(COOKIECUTTER_TEMPLATES_DIR, COOKIECUTTER_TEMPLATES_PREFIX + "-single-layer/template"))
    templates_files = find_templates_files(templates_dir)

    # Set of used module to load data once
    used_modules = set()

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
                    dynamic_params.update({k: v[0] + "." + dirs[v[1]] + "." + ".".join(v[2:])})
                except KeyError:
                    pass

        # Set correct dir name
        resource.update({"dir_name": dirs.get(resource.get("ref_id"))})

        # Render the layer
        logger.info("Rendering single layer resource id: %s" % resource.get("ref_id"))
        used_module_type = prepare_single_layer(resource, region, templates_dir, templates_files)

        used_modules.add(used_module_type)

    extra_context = dict({"module_sources": {}, "module_variables": {}})
    for module_type in used_modules:
        extra_context["module_sources"].update({
            module_type: MODULES[module_type]["source"],
        })

        extra_context["module_variables"].update({
            module_type: MODULES[module_type]["variables"],
        })

    logger.info("Prepare common layer")
    templates_dir = path.realpath(path.join(COOKIECUTTER_TEMPLATES_DIR, COOKIECUTTER_TEMPLATES_PREFIX + "-common-layer/template"))
    copy_to_working_dir(templates_dir)

    logger.info("Prepare root dir")
    templates_dir = path.realpath(path.join(COOKIECUTTER_TEMPLATES_DIR, "root/template"))
    copy_to_working_dir(templates_dir)

    shutil.copy(templates_dir + "/../cookiecutter.json", "cookiecutter.json")

    extra_context["source_name"] = source["name"]
    extra_context["dirs"] = dirs
    extra_context["region"] = region

    logger.info("Rendering all")
    render_all(extra_context)

    logger.info("Complete!")
