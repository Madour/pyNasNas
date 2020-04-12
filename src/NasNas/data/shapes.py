from typing import Union, Tuple
import math

from sfml import sf

from ..core.utils import to_Vector2


class LineShape(sf.Drawable):
    def __init__(self, *args: Union[Tuple[float, float], sf.Vector2]):
        super().__init__()
        self._points = []
        self._position = sf.Vector2(0, 0)
        self._vertexarray = sf.VertexArray(sf.PrimitiveType.LINES_STRIP)
        self._color = sf.Color.WHITE
        for arg in args:
            self._points.append(to_Vector2(arg))
        self.update()

    @property
    def point_count(self) -> int:
        return len(self._points)

    @property
    def position(self) -> sf.Vector2:
        return self._position

    @position.setter
    def position(self, pos: Union[Tuple[float, float], sf.Vector2]):
        self._position = to_Vector2(pos)
        self.update(offset=True)

    @property
    def color(self) -> sf.Color:
        return self._color

    @color.setter
    def color(self, color: sf.Color):
        self._color = color
        self.update(color=True)

    def add_point(self, point: Union[Tuple[float, float], sf.Vector2]):
        self._points.append(to_Vector2(point))
        self.update(append=True)

    def remove_point(self, index: int):
        if index >= len(self._points):
            raise IndexError(f"Point number {index} out of range.")
        else:
            self._points.pop(index)
            self.update()

    def update(self, append=False, color=False, offset=False):
        if append:
            self._vertexarray.resize(self.point_count)
            self._vertexarray.append(sf.Vertex(position=self._points[-1], color=self._color))
        if color:
            for i in range(self.point_count):
                self._vertexarray[i].color = self._color
        if offset:
            for vertex in self._vertexarray:
                vertex.position += self._position
        if not color and not append and not offset:
            self._vertexarray.resize(self.point_count)
            for i in range(self.point_count):
                self._vertexarray[i].position = self._points[i]
                self._vertexarray[i].color = self._color

    def draw(self, target, states):
        target.draw(self._vertexarray, states)


class EllipseShape(sf.ConvexShape):
    def __init__(self, radius: Union[Tuple[float, float], sf.Vector2]):
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
