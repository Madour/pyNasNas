from typing import List, Optional

from sfml import sf

from .tilesets import MapTileset


class TileTransformation:
    HORIZONTAL_FLIP = 0x80000000
    VERTICAL_FLIP = 0x40000000
    DIAGONAL_FLIP = 0x20000000
    ROT90 = HORIZONTAL_FLIP + DIAGONAL_FLIP
    ROT180 = HORIZONTAL_FLIP + VERTICAL_FLIP
    ROT270 = VERTICAL_FLIP + DIAGONAL_FLIP

    @staticmethod
    def get_transformations(tile_id: int):
        transformations = []
        if bool((tile_id & TileTransformation.HORIZONTAL_FLIP) >> 31):
            transformations.append(TileTransformation.HORIZONTAL_FLIP)
        if bool((tile_id & TileTransformation.VERTICAL_FLIP) >> 30):
            transformations.append(TileTransformation.VERTICAL_FLIP)
        if bool((tile_id & TileTransformation.DIAGONAL_FLIP) >> 29):
            transformations.append(TileTransformation.DIAGONAL_FLIP)
        return transformations


class Tile(sf.Drawable):
    def __init__(self, tilelayer, x: int, y: int, gid: int):
        super().__init__()
        self._map = tilelayer.map
        self._tileset: Optional[MapTileset] = None

        self._gid = gid
        self._id = gid

        self._transformations = TileTransformation.get_transformations(self._gid)
        for tr in self._transformations:
            self._gid -= tr
        for tileset in self._map.tilesets:
            if tileset.first_gid <= self._gid <= tileset.last_gid:
                self._id = self._gid - tileset.first_gid
                self._tileset = tileset
                break

        self._x = x*self._tileset.tile_width
        self._y = y*self._tileset.tile_height
        self._tx = (self._id % self._tileset.columns) * self._tileset.tile_width
        self._ty = (self._id // self._tileset.columns) * self._tileset.tile_height

        self._sprite: sf.VertexArray = sf.VertexArray(sf.PrimitiveType.QUADS)
        self._sprite.resize(4)

        self._sprite[0].position = self.position
        self._sprite[1].position = self.position + sf.Vector2(self._tileset.tile_width, 0)
        self._sprite[2].position = self.position + sf.Vector2(self._tileset.tile_width, self._tileset.tile_height)
        self._sprite[3].position = self.position + sf.Vector2(0, self._tileset.tile_height)

        tex_coords = self._calculate_tex_coo(self._tx, self._ty)
        self._sprite[0].tex_coords = tex_coords[0]
        self._sprite[1].tex_coords = tex_coords[1]
        self._sprite[2].tex_coords = tex_coords[2]
        self._sprite[3].tex_coords = tex_coords[3]

        self._frames = []
        self._anim_data = []
        self._anim_index = 0

        if self.id in self._tileset.animations:
            self._anim_data = self.tileset.animations[self.id]
            for frame in self._anim_data:
                vert = sf.VertexArray(sf.PrimitiveType.QUADS)
                vert.resize(4)
                tx = (frame['id'] % self._tileset.columns) * self._tileset.tile_width
                ty = (frame['id'] // self._tileset.columns) * self._tileset.tile_height
                vert[0].position = self.position
                vert[1].position = self.position + sf.Vector2(self._tileset.tile_width, 0)
                vert[2].position = self.position + sf.Vector2(self._tileset.tile_width, self._tileset.tile_height)
                vert[3].position = self.position + sf.Vector2(0, self._tileset.tile_height)
                tex_coords = self._calculate_tex_coo(tx, ty)
                vert[0].tex_coords = tex_coords[0]
                vert[1].tex_coords = tex_coords[1]
                vert[2].tex_coords = tex_coords[2]
                vert[3].tex_coords = tex_coords[3]
                self._frames.append(vert)
        self._clock = sf.Clock()

    def _calculate_tex_coo(self, tx, ty) -> List[sf.Vector2]:
        tex_coords = [
            sf.Vector2(tx, ty),
            sf.Vector2(tx + self._tileset.tile_width, ty),
            sf.Vector2(tx + self._tileset.tile_width, ty + self._tileset.tile_height),
            sf.Vector2(tx, ty + self._tileset.tile_height)
        ]
        # applying tile transformation to the texture coordinates
        modifier = [sf.Vector2(0, 0), sf.Vector2(0, 0), sf.Vector2(0, 0), sf.Vector2(0, 0)]
        index0, index1, index2, index3 = range(4)
        if TileTransformation.DIAGONAL_FLIP in self._transformations:
            index2 = 0
            index0 = 2
            tex_coords[0], tex_coords[2] = tex_coords[2], tex_coords[0]
        if TileTransformation.HORIZONTAL_FLIP in self._transformations:
            modifier[index0] += sf.Vector2(self._tileset.tile_width, 0)
            modifier[index1] += sf.Vector2(-self._tileset.tile_width, 0)
            modifier[index2] += sf.Vector2(-self._tileset.tile_width, 0)
            modifier[index3] += sf.Vector2(self._tileset.tile_width, 0)
        if TileTransformation.VERTICAL_FLIP in self._transformations:
            modifier[index0] += sf.Vector2(0, self._tileset.tile_height)
            modifier[index1] += sf.Vector2(0, self._tileset.tile_height)
            modifier[index2] += sf.Vector2(0, -self._tileset.tile_height)
            modifier[index3] += sf.Vector2(0, -self._tileset.tile_height)
        return [tex_coords[i] + modifier[i] for i in range(4)]

    def update(self):
        if self._frames:
            if self._clock.elapsed_time.milliseconds > self._anim_data[self._anim_index]['duration']:
                self._anim_index += 1
                if self._anim_index > len(self._frames) - 1:
                    self._anim_index = 0
                self._sprite = self._frames[self._anim_index]
                self._clock.restart()

    def draw(self, target, state):
        state.texture = self._tileset.texture
        target.draw(self._sprite, state)

    @property
    def gid(self) -> int:
        return self._gid

    @property
    def id(self) -> int:
        return self._id

    @property
    def animated(self):
        return len(self._frames) > 0

    @property
    def transformations(self) -> List[int]:
        return self._transformations

    @property
    def sprite(self) -> sf.VertexArray:
        return self._sprite

    @property
    def size(self) -> sf.Vector2:
        return sf.Vector2(self.tileset.tile_width, self.tileset.tile_height)

    @property
    def position(self) -> sf.Vector2:
        return sf.Vector2(self._x, self._y)

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def tileset(self) -> MapTileset:
        return self._tileset

    @property
    def texture(self):
        return self._tileset.texture
