import os
import tempfile

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

COOKIECUTTER_TEMPLATES_DIR = os.path.join(BASE_PATH, "../templates")

OUTPUT_DIR = "output"
WORK_DIR = "work"
WORK_DIR_FOR_COOKIECUTTER = "{{ cookiecutter.dir_name }}"

FINAL_DIR = "final"

S3_BUCKET = "dl.modules.tf"
S3_BUCKET_REGION = "eu-west-1"

if os.environ.get("AWS_EXECUTION_ENV") is not None:
    tmp_dir = tempfile.gettempdir()  # was /tmp
else:
    tmp_dir = os.getcwd()
