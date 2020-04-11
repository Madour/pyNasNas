from sfml import sf
from typing import Union, Tuple


class Rect(sf.Rect):
    def __init__(self, pos: Union[Tuple[float, float], sf.Vector2], size: Union[Tuple[float, float], sf.Vector2]):
        super().__init__(pos, size)

    @property
    def size(self):
        return sf.Vector2(self.width, self.height)

    @property
    def right(self):
        return self.left + self.width

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def topleft(self):
        return sf.Vector2(self.left, self.top)

    @property
    def bottomleft(self):
        return sf.Vector2(self.left, self.bottom)

    @property
    def topright(self):
        return sf.Vector2(self.right, self.top)

    @property
    def bottomright(self):
        return sf.Vector2(self.right, self.bottom)

    @property
    def center(self):
        return sf.Vector2(self.left + self.width/2, self.top + self.height/2)

    @property
    def topcenter(self):
        return sf.Vector2(self.center.x, self.top)

    def intersects(self, other_rect):
        if isinstance(other_rect, Rect):
            if self.left >= other_rect.right or \
                    self.right <= other_rect.left or \
                    self.top >= other_rect.bottom or \
                    self.bottom <= other_rect.top:
                return False
            return True
        elif isinstance(other_rect, sf.Rect):
            if self.left >= other_rect.left + other_rect.width or \
                    self.left + self.width <= other_rect.left or \
                    self.top >= other_rect.top + other_rect.height or \
                    self.top + self.height <= other_rect.top:
                return False
            return True