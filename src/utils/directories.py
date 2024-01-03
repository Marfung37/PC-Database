# Contains various directories in the repo

import os

def get_root_dir():
    script = os.path.realpath(__file__)
    return  os.path.normpath(os.path.join(os.path.dirname(script), "../.."))

ROOT = get_root_dir()

SFINDERPATH = os.path.join(ROOT, "src", "solution-finder-1.42", "sfinder.jar")
KICKPATH = os.path.join(ROOT, "src", "solution-finder-1.42", "kicks", "jstris180.properties")
