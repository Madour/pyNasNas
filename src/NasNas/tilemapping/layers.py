from typing import List, Dict, Union, Optional
from xml.etree import ElementTree

from sfml import sf

from ..data.rect import Rect
from ..data.shapes import EllipseShape, LineShape
from .tiles import Tile


class TileLayer(sf.Drawable):
    def __init__(self, tiledmap, xml: ElementTree.Element):
        super().__init__()
        self.xml = xml
        self.map = tiledmap

        self.id: int = int(self.xml.get('id'))
        self.name: str = self.xml.get('name')
        self.width: int = int(self.xml.get('width'))
        self.height: int = int(self.xml.get('height'))
        self.visible: bool = not bool(self.xml.get('visible'))

        self.tiles: List[List[Optional[Tile]]] = []
        self.properties: Dict[str, Union[int, float, str, bool, sf.Color]] = {}
        self.animated_tiles: Dict[tuple, Tile] = {}

        self.render_texture: sf.RenderTexture = sf.RenderTexture(self.width*self.map.tile_width,
                                                                 self.height*self.map.tile_height)
        self.sprite: sf.Sprite = sf.Sprite(self.render_texture.texture)

    def parse(self):
        # parsing properties of the layer
        if self.xml.find('properties'):
            for prop in self.xml.find('properties'):
                name = prop.get('name')
                prop_type = prop.get('type')
                value = prop.get('value')
                if prop_type == "bool":
                    value = True if value == "true" else False
                elif prop_type == "int":
                    value = int(value)
                elif prop_type == "float":
                    value = float(value)
                elif prop_type == "color":
                    value = sf.Color(int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16), int(value[7:9], 16))

                self.properties[name] = value

        self.render_texture.clear(sf.Color.TRANSPARENT)
        layer_data = [int(n) for n in self.xml.find('data').text.split(',')]
        # iterating over the tiles of the layer
        for j in range(self.height):
            self.tiles.append([])
            for i in range(self.width):
                gid = layer_data[i + j * self.width]
                if gid != 0:
                    tile = Tile(self, i, j, gid)
                    self.tiles[j].append(tile)
                    self.render_texture.draw(tile)
                else:
                    self.tiles[j].append(None)

        self.render_texture.display()
        self.sprite.texture = self.render_texture.texture

    @property
    def position(self):
        return self.sprite.position

    @property
    def y(self):
        return self.sprite.position.y

    def update_tile(self, i, j):
        tile = self.tiles[j][i]
        if tile is not None and tile.animated:
            tile.update()
            clear = sf.RectangleShape()
            clear.position = tile.position
            clear.size = tile.size
            clear.fill_color = sf.Color.TRANSPARENT
            self.render_texture.draw(clear, sf.RenderStates(sf.BLEND_NONE))
            self.render_texture.draw(tile)

    def draw(self, target, states):
        if self.visible:
            target.draw(self.sprite, states)
        else:
            print(f"Trying to draw invisible TileLayer {self.name}")


class ObjectGroup(sf.Drawable):
    def __init__(self, tiledmap, xml: ElementTree.Element):
        super().__init__()
        self.xml = xml
        self.map = tiledmap

        self.id = int(self.xml.get('id'))
        self.name = self.xml.get('name')

        color = self.xml.get('color')
        if color:
            if len(color) == 9:
                self.color = sf.Color(int(color[3:5], 16), int(color[5:7], 16), int(color[7:9], 16), int(color[1:3], 16))
            else:
                self.color = sf.Color(int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), 255)
        else:
            self.color = sf.Color(100, 100, 100, 160)

        self.rectangles = []
        self.points = []
        self.ellipses = []
        self.polygons = []
        self.lines = []

        self._render_texture = sf.RenderTexture(tiledmap.width*tiledmap.tile_width, tiledmap.height*tiledmap.tile_height)
        self.sprite = sf.Sprite(self._render_texture.texture)

    def parse(self):
        self._render_texture.clear(sf.Color.TRANSPARENT)
        pts_vertexarray = sf.VertexArray(sf.PrimitiveType.POINTS)
        rect_vertexarray = sf.VertexArray(sf.PrimitiveType.QUADS)
        for object_elmnt in self.xml.findall('object'):
            x = float(object_elmnt.get('x'))
            y = float(object_elmnt.get('y'))
            width = float(object_elmnt.get('width')) if object_elmnt.get('width') else 0
            height = float(object_elmnt.get('height')) if object_elmnt.get('height') else 0
            if not list(object_elmnt):
                self.rectangles.append(Rect((x, y), (width, height)))
            else:
                child = list(object_elmnt)[0]
                if child.tag == "ellipse":
                    ellipse = EllipseShape((width/2, height/2))
                    ellipse.position = (x, y)
                    ellipse.fill_color = self.color
                    self._render_texture.draw(ellipse)
                elif child.tag == "point":
                    self.points.append(sf.Vector2(x, y))
                elif child.tag == "polyline":
                    points = []
                    for strpt in child.get('points').split():
                        points.append(sf.Vector2(float(strpt.split(',')[0]), float(strpt.split(',')[1])))
                    line = LineShape(*points)
                    line.position = (x, y)
                    line.color = self.color
                    self._render_texture.draw(line)
                elif child.tag == "polygon":
                    points = []
                    for strpt in child.get('points').split():
                        points.append(sf.Vector2(float(strpt.split(',')[0]), float(strpt.split(',')[1])))
                    polygone = sf.ConvexShape(len(points))
                    for i, p in enumerate(points):
                        polygone.set_point(i, p)
                    polygone.position = (x, y)
                    polygone.fill_color = self.color
                    self.polygons.append(polygone)
                    self._render_texture.draw(polygone)

        rect_vertexarray.resize(4*len(self.rectangles))
        for index in range(0, len(self.rectangles)*4, 4):
            rect_vertexarray[index + 0].position = self.rectangles[index//4].topleft
            rect_vertexarray[index + 1].position = self.rectangles[index//4].topright
            rect_vertexarray[index + 2].position = self.rectangles[index//4].bottomright
            rect_vertexarray[index + 3].position = self.rectangles[index//4].bottomleft
            for i in range(4):
                rect_vertexarray[index + i].color = self.color

        pts_vertexarray.resize(len(self.points))
        for index in range(len(self.points)):
            pts_vertexarray[index].position = self.points[index]
            pts_vertexarray[index].color = self.color

        self._render_texture.draw(rect_vertexarray)
        self._render_texture.draw(pts_vertexarray)
        self._render_texture.display()
        self.sprite.texture = self._render_texture.texture

    @property
    def position(self):
        return sf.Vector2(0, 0)

    def draw(self, target, states):
        target.draw(self.sprite)
