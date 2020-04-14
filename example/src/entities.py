from sfml import sf
import src.NasNas as ns

from example.src.sprites import Sprites


class Player(ns.PlatformerEntity):
    def __init__(self, name):
        super().__init__(name, Sprites.character)
        self.jump_velocity = sf.Vector2(0, -15)
        self.score = 0

    def update(self, dt, inputs=None):
        if self.controls['up'] in inputs:
            if self.remaining_jumps > 0 and not self.falling:
                self.jump()
            inputs.remove(self.controls['up'])

        if inputs:
            for key in inputs:
                if key == self.controls['down'] and self.onground:
                    self.idle()
                    break
                elif key == self.controls['right']:
                    self.walk_right()
                    break
                elif key == self.controls['left']:
                    self.walk_left()
                    break
        else:
            self.idle()

        to_remove = []
        for coin in self.game.coins:
            if self.global_bounds.intersects(coin.global_bounds):
                self.score += 1
                self.game.entities_layer.remove(coin)
                to_remove.append(coin)
        self.game.coins = [c for c in self.game.coins if c not in to_remove]

        super().update(dt)


class Light(sf.Drawable):
    def __init__(self, position, fill_color):
        super().__init__()
        self.growing = True
        self.sprite = sf.CircleShape(33)
        self.sprite.fill_color = sf.Color(fill_color.r, fill_color.g, fill_color.b, 50)
        self.sprite.position = position - sf.Vector2(0, 5)
        self.sprite2 = sf.CircleShape(50)
        self.sprite2.fill_color = sf.Color(fill_color.r, fill_color.g, fill_color.b, 190)
        self.sprite2.position = position - sf.Vector2(0, 5)

    def update(self):
        # doing the light animation
        if self.sprite.radius < 33 and self.light_growing:
            self.sprite.radius += 0.015
            self.sprite2.radius += 0.05
            self.sprite.origin = (self.sprite.radius, self.sprite.radius + 10)
            self.sprite2.origin = (self.sprite2.radius, self.sprite2.radius + 10)
        else:
            self.light_growing = False

        if not self.light_growing and self.sprite.radius > 30:
            self.sprite.radius -= 0.015
            self.sprite2.radius -= 0.05
            self.sprite.origin = (self.sprite.radius, self.sprite.radius + 10)
            self.sprite2.origin = (self.sprite2.radius, self.sprite2.radius + 10)
        else:
            self.light_growing = True

    @property
    def position(self):
        return self.sprite.position

    @position.setter
    def position(self, value):
        self.sprite.position = value
        self.sprite2.position = value

    def draw(self, target, states):
        target.draw(self.sprite2, states)
        target.draw(self.sprite, states)
