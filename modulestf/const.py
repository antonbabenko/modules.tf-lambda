import os
import tempfile

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

COOKIECUTTER_TEMPLATES_DIR = os.path.join(BASE_PATH, "../templates")

COOKIECUTTER_TEMPLATES_PREFIX = "terragrunt"  # or "terraform"

OUTPUT_DIR = "output"
WORK_DIR = "work"
WORK_DIR_FOR_COOKIECUTTER = "{{ cookiecutter.dir_name }}"

FINAL_DIR = "final"

S3_BUCKET = "dl.modules.tf"
S3_BUCKET_REGION = "eu-west-1"

if os.environ.get("IS_LOCAL"):
    tmp_dir = os.getcwd()
else:
    tmp_dir = tempfile.gettempdir()  # was /tmp
