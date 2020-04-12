from sfml import sf

from .data.callbacks import callback, HasCallbacks
from .data.game_obj import GameObject
from .camera import Camera


class RenderWindow(GameObject, HasCallbacks, sf.RenderWindow):
    def __init__(self, videomode: sf.VideoMode, title: str, style: sf.Style = sf.Style.DEFAULT):
        super().__init__(videomode, title, style)
        self.style = style
        self.base_videomode = videomode
        self.base_size = sf.Vector2(videomode.width, videomode.height)
        self.base_title = title
        self._ui_view = Camera("ui_view", -1)
        self._ui_view.reset((0, 0), (self.game.V_WIDTH, self.game.V_HEIGHT))
        self._ui_view.reset_viewport((0, 0), (1, 1))

    @property
    def ui_view(self):
        return self._ui_view

    @callback("on_close")
    def on_close(self, user_fn):
        return user_fn

    def close(self):
        super().close()
        self.callbacks.call("on_close")

    def on_resize(self):
        self.game.scale_view()
