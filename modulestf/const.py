import os, tempfile

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

COOKIECUTTER_TEMPLATES_DIR = os.path.join(BASE_PATH, "../templates")

COOKIECUTTER_TEMPLATES_PREFIX = "terragrunt" #"terraform" # or "terragrunt"

OUTPUT_DIR = "output"
WORK_DIR = "work"
FINAL_DIR = "../final"

if os.environ.get("IS_LOCAL"):
    tmp_dir = os.getcwd()
else:
    tmp_dir = tempfile.gettempdir() # was /tmp
