from sfml import sf
from .data.game_obj import GameObject
import math
import random


class Transition(GameObject, sf.Drawable):
    def __init__(self):
        if self.__class__.__name__ == __class__.__name__:
            raise NotImplementedError("Transition class is not instantiable. Please use inheritance to create a Transition.")
        super().__init__()
        self.render_texture = sf.RenderTexture(self.game._default_view.size.x, self.game._default_view.size.y)
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

    def start(self):
        self.started = True
        self.game.transitions.append(self)
        self.on_start()

    def on_start(self):
        pass

    def end(self):
        self.ended = True
        self.on_end()
        self.game.transitions.remove(self)

    def on_end(self):
        pass

    @staticmethod
    def update_handler(update_func):
        def _decorate(self):
            if not self.ended:
                self.render_texture.clear(sf.Color(self.r, self.g, self.b, self.a))
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


class FadeIn(Transition):
    """ Fade transition from black screen to transparent"""
    def __init__(self, speed=5):
        super().__init__()
        self.a = 255
        self.speed = speed
        self.update()

    @Transition.update_handler
    def update(self):
        self.a -= self.speed
        if self.a <= 0:
            self.a = 0
            self.end()


class FadeOut(Transition):
    """ Fade transition from transparent to black screen"""
    def __init__(self, speed=5):
        super().__init__()
        self.a = 0
        self.speed = speed
        self.update()

    @Transition.update_handler
    def update(self):
        self.a += self.speed
        if self.a >= 255:
            self.a = 255
            self.end()


class CircleOpen(Transition):
    def __init__(self, speed=5):
        super().__init__()
        self.speed = speed
        self.limit = math.sqrt((self.width/2)**2 + (self.height/2)**2)
        self.shape = sf.CircleShape(0.1)
        self.shape.origin = (0.1, 0.1)
        self.shape.position = (self.width/2, self.height/2)
        self.shape.fill_color = sf.Color.TRANSPARENT
        self.shapes.append(self.shape)
        self.update()

    @Transition.update_handler
    def update(self):
        if self.shape.radius > self.limit:
            self.end()
        elif self.shape.radius <= self.limit:
            self.shape.radius += self.speed
        else:
            self.shape.radius = 0
        self.shape.origin = (self.shape.radius, self.shape.radius)


class CircleClose(Transition):
    """ Closing circle transition"""
    def __init__(self, speed=5):
        super().__init__()
        self.speed = speed
        self.shape = sf.CircleShape(self.width + self.height/2)
        self.shape.origin = (self.shape.radius, self.shape.radius)
        self.shape.position = (self.width/2, self.height/2)
        self.shape.fill_color = sf.Color.TRANSPARENT
        self.shapes.append(self.shape)
        self.update()

    @Transition.update_handler
    def update(self):
        if self.shape.radius == 0:
            self.end()
        elif self.shape.radius >= self.speed:
            self.shape.radius -= self.speed
        else:
            self.shape.radius = 0
        self.shape.origin = (self.shape.radius, self.shape.radius)


class RotatingSquareOpen(Transition):
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

    @Transition.update_handler
    def update(self):
        if self.shape.size.x/2 > self.limit:
            self.end()
        elif self.shape.size.x/2 <= self.limit:
            self.shape.size += sf.Vector2(self.speed, self.speed)
            self.shape.rotate(self.speed*2)
        self.shape.origin = (self.shape.size.x/2, self.shape.size.y/2)

class RotatingSquareClose(Transition):
    def __init__(self, speed:int=5):
        super().__init__()
        self.speed = speed
        self.shape = sf.RectangleShape()
        self.shape.position = (self.width/2, self.height/2)
        self.shape.size = (self.width, self.width)
        self.shape.origin = (self.width/2, self.width/2)
        self.shape.fill_color = sf.Color.TRANSPARENT
        self.shapes.append(self.shape)
        self.update()

    @Transition.update_handler
    def update(self):
        if self.shape.size.x == 0:
            self.end()
        elif self.shape.size.x > self.speed:
            self.shape.size -= sf.Vector2(self.speed, self.speed)
            self.shape.rotate(self.speed*2)
        else:
            self.shape.size = (0, 0)
        self.shape.origin = (self.shape.size.x/2, self.shape.size.y/2)


class PixelsIn(Transition):
    """ From black screen to transparent square by square """
    def __init__(self, speed: int, pixelsize: float):
        """ Warning : a small pixelsize and big speed will lead to severe frame drops.
            Avoid using a pixelsize smaller than 8.
        """
        super().__init__()
        self.speed = speed
        self.shapes = []
        self.remaining = []
        col_nb = math.ceil(self.render_texture.size.x/pixelsize)
        row_nb = math.ceil(self.render_texture.size.y/pixelsize)
        for x in range(col_nb):
            for y in range(row_nb):
                s = sf.RectangleShape()
                s.position = (x*pixelsize, y*pixelsize)
                s.size = (pixelsize, pixelsize)
                s.fill_color = sf.Color.BLACK
                self.shapes.append(s)
                self.remaining.append(s)
        self.update()

    @Transition.update_handler
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


class PixelsOut(Transition):
    """ From transparent screen to black screen square by square """
    def __init__(self, speed: int, pixelsize: float):
        """ Warning : a small pixelsize and big speed will lead to severe frame drops.
            Avoid using a pixelsize smaller than 8.
        """
        super().__init__()
        self.speed = speed
        self.shapes = []
        self.remaining = []
        col_nb = math.ceil(self.render_texture.size.x/pixelsize)
        row_nb = math.ceil(self.render_texture.size.y/pixelsize)
        for x in range(col_nb):
            for y in range(row_nb):
                s = sf.RectangleShape()
                s.position = (x*pixelsize, y*pixelsize)
                s.size = (pixelsize, pixelsize)
                s.fill_color = sf.Color.TRANSPARENT
                self.shapes.append(s)
                self.remaining.append(s)
        self.update()

    @Transition.update_handler
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