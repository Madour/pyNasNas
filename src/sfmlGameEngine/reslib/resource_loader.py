from sfml import sf
import os
from .resource_path import find_resource
from . import tile_mapping as tm


def load_resources(obj, path):
    for file in os.listdir(find_resource(path)):
        filename, ext = os.path.splitext(file)
        if os.path.isfile(os.path.join(path, file)):
            if ext in [".png", ".jpg", ".bmp"]:
                value = sf.Texture.from_file(find_resource(os.path.join(path, file)))
                setattr(obj, filename, value)
                res = obj
                while res.parent:
                    res = res.parent
                setattr(res._textures, filename, value)

            elif ext in [".ttf"]:
                value = sf.Font.from_file(find_resource(os.path.join(path, file)))
                value.get_texture(8).smooth = False
                value.get_texture(16).smooth = False
                value.get_texture(32).smooth = False
                setattr(obj, filename, value)
                res = obj
                while res.parent:
                    res = res.parent
                setattr(res._fonts, filename, value)

            elif ext in [".tmx"]:
                value = tm.TileMap(find_resource(os.path.join(path, file)))
                setattr(obj, filename, value)
                res = obj
                while res.parent:
                    res = res.parent
                setattr(res._maps, filename, value)

        elif os.path.isdir(os.path.join(path, file)):
            dir = Dir(filename, parent=obj)
            load_resources(dir, os.path.join(path, file))
            setattr(obj, filename, dir)

class Dir:
    def __init__(self, name, parent = None):
        self.__dict__["name"] = name
        self.__dict__["parent"] = parent
        self.__dict__["data"] = {}

    def __getattr__(self, item):
        if item in self.__dict__["data"]:
            return self.__dict__["data"][item]
        raise AttributeError(f"file or directory '{item}' not found in directory '{self.name}'")

    def __setattr__(self, key, value):
        if key not in vars(dict).keys():
            self.__dict__["data"][key] = value
        else:
            raise AttributeError(f"{key} is not a valid key")

    def __iter__(self):
        for key in self.__dict__["data"].keys():
            yield key

    def values(self):
        return self.__dict__["data"].values()

    def all_files(self):
        for file in self.values():
            if isinstance(file, Dir):
                for f in file.all_files():
                    yield f
            else:
                yield file

