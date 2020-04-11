from sfml import sf

from .utils import to_Vector2
from .data.rect import Rect

from typing import Union, Tuple, Optional


class BitmapGlyph():
    def __init__(self, texture_rect, character, spacing):
        self.texture_rectangle = texture_rect
        self.character = character
        self.spacing = spacing


class BitmapFont():
    def __init__(self, texture: sf.Texture, char_size: Union[Tuple[int, int], sf.Vector2], chars_map=None, spacings_map=None):
        self.texture = texture

        self.char_size = to_Vector2(char_size)

        self.chars_map = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        if chars_map:
            self.chars_map = chars_map

        self.spacings_map = {}
        if spacings_map:
            self.spacings_map = spacings_map

        self.glyphs = {}
        i = 0
        for y in range(0, self.texture.height, self.char_size.y):
            for x in range(0, self.texture.width, self.char_size.x):
                if i < len(self.chars_map):
                    character = self.chars_map[i]
                    spacing = self.char_size.x
                    if character in self.spacings_map:
                        spacing = self.spacings_map[character]
                    self.glyphs[character] = BitmapGlyph(sf.Rect((x, y), self.char_size), character, spacing)
                i += 1

    def get_glyph(self, character: str) -> BitmapGlyph:
        return self.glyphs[character]

    def get_glyph_sprite(self, character: str) -> sf.Sprite:
        spr = sf.Sprite(self.texture)
        spr.texture_rectangle = self.glyphs[character].texture_rectangle
        return spr


class BitmapText(sf.Drawable):
    def __init__(self, text: str, font: BitmapFont = None):
        super().__init__()
        self._font: Optional[BitmapFont] = None
        self._text = text
        self._render_texture = sf.RenderTexture(1, 1)
        self._sprite = sf.Sprite(self._render_texture.texture)
        self._glyphs_sprites = []
        if font is not None:
            self.font = font
        self.position = (0, 0)

    @property
    def text(self):
        return self._text

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        if isinstance(value, BitmapFont):
            self._font = value
            x = 0
            self._glyphs_sprites = []
            for character in self.text:
                glyph = self._font.get_glyph(character)
                glyph_spr = self._font.get_glyph_sprite(character)
                glyph_spr.position = (x, 0)
                self._glyphs_sprites.append(glyph_spr)
                x += glyph.spacing
            self.update()
        else:
            raise TypeError("BitmapText font argument should be a BitmapFont instance")

    @property
    def position(self) -> sf.Vector2:
        return self._sprite.position

    @position.setter
    def position(self, value):
        self._sprite.position = to_Vector2(value)

    @property
    def origin(self):
        return self._sprite.origin

    @property
    def width(self):
        res = 0
        for c in self.text:
            res += self._font.get_glyph(c).spacing
        return res

    @property
    def height(self):
        return self._font.char_size.y

    @property
    def global_bounds(self):
        return self._sprite.global_bounds

    def update(self):
        self._render_texture = sf.RenderTexture(self.width, self.height)
        self._render_texture.clear(sf.Color.TRANSPARENT)
        for spr in self._glyphs_sprites:
            self._render_texture.draw(spr)
        self._render_texture.display()
        self._sprite.texture = self._render_texture.texture

    def draw(self, target, states):
        if self.font:
            target.draw(self._sprite, states)

