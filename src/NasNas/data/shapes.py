from sfml import sf
import math

from ..utils import to_Vector2

from typing import Union, Tuple


class EllipseShape(sf.ConvexShape):
    def __init__(self, radius: Union[Tuple[int, int], sf.Vector2]):
        super().__init__()
        self._radius = to_Vector2(radius)
        self.point_count = 30
        self.update()

    def update(self):
        for i in range(self.point_count):
            self.set_point(i, self._calc_point(i))

    def _calc_point(self, index: int):
        pi = 3.141592654
        angle = index * 2 * pi / self.point_count - pi / 2
        x = math.cos(angle) * self._radius.x
        y = math.sin(angle) * self._radius.y

        return sf.Vector2(self._radius.x + x, self._radius.y + y)

    def set_point_count(self, count: int):
        self.point_count = count
        self.update()

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, radius: Union[Tuple[int, int], sf.Vector2]):
        self._radius = to_Vector2(radius)
        self.update()
