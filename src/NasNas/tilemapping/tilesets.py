from sfml import sf
from xml.etree import ElementTree
import os
from ..reslib.resource_path import split_path

from typing import Dict, Union, List, Optional


# base class for tilesets, called when loading an external tileset
class Tileset:
    def __init__(self, xml: ElementTree.Element, path: str):
        self.xml_root: ElementTree.Element = xml
        self.path = path

        image = self.xml_root.find('image')

        self.name: str = self.xml_root.get('name')
        self.columns: int = int(self.xml_root.get('columns'))
        self.rows: int = int(image.get('height')) // int(self.xml_root.get('tileheight'))
        self.tile_width: int = int(self.xml_root.get('tilewidth'))
        self.tile_height: int = int(self.xml_root.get('tileheight'))
        self.tile_count: int = int(self.xml_root.get('tilecount'))
        self.texture_source = image.get('source')
        self.texture: Optional[sf.Texture] = None

        self.properties: Dict[int, Dict[str, Union[bool, int, float, str, sf.Color]]] = {}
        self.animations: Dict[int, List[Dict[str, int]]] = {}

    def load(self):
        texture_path = split_path(os.path.dirname(self.path)) + split_path(os.path.splitext(self.texture_source)[0])

        from ..reslib import Res
        res = Res
        if texture_path[0] == "assets":
            texture_path.pop(0)
        for folder in texture_path:
            res = getattr(res, folder)

        self.texture = res

        for tile in self.xml_root.findall('tile'):
            tile_id = int(tile.get('id'))
            for child in tile:
                if child.tag == "properties":
                    if tile_id not in self.properties:
                        self.properties[tile_id] = {}

                    for prop in child:
                        name = prop.get('name')
                        prop_type = prop.get('type')
                        val = prop.get('value')
                        if prop_type == "bool":
                            val = True if val == "true" else False
                        elif prop_type == "int":
                            val = int(val)
                        elif prop_type == "float":
                            val = float(val)
                        elif prop_type == "color":
                            val = sf.Color(int(val[1:3], 16), int(val[3:5], 16), int(val[5:7], 16), int(val[7:9], 16))
                        self.properties[tile_id].update({name: val})

                elif child.tag == "animation":
                    if tile_id not in self.animations:
                        self.animations[tile_id] = []

                    for frame in child:
                        self.animations[tile_id].append(
                            {
                                'id': int(frame.get('tileid')),
                                'duration': int(frame.get('duration'))
                            }
                        )


# when loading a TiledMap, a MapTileset are created for each tileset used in the map
class MapTileset:
    def __init__(self, tileset: Tileset, firstgid: int):
        self._data: Tileset = tileset
        self._first_gid: int = firstgid
        self._last_gid = self.first_gid + self._data.tile_count - 1

    @property
    def name(self) -> str:
        return self._data.name

    @property
    def columns(self) -> int:
        return self._data.columns

    @property
    def rows(self) -> int:
        return self._data.rows

    @property
    def tile_width(self) -> int:
        return self._data.tile_width

    @property
    def tile_height(self) -> int:
        return self._data.tile_height

    @property
    def tile_count(self) -> int:
        return self._data.tile_count

    @property
    def first_gid(self) -> int:
        return self._first_gid

    @property
    def last_gid(self) -> int:
        return self._last_gid

    @property
    def texture(self) -> sf.Texture:
        return self._data.texture

    @property
    def properties(self) -> Dict[int, Dict[str, Union[bool, int, float, str, sf.Color]]]:
        return self._data.properties

    @property
    def animations(self) -> Dict[int, List[Dict[str, int]]]:
        return self._data.animations
