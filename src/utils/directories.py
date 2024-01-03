# Contains various directories in the repo

import os

def get_root_dir():
    script = os.path.realpath(__file__)
    return  os.path.normpath(os.path.join(os.path.dirname(script), "../.."))

ROOT = get_root_dir()

SFINDERPATH = os.path.join(ROOT, "src", "solution-finder-1.42", "sfinder.jar")
KICKPATH = os.path.join(ROOT, "src", "solution-finder-1.42", "kicks", "jstris180.properties")

# dict of pc number to filename/paths
FILENAMES = {
    1: os.path.join(ROOT, "tsv", "1stPC.tsv"),
    2: os.path.join(ROOT, "tsv", "2ndPC.tsv"),
    3: os.path.join(ROOT, "tsv", "3rdPC.tsv"),
    4: os.path.join(ROOT, "tsv", "4thPC.tsv"),
    5: os.path.join(ROOT, "tsv", "5thPC.tsv"),
    6: os.path.join(ROOT, "tsv", "6thPC.tsv"),
    7: os.path.join(ROOT, "tsv", "7thPC.tsv"),
    8: os.path.join(ROOT, "tsv", "8thPC.tsv"),
}
