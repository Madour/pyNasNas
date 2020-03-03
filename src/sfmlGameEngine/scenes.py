from .data.game_obj import GameObject
from . import layers
from sfml import sf


class Scene(GameObject, sf.Drawable):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.render_texture = sf.RenderTexture(width, height)
        self.sprite = sf.Sprite(self.render_texture.texture)
        self.layers = {}
        self.masks = []

    @property
    def width(self):
        return self.render_texture.width

    @property
    def height(self):
        return self.render_texture.height

    def add_layer(self, layer: layers.Layer, order: int):
        """ Adds a Layer to the scene at the given order
        Order 0 will be drawn first on the scene, then 1, then 2 etc
        """
        if isinstance(layer, layers.Layer):
            self.layers[order] = layer
        else:
            raise TypeError("Argument layer should be a Layer instance.")

    def remove_layer(self, layer: layers.Layer = None, order: int = None):
        if layer:
            if layer in self.layers.values():
                self.layers = {key:val for key, val in self.layers.items() if val != layer}
        elif order:
            if order in self.layers.keys():
                self.layers.pop(order)

    def get_layer(self, name: str) -> layers.Layer:
        for order, layer in self.layers.items():
            if layer.name == name:
                return layer

    def add_mask(self, mask: layers.Mask):
        if isinstance(mask, layers.Mask):
            self.masks.append(mask)
        else:
            raise TypeError("Argument mask should be a Mask instance.")

    def remove_mask(self, mask: layers.Mask):
        if mask in self.masks:
            self.masks.remove(mask)

    def update(self):
        self.render_texture.clear(sf.Color.TRANSPARENT)
        sorted_layers = [layer for order, layer in sorted(self.layers.items(), key=lambda item: item[0])]
        for layer in sorted_layers:
            self.render_texture.draw(layer)

        for mask in self.masks:
            mask.update()
            self.render_texture.draw(mask)
        self.render_texture.display()
        self.sprite.texture = self.render_texture.texture

    def draw(self, target, states):
        target.draw(self.sprite)

