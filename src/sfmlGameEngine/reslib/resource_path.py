import sys, os

ABSOLUTE_PATH = sys.path[0]
RES_DIR = "assets"


def find_resource(relative_path):
    try:  # for release : pyInstaller stores assets in a temporary folder _MEIPASS
        absolute_path = sys._MEIPASS
    except:  # for developement
        absolute_path = ""
    return os.path.join(absolute_path, relative_path)


