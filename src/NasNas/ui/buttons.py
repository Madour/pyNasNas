from typing import Union, Tuple

from sfml import sf

from ..data.game_obj import GameObject
from ..data.callbacks import HasCallbacks, callback
from ..core.sprites import AnimPlayer
from ..core.text import BitmapText
from ..core.utils import to_Vector2
from .styles import ButtonStyle


class Button(GameObject, HasCallbacks, sf.Drawable):
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
    def style(self):
        return self._style

    @property
    def size(self):
        return self._style.size

    @property
    def position(self):
        return self._bg.position

    @position.setter
    def position(self, value):
        self._position = to_Vector2(value)
        self._bg.position = self._position
        self._front.position = self._position + self._style.size / 2 \
                               - sf.Vector2(self._front.global_bounds.width / 2, self._front.global_bounds.height / 2)

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
        self._front.position = self._position + sf.Vector2(self.style.width, self.style.height) / 2\
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
