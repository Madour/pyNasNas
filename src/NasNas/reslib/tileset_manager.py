from typing import Dict
from xml.etree import ElementTree

from .resource_path import find_resource
from ..tilemapping.tilesets import Tileset


class TilesetManagerMeta(type):
    _data: Dict[str, Tileset] = {}

    @classmethod
    def __iter__(mcs):
        for x in mcs._data.values():
            yield x

    @classmethod
    def __contains__(mcs, item):
        if isinstance(item, str):
            if item in mcs._data:
                return True
            return False
        else:
            raise TypeError("Error, `in` comparison with TilesetManager should be a string")


class TilesetManager(metaclass=TilesetManagerMeta):
    @classmethod
    def load_tsx(cls, path: str):
        xml = ElementTree.parse(find_resource(path)).getroot()
        t = Tileset(xml, path)
        cls._data[t.name] = t

    @classmethod
    def get(cls, tilesetname: str):
        if tilesetname in cls._data:
            return cls._data[tilesetname]
