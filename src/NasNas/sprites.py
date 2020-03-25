class Anim:
    """Anim is used to describe an animation

    For each frame, it contains data about :

        - texture rectangle       (rect.Rect or sf.Rect instance)
        - duration for each frame (list of int)
        - origin of the frame     ((0,0) by default )

    You can also specify if the animation should loop or not (True by default)
    """
    def __init__(self, texture_rectangles: list, frames_duration: list, origins: list = None, loop: bool = True):
        self.frames = texture_rectangles
        self.frames_count = len(frames_duration)
        self.frames_duration = frames_duration
        self.frames_origin = origins
        self.loop = loop


class Sprite:
    def __init__(self, name: str, texture, anims: dict):
        self.name = name
        self.texture = texture
        self.anims = anims