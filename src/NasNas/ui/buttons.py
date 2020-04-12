from typing import Union, Tuple

from sfml import sf

from ..data.callbacks import HasCallbacks, callback
from ..sprites import Anim, AnimPlayer
from ..text import BitmapText, BitmapFont
from ..utils import to_Vector2


class ButtonStyle:
    __slots__ = ["size", "width", "height", "padding", "font",
                 "color", "font_size", "background", "anim"]

    def __init__(self,
                 width: int = 0, height: int = 0,
                 padding: Tuple[int, int, int, int] = (0, 0, 0, 0),
                 font: Union[sf.Font, BitmapFont] = None,
                 color: sf.Color = sf.Color.WHITE,
                 font_size: int = 16,
                 background: Union[sf.Color, sf.Texture] = sf.Color.TRANSPARENT,
                 anim: Anim = None,
                 ):
        self.width = width
        self.height = height
        self.size = sf.Vector2(self.width, self.height)
        self.padding = padding
        self.font = font
        self.color = color
        self.font_size = font_size
        self.background = background
        self.anim = anim


class Button(HasCallbacks, sf.Drawable):
    def __init__(self, text: str, style: ButtonStyle = ButtonStyle(),
                 position: Union[Tuple[float, float], sf.Vector2] = (0, 0)):
        super().__init__()
        self._text = text
        self._position = to_Vector2(position)
        self._style = style
        self._render_texture = sf.RenderTexture(self._style.width, self._style.height)
        self.anim_player = AnimPlayer(self._style.anim)

        self._create()

    @property
    def position(self):
        return self._bg.position

    @position.setter
    def position(self, value):
        self._position = value
        self._create()

    def _create(self):
        self.anim_player.play(self._style.anim)
        if isinstance(self._style.background, sf.Color):
            self._bg = sf.RectangleShape((self._style.width, self._style.height))
            self._bg.fill_color = self._style.background
        else:
            self._bg = sf.Sprite(self._style.background)
            if self._style.anim is not None:
                self._bg.texture_rectangle = self._style.anim.frames[0].rectangle
        self._bg.position = self._position

        if isinstance(self._style.font, sf.Font):
            self._front = sf.Text(self._text)
            self._front.font = self._style.font
            self._front.character_size = self._style.font_size
        else:
            self._front = BitmapText(self._text, self._style.font)
            self._front.font = self._style.font
        self._front.position = self._position + self._style.size / 2 \
                               - sf.Vector2(self._front.global_bounds.width / 2, self._front.global_bounds.height / 2) \
                               - sf.Vector2(self._front.global_bounds.left, self._front.global_bounds.top)

    @callback("on_press")
    def on_press(self, user_fn):
        return user_fn

    def press(self):
        self.callbacks.call("on_press")

    def update(self):
        if isinstance(self._bg, sf.Sprite):
            self._bg.texture_rectangle = self.anim_player.active_frame.rectangle
            self.anim_player.update()
            self._bg.origin = self.anim_player.active_frame.origin

    def draw(self, target, states):
        target.draw(self._bg, states)
        target.draw(self._front, states)
