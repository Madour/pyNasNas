from sfml import sf

from ..data.game_obj import GameObject
from . import transitions


class Layer(GameObject, sf.Drawable):
    """
    A Layer is a collection of Drawables. It can be drawn on the window.
    Used to organize the order of drawing in the game.
    """
    def __init__(self, name: str, *args: sf.Drawable):
        super().__init__()
        self.name = name
        self._drawables = []
        for arg in args:
            if isinstance(arg, sf.Drawable):
                self._drawables.append(arg)
            else:
                raise TypeError("Layer can only contain Drawables.")

    def add(self, *args: sf.Drawable):
        for arg in args:
            if isinstance(arg, sf.Drawable):
                self._drawables.append(arg)
            else:
                raise TypeError("You can only add Drawables to Layer")

    def remove(self, drawable: sf.Drawable):
        if drawable in self._drawables:
            self._drawables.remove(drawable)

    def ysort(self):
        """Sort all drawables of the layer by y position
        """
        self._drawables.sort(key=lambda x: x.position.y)

    def update(self):
        to_remove = []
        for spr in self._drawables:
            if isinstance(spr, transitions.Transition):
                if spr.ended:
                    to_remove.append(spr)
        for tr in to_remove:
            self._drawables.remove(tr)

    def draw(self, target, states):
        for drawable in self._drawables:
            if isinstance(drawable, transitions.Transition):
                if drawable.started:
                    target.draw(drawable, states)
            else:
                target.draw(drawable, states)

    def __iter__(self):
        return iter(self._drawables)


class Mask(GameObject, sf.Drawable):
    def __init__(self, name: str, width: int, height: int, fill_color: sf.Color, *args: sf.Drawable):
        super().__init__()
        self.name = name
        self.fill_color = fill_color
        self.render_texture = sf.RenderTexture(width, height)
        self.sprite = sf.Sprite(self.render_texture.texture)
        self._drawables = []
        for arg in args:
            if isinstance(arg, sf.Drawable):
                self._drawables.append(arg)
            else:
                raise TypeError("Mask can only contain Drawables.")

    def add(self, *args: sf.Drawable):
        for arg in args:
            if isinstance(arg, sf.Drawable):
                self._drawables.append(arg)
            else:
                raise TypeError("Mask can only contain Drawables.")

    def update(self):
        self.render_texture.clear(self.fill_color)
        for drawable in self._drawables:
            self.render_texture.draw(drawable, sf.RenderStates(sf.BLEND_NONE))
        self.render_texture.display()
        self.sprite = sf.Sprite(self.render_texture.texture)

    def draw(self, target, states):
        target.draw(self.sprite, states)

    def __iter__(self):
        return iter(self._drawables)
