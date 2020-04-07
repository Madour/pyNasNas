import os
from sfml import sf
from xml.etree import ElementTree

from ..data.game_obj import GameObject
from ..data.rect import Rect
from ..reslib.resource_path import find_resource
from ..reslib.tileset_manager import TilesetManager
from .tilesets import Tileset, MapTileset
from .layers import TileLayer, ObjectGroup

from typing import List, Dict


class TiledMap(GameObject):
    def __init__(self, path: str):
        self.name = os.path.basename(path)
        self.path = path
        self.root = ElementTree.parse(find_resource(os.path.join(os.path.dirname(self.path), self.name))).getroot()

        self._size: sf.Vector2 = sf.Vector2(int(self.root.get('width')), int(self.root.get('height')))
        self._tile_size: sf.Vector2 = sf.Vector2(int(self.root.get('tilewidth')), int(self.root.get('tileheight')))

        self.tilesets: List[MapTileset] = []
        self.layers: Dict[str, TileLayer] = {}
        self.objectgroups: Dict[str, ObjectGroup] = {}
        self._collisions = []

    def load(self):
        # loading tilesets
        for tileset_elmnt in self.root.findall('tileset'):
            name = tileset_elmnt.get('name')
            if not name:
                t = TilesetManager.get(os.path.splitext(os.path.basename(tileset_elmnt.get('source')))[0])
            else:
                t = Tileset(tileset_elmnt, self.path)
                t.load()
            self.tilesets.append(MapTileset(t, int(tileset_elmnt.get('firstgid'))))

        # loading layers
        for layer_elmnt in self.root.findall('layer'):
            layer = TileLayer(self, layer_elmnt)
            layer.parse()
            self.layers[layer.name] = layer

        # loading objectgroups
        for objectgroup_elmnt in self.root.findall('objectgroup'):
            objectgroup = ObjectGroup(self, objectgroup_elmnt)
            objectgroup.parse()
            self.objectgroups[objectgroup.name] = objectgroup

    def update(self):
        yrange = []
        xrange = []
        for cam in self.game.cameras:
            yboundsmin = max(0, int(cam.top) // 16 - 2)
            yboundsmax = min(self.size.x, int(cam.bottom) // 16 + 2)
            yrange += list(range(yboundsmin, yboundsmax))
            xboundsmin = max(0, int(cam.left) // 16 - 2)
            xboundsmax = min(self.size.y, int(cam.right) // 16 + 2)
            xrange += list(range(xboundsmin, xboundsmax))
        yrange = list(set(yrange))
        xrange = list(set(xrange))
        # iterating over the visible tiles only
        for j in yrange:
            for i in xrange:
                for layer in self.layers.values():
                    if layer.visible:
                        layer.update_tile(i, j)
        for layer in self.layers.values():
            if layer.visible:
                layer.render_texture.display()
                layer.sprite.texture = layer.render_texture.texture

    def set_collisions_objectgroup(self, name):
        if name in self.objectgroups:
            self._collisions = self.objectgroups[name].objects
        else:
            raise AttributeError(f"{name} is not an objectgroup of {self.name} TiledMap")

    @property
    def collisions(self):
        return self._collisions

    @property
    def size(self) -> sf.Vector2:
        return self._size

    @property
    def width(self) -> int:
        return self._size.x

    @property
    def height(self) -> int:
        return self._size.y

    @property
    def tile_size(self):
        return self._tile_size

    @property
    def tile_width(self):
        return self._tile_size.x

    @property
    def tile_height(self):
        return self._tile_size.y
