from typing import List

from sfml import sf

from ..data.game_obj import GameObject
from ..data.keys import Keyboard
from .buttons import Button


class Menu(GameObject, sf.Drawable):
    def __init__(self, name: str, *args: Button):
        super().__init__()
        self.name = name
        self._buttons: List[Button] = []
        self._cursor_index = 0
        self.opened = False
        for arg in args:
            self.add_button(arg)
        self._buttons[0].anim_player.resume()

    def add_button(self, button: Button):
        if isinstance(button, Button):
            self._buttons.append(button)
            button.anim_player.stop()
        else:
            raise TypeError("Menu button should be a Button instance.")

    def open(self):
        self.game.menus.append(self)
        self.opened = True

    def close(self):
        self.opened = False
        self.game.menus.remove(self)

    def event_handler(self, event: sf.Event):
        if event == sf.Event.KEY_RELEASED:
            if event['code'] == Keyboard.SPACE:
                self._buttons[self._cursor_index].press()
            elif event['code'] == Keyboard.ESCAPE:
                self.close()
            elif event['code'] == Keyboard.DOWN:
                self._buttons[self._cursor_index].anim_player.stop()
                self._cursor_index = (self._cursor_index + 1) % len(self._buttons)
                self._buttons[self._cursor_index].anim_player.resume()
            elif event['code'] == Keyboard.UP:
                self._buttons[self._cursor_index].anim_player.stop()
                self._cursor_index = (self._cursor_index - 1) % len(self._buttons)
                self._buttons[self._cursor_index].anim_player.resume()

    def update(self):
        for btn in self._buttons:
            btn.update()

    def draw(self, target, states):
        for btn in self._buttons:
            target.draw(btn, states)
