from sfml import sf
from .data.game_obj import GameObject


class Camera(GameObject, sf.View):
    def __init__(self):
        super().__init__()
        self.reference = None
        self.frames_delay = 15
        self.size = (0, 0)

    def reset(self, position: tuple, size: tuple):
        if type(position) in [tuple, sf.Vector2]:
            if isinstance(position, tuple):
                super().reset(sf.Rect(position, size))
                self.size = sf.Vector2(size[0], size[1])
            elif isinstance(position, sf.Vector2):
                super().reset(sf.Rect(position, size))
                self.size = size
        else:
            raise TypeError("position argument of Camera.reset() should be a tuple.")

    @property
    def position(self):
        return sf.Vector2(self.left, self.top)

    @property
    def left(self):
        return self.center.x - self.size.x / 2

    @left.setter
    def left(self, value: int):
        self.center = (value + self.size.x / 2, self.center.y)

    @property
    def top(self):
        return self.center.y - self.size.y / 2

    @top.setter
    def top(self, value: int):
        self.center = (self.center.x, value + self.size.y/2)

    @property
    def right(self):
        return self.center.x + self.size.x / 2

    @right.setter
    def right(self, value: int):
        self.center = (value - self.size.x/2, self.center.y)

    @property
    def bottom(self):
        return self.center.y + self.size.y / 2

    @bottom.setter
    def bottom(self, value: int):
        self.center = (self.center.x, value - self.size.y / 2)

    def follow(self, entity):
        self.reference = entity

    def look_at(self, position: tuple):
        self.center = position

    def update(self, dt):
        if self.reference:
            dif = self.reference.position - self.center
            if self.frames_delay > 0:
                self.move(dif.x/self.frames_delay, dif.y/self.frames_delay)
                if self.left < 0:
                    self.left = 0
                elif self.right > self.game.level.width*16:
                    self.right = self.game.level.width*16

                if self.top < 0:
                    self.top = 0
                elif self.bottom > self.game.level.height*16:
                    self.bottom = self.game.level.height*16
            else:
                self.center = self.reference.position
