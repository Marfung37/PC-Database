# Contains various directories in the repo

import os

def get_root_dir():
    script = os.path.realpath(__file__)
    return  os.path.normpath(os.path.join(os.path.dirname(script), "../.."))

ROOT = get_root_dir()
