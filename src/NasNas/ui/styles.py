from typing import Tuple, Union

from sfml import sf

from ..data.rect import Rect
from ..core.text import BitmapFont
from ..core.sprites import Anim
from ..core.utils import to_Vector2


class BoxBorder():
    def __init__(self, texture: sf.Texture, tex_pos: Union[Tuple[int, int], sf.Vector2], tile_size: Union[Tuple[int, int], sf.Vector2]):
        self._texture = texture
        self._pattern_pos = to_Vector2(tex_pos)
        self._tile_size = to_Vector2(tile_size)
        self._render_textures = {}

        top_left = sf.Sprite(self._texture)
        top_left.texture_rectangle = Rect(self._pattern_pos, self._tile_size)

        top_right = sf.Sprite(self._texture)
        top_right.texture_rectangle = Rect(self._pattern_pos + sf.Vector2(2*self._tile_size.x, 0), self._tile_size)

        bot_left = sf.Sprite(self._texture)
        bot_left.texture_rectangle = Rect(self._pattern_pos + sf.Vector2(0, 2*self._tile_size.y), self._tile_size)

        bot_right = sf.Sprite(self._texture)
        bot_right.texture_rectangle = Rect(self._pattern_pos + self._tile_size + self._tile_size, self._tile_size)

        self.corners = {
            'top_left': top_left,
            'top_right': top_right,
            'bot_left': bot_left,
            'bot_right': bot_right
        }

        self.vertex_pos = [
            sf.Vector2(0, 0),
            sf.Vector2(self._tile_size.x, 0),
            sf.Vector2(self._tile_size.x, self._tile_size.y),
            sf.Vector2(0, self._tile_size.y),
        ]

        self.tex_coords = {
            'top': [
                self._pattern_pos + sf.Vector2(self._tile_size.x, 0),
                self._pattern_pos + sf.Vector2(self._tile_size.x, 0) + sf.Vector2(self._tile_size.x, 0),
                self._pattern_pos + sf.Vector2(self._tile_size.x, 0) + self._tile_size,
                self._pattern_pos + sf.Vector2(self._tile_size.x, 0) + sf.Vector2(0, self._tile_size.y),
            ],
            'right': [
                self._pattern_pos + sf.Vector2(2 * self._tile_size.x, self._tile_size.y),
                self._pattern_pos + sf.Vector2(2 * self._tile_size.x, self._tile_size.y) + sf.Vector2(self._tile_size.x, 0),
                self._pattern_pos + sf.Vector2(2 * self._tile_size.x, self._tile_size.y) + self._tile_size,
                self._pattern_pos + sf.Vector2(2 * self._tile_size.x, self._tile_size.y) + sf.Vector2(0, self._tile_size.y),
            ],
            'bot': [
                self._pattern_pos + sf.Vector2(self._tile_size.x, 2 * self._tile_size.y),
                self._pattern_pos + sf.Vector2(self._tile_size.x, 2 * self._tile_size.y) + sf.Vector2(self._tile_size.x, 0),
                self._pattern_pos + sf.Vector2(self._tile_size.x, 2 * self._tile_size.y) + self._tile_size,
                self._pattern_pos + sf.Vector2(self._tile_size.x, 2 * self._tile_size.y) + sf.Vector2(0, self._tile_size.y),
            ],
            'left': [
                self._pattern_pos + sf.Vector2(0, self._tile_size.y),
                self._pattern_pos + sf.Vector2(0, self._tile_size.y) + sf.Vector2(self._tile_size.x, 0),
                self._pattern_pos + sf.Vector2(0, self._tile_size.y) + self._tile_size,
                self._pattern_pos + sf.Vector2(0, self._tile_size.y) + sf.Vector2(0, self._tile_size.y),
            ],
            'center': [
                self._pattern_pos + self._tile_size,
                self._pattern_pos + self._tile_size + sf.Vector2(self._tile_size.x, 0),
                self._pattern_pos + self._tile_size + self._tile_size,
                self._pattern_pos + self._tile_size + sf.Vector2(0, self._tile_size.y),
            ]
        }

    def generate_texture(self, width: int, height: int) -> sf.Texture:
        w = width//self._tile_size.x * self._tile_size.x
        h = height//self._tile_size.y * self._tile_size.y
        if (w, h) in self._render_textures: return self._render_textures[(w, h)].texture

        self.corners['top_left'].position = (0, 0)
        self.corners['top_right'].position = (w - self._tile_size.x, 0)
        self.corners['bot_left'].position = (0, h - self._tile_size.y)
        self.corners['bot_right'].position = (w - self._tile_size.x, h - self._tile_size.y)

        horizontal_size = ((w - 2 * self._tile_size.x) // self._tile_size.x) * 4
        vertical_size = ((h - 2 * self._tile_size.y) // self._tile_size.y) * 4
        fill_size = (((w - 2 * self._tile_size.x) // self._tile_size.x) * (h - 2 * self._tile_size.y) // self._tile_size.y) * 4
        sizes = {'top': horizontal_size, 'right': vertical_size, 'bot': horizontal_size, 'left': vertical_size, 'center': fill_size}
        offset = {
            'top': sf.Vector2(self._tile_size.x, 0),
            'right': sf.Vector2(w - self._tile_size.x, self._tile_size.y),
            'bot': sf.Vector2(self._tile_size.x, h - self._tile_size.y),
            'left': sf.Vector2(0, self._tile_size.y),
            'center': self._tile_size,
        }
        increment = {
            'top': sf.Vector2(self._tile_size.x/4, 0),
            'right': sf.Vector2(0, self._tile_size.y/4),
            'bot': sf.Vector2(self._tile_size.x/4, 0),
            'left': sf.Vector2(0, self._tile_size.y/4),
            'center': sf.Vector2(self._tile_size.x/4, self._tile_size.y/4)
        }

        vertices = []

        for side in self.tex_coords:
            vert = sf.VertexArray(sf.PrimitiveType.QUADS)
            vert.resize(sizes[side])
            for i in range(0, sizes[side], 4):
                for j in range(4):
                    vert[i + j].tex_coords = self.tex_coords[side][j]
                    if side == 'center':
                        center_offset = sf.Vector2(
                            (increment[side].x * i) % (w - 2 * self._tile_size.x),
                            (increment[side].y * i) // (w - 2 * self._tile_size.x) * self._tile_size.y
                        )
                        vert[i + j].position = self.vertex_pos[j] + offset[side] + center_offset
                    else:
                        vert[i + j].position = self.vertex_pos[j] + offset[side] + increment[side] * i
            vertices.append(vert)

        render_texture = sf.RenderTexture(w, h)
        render_texture.clear(sf.Color.TRANSPARENT)

        render_texture.draw(self.corners['top_left'])
        render_texture.draw(self.corners['top_right'])
        render_texture.draw(self.corners['bot_left'])
        render_texture.draw(self.corners['bot_right'])

        for vert in vertices:
            render_texture.draw(vert, sf.RenderStates(texture=self._texture))
        render_texture.display()

        self._render_textures[(w, h)] = render_texture
        return render_texture.texture


class ButtonStyle:
    __slots__ = ["width", "height", "size", "bounds", "margin", "font",
                 "color", "font_size", "background", "anim"]

    def __init__(self,
                 width: int = 0, height: int = 0,
                 margin: Tuple[int, int, int, int] = (0, 0, 0, 0),
                 font: Union[sf.Font, BitmapFont] = None,
                 color: sf.Color = sf.Color.WHITE,
                 font_size: int = 16,
                 background: Union[sf.Color, sf.Texture] = sf.Color.TRANSPARENT,
                 anim: Anim = None,
                 ):
        self.width = width
        self.height = height
        self.size = sf.Vector2(width, height)
        self.bounds = sf.Vector2(margin[3] + width + margin[1], margin[0] + height + margin[2])
        self.margin = margin
        self.font = font
        self.color = color
        self.font_size = font_size
        self.background = background
        self.anim = anim


class MenuStyle:
    __slots__ = ["width", "height", "size", "bounds", "padding", "background"]

    def __init__(self,
                 width: int = 0, height: int = 0,
                 padding: Tuple[int, int, int, int] = (0, 0, 0, 0),
                 background: Union[sf.Color, sf.Texture, BoxBorder] = sf.Color.TRANSPARENT
                 ):
        self.size = sf.Vector2(padding[3] + width + padding[1] , padding[0] + height  + padding[3])
        self.width = self.size.x
        self.height = self.size.y
        self.padding = padding
        self.background = background

