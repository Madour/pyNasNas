import math
import random

from sfml import sf

from ..data.callbacks import callback, HasCallbacks
from ..data.game_obj import GameObject


class Transition(GameObject, HasCallbacks, sf.Drawable):
    def __init__(self):
        if self.__class__.__name__ == __class__.__name__:
            raise NotImplementedError("Transition class is not instantiable. Please use inheritance to create a Transition.")
        super().__init__()
        self.render_texture = sf.RenderTexture(self.game.window.ui_view.size.x, self.game.window.ui_view.size.y)
        self.r = self.g = self.b = 0
        self.a = 255
        self.blend_mode = sf.BLEND_NONE
        self.shapes = []
        self.sprite = sf.Sprite(self.render_texture.texture)
        self.ended = False
        self.started = False

    def reset(self):
        self.render_texture = sf.RenderTexture(self.game.window.ui_view.size.x, self.game.window.ui_view.size.y)
        self.r = self.g = self.b = 0
        self.a = 255
        self.blend_mode = sf.BLEND_NONE
        self.shapes = []
        self.sprite = sf.Sprite(self.render_texture.texture)
        self.ended = False
        self.started = False

    @property
    def width(self):
        return self.render_texture.size.x

    @property
    def height(self):
        return self.render_texture.size.y

    @property
    def fill_color(self):
        return sf.Color(self.r, self.g, self.b, self.a)

    @fill_color.setter
    def fill_color(self, value: sf.Color):
        self.r = value.r
        self.g = value.g
        self.b = value.b
        self.a = value.a

    def start(self):
        if not self.started:
            self.started = True
            self.game.transitions.append(self)
            self.callbacks.call("on_start")

    @callback("on_start")
    def on_start(self, user_fn):
        return user_fn

    def end(self):
        if not self.ended:
            self.ended = True
            self.game.transitions.remove(self)
            self.callbacks.call("on_end")

    @callback("on_end")
    def on_end(self, user_fn):
        return user_fn

    @staticmethod
    def updater(update_func):
        def _decorate(self):
            if not self.ended:
                self.render_texture.clear(self.fill_color)
                if self.started:
                    update_func(self)
                for shape in self.shapes:
                    self.render_texture.draw(shape, sf.RenderStates(self.blend_mode))
                self.render_texture.display()
                self.sprite.texture = self.render_texture.texture
        return _decorate

    def update(self):
        pass

    def draw(self, target, transformations):
        target.draw(self.sprite)


class FadeInTransition(Transition):
    """ Fade transition from black screen to transparent"""
    def __init__(self, speed=5):
        super().__init__()
        self.speed = speed
        self.reset()

    def reset(self):
        super().reset()
        self.a = 255
        self.update()

    @Transition.updater
    def update(self):
        self.a -= self.speed
        if self.a <= 0:
            self.a = 0
            self.end()


class FadeOutTransition(Transition):
    """ Fade transition from transparent to black screen"""
    def __init__(self, speed=5):
        super().__init__()
        self.speed = speed
        self.reset()

    def reset(self):
        super().reset()
        self.a = 0
        self.update()

    @Transition.updater
    def update(self):
        self.a += self.speed
        if self.a >= 255:
            self.a = 255
            self.end()


class CircleOpenTransition(Transition):
    def __init__(self, speed=5):
        super().__init__()
        self.speed = speed
        self.limit = math.sqrt((self.width/2)**2 + (self.height/2)**2)
        self.reset()

    def reset(self):
        super().reset()
        shape = sf.CircleShape(0.1)
        shape.origin = (0.1, 0.1)
        shape.position = (self.width / 2, self.height / 2)
        shape.fill_color = sf.Color.TRANSPARENT
        self.shapes.append(shape)
        self.update()

    @Transition.updater
    def update(self):
        if self.shapes[0].radius > self.limit:
            self.end()
        elif self.shapes[0].radius <= self.limit:
            self.shapes[0].radius += self.speed
        else:
            self.shapes[0].radius = 0
        self.shapes[0].origin = (self.shapes[0].radius, self.shapes[0].radius)


class CircleCloseTransition(Transition):
    """ Closing circle transition"""
    def __init__(self, speed=5):
        super().__init__()
        self.speed = speed
        self.reset()

    def reset(self):
        super().reset()
        shape = sf.CircleShape(math.sqrt((self.width/2)**2 + (self.height/2)**2))
        shape.origin = (shape.radius, shape.radius)
        shape.position = (self.width / 2, self.height / 2)
        shape.fill_color = sf.Color.TRANSPARENT
        self.shapes.append(shape)
        self.update()

    @Transition.updater
    def update(self):
        if self.shapes[0].radius == 0:
            self.end()
        elif self.shapes[0].radius >= self.speed:
            self.shapes[0].radius -= self.speed
        else:
            self.shapes[0].radius = 0
        self.shapes[0].origin = (self.shapes[0].radius, self.shapes[0].radius)


class RotatingSquareOpenTransition(Transition):
    def __init__(self, speed=5):
        super().__init__()
        self.speed = speed
        self.limit = math.sqrt((self.width/2)**2 + (self.height/2)**2)
        self.shape = sf.RectangleShape()
        self.shape.position = (self.width/2, self.height/2)
        self.shape.size = (0.1, 0.1)
        self.shape.origin = (0.05, 0.05)
        self.shape.fill_color = sf.Color.TRANSPARENT
        self.shapes.append(self.shape)
        self.update()

    @Transition.updater
    def update(self):
        if self.shape.size.x/2 > self.limit:
            self.end()
        elif self.shape.size.x/2 <= self.limit:
            self.shape.size += sf.Vector2(self.speed, self.speed)
            self.shape.rotate(self.speed*2)
        self.shape.origin = (self.shape.size.x/2, self.shape.size.y/2)


class RotatingSquareCloseTransition(Transition):
    def __init__(self, speed: int = 5):
        super().__init__()
        self.speed = speed
        self.reset()

    def reset(self):
        super().reset()
        shape = sf.RectangleShape()
        shape.position = (self.width / 2, self.height / 2)
        shape.size = (self.width, self.width)
        shape.origin = (self.width / 2, self.width / 2)
        shape.fill_color = sf.Color.TRANSPARENT
        self.shapes.append(shape)
        self.update()

    @Transition.updater
    def update(self):
        if self.shapes[0].size.x == 0:
            self.end()
        elif self.shapes[0].size.x > self.speed:
            self.shapes[0].size -= sf.Vector2(self.speed, self.speed)
            self.shapes[0].rotate(self.speed*2)
        else:
            self.shapes[0].size = (0, 0)
        self.shapes[0].origin = (self.shapes[0].size.x/2, self.shapes[0].size.y/2)


class PixelsInTransition(Transition):
    """ From black screen to transparent square by square """
    def __init__(self, speed: int, pixelsize: float):
        """ Warning : a small pixelsize and big speed will lead to severe frame drops.
            Avoid using a pixelsize smaller than 8.
        """
        super().__init__()
        self.speed = speed
        self.pixel_size = pixelsize
        self.remaining = []
        self.reset()

    def reset(self):
        super().reset()
        self.remaining = []
        col_nb = math.ceil(self.render_texture.size.x / self.pixel_size)
        row_nb = math.ceil(self.render_texture.size.y / self.pixel_size)
        for x in range(col_nb):
            for y in range(row_nb):
                s = sf.RectangleShape()
                s.position = (x * self.pixel_size, y * self.pixel_size)
                s.size = (self.pixel_size, self.pixel_size)
                s.fill_color = sf.Color.BLACK
                self.shapes.append(s)
                self.remaining.append(s)
        self.update()

    @Transition.updater
    def update(self):
        if self.remaining:
            for i in range(self.speed):
                s = random.choice(self.remaining)
                s.fill_color = sf.Color.TRANSPARENT
                self.remaining.remove(s)
                if not self.remaining:
                    break
        else:
            self.end()


class PixelsOutTransition(Transition):
    """ From transparent screen to black screen square by square """
    def __init__(self, speed: int, pixelsize: float):
        """ Warning : a small pixelsize and big speed will lead to severe frame drops.
            Avoid using a pixelsize smaller than 8.
        """
        super().__init__()
        self.speed = speed
        self.pixel_size = pixelsize
        self.shapes = []
        self.remaining = []

    def reset(self):
        super().reset()
        self.remaining = []
        col_nb = math.ceil(self.render_texture.size.x / self.pixel_size)
        row_nb = math.ceil(self.render_texture.size.y / self.pixel_size)
        for x in range(col_nb):
            for y in range(row_nb):
                s = sf.RectangleShape()
                s.position = (x * self.pixel_size, y * self.pixel_size)
                s.size = (self.pixel_size, self.pixel_size)
                s.fill_color = sf.Color.TRANSPARENT
                self.shapes.append(s)
                self.remaining.append(s)
        self.update()

    @Transition.updater
    def update(self):
        if self.remaining:
            for i in range(self.speed):
                s = random.choice(self.remaining)
                s.fill_color = sf.Color.BLACK
                self.remaining.remove(s)
                if not self.remaining:
                    break
        else:
            self.end()
