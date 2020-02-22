import src.sfmlGameEngine as ge
from sfml import sf
from example.src.data.sprites import Sprites


class Player(ge.entities.PlatformerEntity):
    def __init__(self):
        super().__init__(Sprites.character)
        self.jump_velocity = sf.Vector2(0, -15)

    def update(self, dt, inputs = None):
        if ge.Keyboard.UP in inputs:
            if self.remaining_jumps > 0 and not self.falling:
                self.jump()
            inputs.remove(ge.Keyboard.UP)
        if inputs:
            if ge.Keyboard.DOWN in inputs and self.onground:
                self.idle()
            elif inputs[0] == ge.Keyboard.RIGHT:
                self.walk_right()
            elif inputs[0] == ge.Keyboard.LEFT:
                self.walk_left()
            else:
                self.idle()

        else:
            self.idle()


        super().update(dt)