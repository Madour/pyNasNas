from typing import Union, Tuple, List

from sfml import sf

from .data.rect import Rect
from .utils import to_Vector2


class AnimFrame:
    def __init__(self, rectangle: Rect, duration: int, origin: Union[Tuple[int, int], sf.Vector2] = (0, 0)):
        self.rectangle: Rect = rectangle    # texture rectangle of the frame
        self.duration: int = duration       # duration of the frame in milliseconds
        self.origin: Union[Tuple[int, int], sf.Vector2] = to_Vector2(origin)    # origin of the frame


class Anim:
    """Anim is used to describe an animation

    For each frame, it contains data about :

        - texture rectangle       (rect.Rect or sf.Rect instance)
        - duration for each frame (list of int)
        - origin of the frame     ((0,0) by default )

    You can also specify if the animation should loop or not (True by default)
    """
    def __init__(self, frames: List[AnimFrame], loop: bool = True):
        self.frames = frames
        self.frames_count = len(self.frames)
        self.loop = loop


class AnimPlayer:
    def __init__(self, animation: Anim):
        self.anim = animation
        self.active_frame = self.anim.frames[0]
        self.index = 0
        self.playing = True
        self.clock = sf.Clock()

    def play(self, animation: Anim):
        if animation != self.anim:
            self.anim = animation
            self.index = 0
            self.playing = True
            self.clock.restart()

    def stop(self):
        self.playing = False
        self.index = 0
        self.active_frame = self.anim.frames[0]

    def pause(self):
        self.playing = False

    def resume(self):
        self.playing = True

    def update(self):
        if self.playing:
            if self.clock.elapsed_time.milliseconds >= self.anim.frames[self.index].duration:
                self.index += 1
                if self.index >= self.anim.frames_count:
                    if self.anim.loop:
                        self.index = 0
                    else:
                        self.playing = False
                        self.index -= 1
                self.clock.restart()
            self.active_frame = self.anim.frames[self.index]


class Sprite:
    def __init__(self, name: str, texture, anims: dict):
        self.name = name
        self.texture = texture
        self.anims = anims
