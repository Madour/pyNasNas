from sfml import sf
from .data.game_obj import GameObject
from functools import wraps


class RenderWindow(GameObject, sf.RenderWindow):
    def __init__(self, videomode: sf.VideoMode, title: str, style: sf.Style = sf.Style.DEFAULT):
        super().__init__(videomode, title, style)
        self.style = style
        self.base_videomode = videomode
        self.base_size = sf.Vector2(videomode.width, videomode.height)
        self.base_title = title
        self._callbacks = {"on_close": lambda: None}

    def on_close(self, fn):
        @wraps(fn)
        def wrapper():
            return fn()

        self._set_close_callback(wrapper)
        return wrapper

    def close(self):
        self._callbacks["on_close"]()
        super().close()

    def on_resize(self):
        self.game.scale_view()

    def _set_close_callback(self, fn, ):
        self._callbacks["on_close"] = fn
