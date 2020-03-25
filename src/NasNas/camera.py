from sfml import sf
import random as rand
from .data.game_obj import GameObject
from typing import Union, Optional


class Camera(GameObject, sf.View):
    def __init__(self, name, render_order):
        super().__init__()
        self.name = name
        self.render_order = render_order
        self.reference = None
        self.state = CameraState()
        self.frames_delay = 15
        self.base_pos = sf.Vector2(0, 0)
        self.base_size = sf.Vector2(0, 0)
        self.vp_base_pos = sf.Vector2(0, 0)
        self.vp_base_size = sf.Vector2(1, 1)
        self.offset = sf.Vector2(0, 0)
        self.visible : bool = True
        self._scene = []

    def reset(self, position: Union[sf.Vector2, tuple], size: Union[sf.Vector2, tuple]):
        if type(position) in [sf.Vector2, tuple] and type(size) in [sf.Vector2, tuple]:
            super().reset(sf.Rect(position, size))
            if isinstance(position, sf.Vector2):
                self.base_pos = position
            else:
                self.base_pos = sf.Vector2(position[0], position[1])
            if isinstance(size, sf.Vector2):
                self.base_size = size
            else:
                self.base_size = sf.Vector2(size[0], size[1])
        else:
            raise TypeError("position and size arguments of Camera.reset() should be a sf.Vector or tuple.")

    def reset_viewport(self,position: Union[sf.Vector2, tuple], size: Union[sf.Vector2, tuple]):
        if type(position) in [sf.Vector2, tuple] and type(size) in [sf.Vector2, tuple]:
            self.viewport = sf.Rect(position, size)
            if isinstance(position, sf.Vector2):
                self.vp_base_pos = position
            else:
                self.vp_base_pos = sf.Vector2(position[0], position[1])
            if isinstance(size, sf.Vector2):
                self.vp_base_size = size
            else:
                self.vp_base_size = sf.Vector2(size[0], size[1])
        else:
            raise TypeError("position and size arguments of Camera.reset_viewport() should be a sf.Vector or tuple.")

    @property
    def scene(self):
        return self._scene[0]

    @scene.setter
    def scene(self, val):
        if not self._scene:
            self._scene.append(val)
        else:
            self._scene[0] = val

    def has_scene(self):
        if self._scene:
            return True
        return False

    @property
    def position(self):
        return sf.Vector2(self.left, self.top)

    @property
    def size(self):
        return sf.Vector2(self.base_size.x, self.base_size.y)

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

    def quake(self, duration: float, amplitude: int, horizontal:bool=True, vertical:bool=True):
        self.state = QuakeState(duration, amplitude, horizontal, vertical)

    def update(self, dt):
        self.move( - self.offset.x, - self.offset.y)

        if self.reference:
            dif = self.reference.position - self.center - self.offset
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

        self.offset = self.state.offset
        self.move(self.offset.x, self.offset.y)

        if self.state.expired:
            self.state = CameraState()


class CameraState:
    def __init__(self):
        self.name = "idle"
        self.timer = sf.Clock()
        self.duration: Optional[float] = None

    @property
    def offset(self) -> sf.Vector2:
        return sf.Vector2(0, 0)

    @property
    def expired(self) -> bool:
        if not self.duration:
            return False
        return self.timer.elapsed_time.seconds >= self.duration


class QuakeState(CameraState):
    def __init__(self, duration:float, amplitude:int, horizontal:bool=True, vertical:bool=True):
        super().__init__()
        self.name = "quake"
        self.duration = duration
        self.amplitude = amplitude
        self.direction = sf.Vector2(0, 0)
        self.direction.x = 1 if horizontal else 0
        self.direction.y = 1 if vertical else 0

    @property
    def offset(self) -> sf.Vector2:
        ratio = 1 - self.timer.elapsed_time.seconds/self.duration
        offx = rand.randrange(-self.amplitude, self.amplitude, 1)
        offy = rand.randrange(-self.amplitude, self.amplitude, 1)
        return sf.Vector2(offx*self.direction.x*ratio, offy*self.direction.y*ratio)


