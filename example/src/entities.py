from sfml import sf
import src.NasNas as ns

from example.src.data.sprites import Sprites


class Player(ns.PlatformerEntity):
    def __init__(self, name):
        super().__init__(name, Sprites.character)
        self.jump_velocity = sf.Vector2(0, -15)

    def update(self, dt, inputs = None):
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

        super().update(dt)
