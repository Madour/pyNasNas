import sys
import os

ABSOLUTE_PATH = sys.path[0]
RES_DIR = "assets"


def find_resource(relative_path: str):
    try:  # for release : pyInstaller stores assets in a temporary folder _MEIPASS
        absolute_path = sys._MEIPASS
    except:  # for developement
        absolute_path = ""
    return os.path.join(absolute_path, relative_path)


def split_path(path: str) -> list:
    sep = os.sep if os.sep in path else '/'
    return path.split(sep)


def normalize_path(path: str) -> str:
    path = split_path(path)
    while '..' in path:
        index = path.index('..')
        if index != 0:
            path = [p for i, p in enumerate(path) if i != index and i != index - 1]
    return os.sep.join(path)
