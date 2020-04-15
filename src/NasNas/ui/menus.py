from typing import List

from sfml import sf

from ..data.game_obj import GameObject
from ..data.keys import Keyboard
from ..data.callbacks import callback, HasCallbacks
from ..core.utils import to_Vector2
from .buttons import Button
from .styles import MenuStyle, BoxBorder


class Menu(GameObject, HasCallbacks, sf.Drawable):
    def __init__(self, name: str, style: MenuStyle, *args: Button):
        super().__init__()
        self.name = name
        self._style = style
        self._buttons: List[Button] = []
        self.cursor_index = 0
        self.opened = False
        if isinstance(self._style.background, sf.Color):
            self._bg = sf.RectangleShape((self._style.width, self._style.height))
            self._bg.fill_color = self._style.background
        elif isinstance(self._style.background, sf.Texture):
            self._bg = sf.Sprite(self._style.background)
        elif isinstance(self._style.background, BoxBorder):
            texture = self._style.background.generate_texture(self._style.size.x, self._style.size.y)
            self._bg = sf.Sprite(texture)

        self._bg.position = (0, 0)
        for btn in args:
            self.add_button(btn)

    @property
    def style(self):
        return self._style

    @property
    def position(self):
        return self._bg.position

    @position.setter
    def position(self, value):
        self._bg.position = to_Vector2(value)

    @property
    def center(self):
        return self.position + self._style.size / 2

    @center.setter
    def center(self, value):
        self.position = to_Vector2(value) - self._style.size / 2

    @property
    def buttons(self):
        return self._buttons

    def add_button(self, button: Button):
        if isinstance(button, Button):
            self._buttons.append(button)
            button.anim_player.stop()
        else:
            raise TypeError("Menu button should be a Button instance.")

    @callback('on_open')
    def on_open(self, user_fn):
        return user_fn

    def open(self):
        for btn in self._buttons:
            if btn == self._buttons[self.cursor_index]:
                btn.anim_player.resume()
            else:
                btn.anim_player.stop()
        self.game.menus.append(self)
        self.opened = True
        self.callbacks.call("on_open")

    @callback('on_close')
    def on_close(self, user_fn):
        return user_fn

    def close(self):
        self.game.menus.remove(self)
        self.opened = False
        self.callbacks.call("on_close")

    def event_handler(self, event: sf.Event):
        if event == sf.Event.KEY_RELEASED:
            if event['code'] == Keyboard.SPACE:
                self._buttons[self.cursor_index].press()
            elif event['code'] == Keyboard.ESCAPE:
                self.close()
            elif event['code'] == Keyboard.DOWN:
                self._buttons[self.cursor_index].unhover()
                self.cursor_index = (self.cursor_index + 1) % len(self._buttons)
                self._buttons[self.cursor_index].hover()
            elif event['code'] == Keyboard.UP:
                self._buttons[self.cursor_index].unhover()
                self.cursor_index = (self.cursor_index - 1) % len(self._buttons)
                self._buttons[self.cursor_index].hover()

    def update(self):
        for btn in self._buttons:
            btn.update()

    def draw(self, target, states):
        target.draw(self._bg, states)
        for btn in self._buttons:
            target.draw(btn, states)


class VerticalMenu(Menu):
    def __init__(self, name: str, style: MenuStyle, *args: Button):
        super().__init__(name, style, *args)

    def open(self):
        pos = self.position.__copy__() + sf.Vector2(self.style.padding[3], self.style.padding[0])
        for i, btn in enumerate(self._buttons):
            pos += sf.Vector2(0, btn.style.margin[0])
            btn.position = pos
            btn.position += sf.Vector2(btn.style.margin[3], 0)
            pos += sf.Vector2(0, btn.style.bounds.y)
        super().open()
