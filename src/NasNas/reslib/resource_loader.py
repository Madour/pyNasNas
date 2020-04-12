from typing import Dict, Union
import os

from sfml import sf

from ..tilemapping import tiledmap as tm
from .resource_path import find_resource
from .tileset_manager import TilesetManager


def load_resources(obj, path):
    for file in os.listdir(find_resource(path)):
        filename, ext = os.path.splitext(file)
        if os.path.isfile(os.path.join(path, file)):
            if ext in [".png", ".jpg", ".bmp"]:
                value = sf.Texture.from_file(find_resource(os.path.join(path, file)))
                setattr(obj, filename, value)
                res = obj
                while res._parent:
                    res = res._parent
                setattr(res._textures, filename, value)

            elif ext in [".ttf"]:
                value = sf.Font.from_file(find_resource(os.path.join(path, file)))
                value.get_texture(8).smooth = False
                value.get_texture(16).smooth = False
                value.get_texture(32).smooth = False
                setattr(obj, filename, value)
                res = obj
                while res._parent:
                    res = res._parent
                setattr(res._fonts, filename, value)

            elif ext in [".tmx"]:
                value = tm.TiledMap(find_resource(os.path.join(path, file)))
                setattr(obj, filename, value)
                res = obj
                while res._parent:
                    res = res._parent
                setattr(res._maps, filename, value)

            elif ext in [".tsx"]:
                TilesetManager.load_tsx(find_resource(os.path.join(path, file)))

        elif os.path.isdir(os.path.join(path, file)):
            directory = Dir(filename, parent=obj)
            load_resources(directory, os.path.join(path, file))
            setattr(obj, filename, directory)


class Dir:
    def __init__(self, name, parent=None):
        self._name = name
        self._parent = parent
        self._data: Dict[str, Union[Dir, sf.Texture, tm.TiledMap, sf.Font]] = {}

    def __getattr__(self, item) -> Union[sf.Font, sf.Texture, tm.TiledMap]:
        if item[0] == '_':
            return self.__dict__[item]
        if item == '..':
            return self._parent
        if item in self._data:
            return self._data[item]
        raise AttributeError(f"File or directory '{item}' not found in directory '{self._name}'")

    def __setattr__(self, key, value):
        if key not in vars(dict).keys():
            if key[0] == '_':
                self.__dict__[key] = value
            else:
                self._data[key] = value
        else:
            raise AttributeError(f"{key} is not a valid key")

    def __iter__(self):
        for key in self._data.keys():
            yield key

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def all_files(self):
        for file in self.values():
            if isinstance(file, Dir):
                for f in file.all_files():
                    yield f
            else:
                yield file

    def print_tree(self, indent=0):
        items = [i for i in self.items()]
        dirs = [d for d in items if isinstance(d[1], Dir)]
        dirs.sort(key=lambda x: x[0])
        files = [f for f in items if not isinstance(f[1], Dir)]
        files.sort(key=lambda x: x[0])

        for name, val in dirs:
            print(("│" + " " * 3) * (indent - 1), end='')
            print("├" + "─", end='')
            print(f" {name} : {type(val).__name__}")
            val.print_tree(indent=indent + 1)

        for name, val in files:
            print(("│" + " " * 3) * (indent - 1), end='')
            if (name, val) == files[-1]:
                print("└" + "─", end='')
            else:
                print("├" + "─", end='')
            print(f" {name} : {type(val).__name__}")
