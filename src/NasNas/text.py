from sfml import sf


class BitmapGlyph():
    def __init__(self, texture_rect, character, spacing):
        self.texture_rectangle = texture_rect
        self.character = character
        self.spacing = spacing


class BitmapFont():
    def __init__(self, texture: sf.Texture, char_size: tuple, chars_map=None, spacings_map=None):
        self.texture = texture

        if isinstance(char_size, tuple):
            self.char_size = sf.Vector2(char_size[0], char_size[1])
        else:
            self.char_size = char_size

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
    def __init__(self, string: str, font: BitmapFont = None):
        super().__init__()
        self._font = None
        self.string = string
        self.glyphs_sprites = []
        if font:
            if isinstance(font, BitmapFont):
                self.font = font
            else:
                raise TypeError("BitmapText font argument should be a BitmapFont instance")

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value):
        if isinstance(value, BitmapFont):
            self._font = value
            x = 0
            for character in self.string:
                glyph = self._font.get_glyph(character)
                glyph_spr = self._font.get_glyph_sprite(character)
                glyph_spr.position = (x, 0)
                self.glyphs_sprites.append(glyph_spr)
                x += glyph.spacing

    @property
    def position(self):
        return self.glyphs_sprites[0].position

    @position.setter
    def position(self, value):
        if isinstance(value, tuple):
            value = sf.Vector2(value[0], value[1])
        i = 0
        for spr in self.glyphs_sprites:
            spr.position = value
            value += sf.Vector2(self._font.get_glyph(self.string[i]).spacing, 0)
            i += 1

    def draw(self, target, states):
        if self.font:
            for spr in self.glyphs_sprites:
                target.draw(spr)

