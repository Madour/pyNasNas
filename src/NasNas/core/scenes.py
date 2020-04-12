from typing import Dict

from sfml import sf

from ..data.game_obj import GameObject
from . import layers


class Scene(GameObject, sf.Drawable):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.render_texture: sf.RenderTexture = sf.RenderTexture(width, height)
        self.sprite: sf.Sprite = sf.Sprite(self.render_texture.texture)
        self.layers: Dict[int, layers.Layer] = {}
        self.masks: Dict[int, layers.Mask] = {}

    @property
    def width(self) -> int:
        return self.render_texture.width

    @property
    def height(self) -> int:
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
                self.layers = {key: val for key, val in self.layers.items() if val != layer}
        elif order:
            if order in self.layers.keys():
                self.layers.pop(order)

    def get_layer(self, name: str = None, order: int = None) -> layers.Layer:
        for layer_order, layer in self.layers.items():
            if name is not None and order is not None:
                if self.layers[order].name != name:
                    raise IndexError(f"Requested order {order} and name {name} does not match")
            if name is not None:
                if layer.name == name:
                    return layer
            if order is not None:
                if layer_order == order:
                    return layer

    def add_mask(self, mask: layers.Mask, order: int):
        if isinstance(mask, layers.Mask):
            self.masks[order] = mask
        else:
            raise TypeError("Argument mask should be a Mask instance.")

    def remove_mask(self, mask: layers.Mask):
        if mask in self.masks.values():
            self.masks = {key: val for key, val in self.masks.items() if val != mask}

    def render(self):
        self.render_texture.clear(sf.Color.TRANSPARENT)

        max_layers_order = max(self.layers.keys()) if self.layers.keys() else 0
        max_masks_order = max(self.masks.keys()) if self.masks.keys() else 0

        for i in range(max(max_layers_order, max_masks_order)+1):
            if i in self.layers:
                self.layers[i].update()
                self.render_texture.draw(self.layers[i])
            if i in self.masks:
                self.masks[i].update()
                self.render_texture.draw(self.masks[i])

        self.render_texture.display()
        self.sprite.texture = self.render_texture.texture

    def draw(self, target, states):
        target.draw(self.sprite)
