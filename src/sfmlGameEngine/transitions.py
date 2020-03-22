from sfml import sf
from .data.game_obj import GameObject
import math


class Transition(GameObject, sf.Drawable):
    def __init__(self, width, height):
        super().__init__()
        self.render_texture = sf.RenderTexture(width, height)
        self.r = self.g = self.b = 0
        self.a = 255
        self.blend_mode = sf.BLEND_NONE
        self.shapes = []
        self.sprite = sf.Sprite(self.render_texture.texture)
        self.ended = False
        self.started = False

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
    """ Transition from black screen to transparent"""
    def __init__(self, width, height, speed=5):
        super().__init__(width, height)
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
    """ Transition from transparent to black screen"""
    def __init__(self, width, height, speed=5):
        super().__init__(width, height)
        self.a = 0
        self.speed = speed
        self.update()

    @Transition.update_handler
    def update(self):
        self.a += self.speed
        if self.a >= 255:
            self.a = 255
            self.end()


class CircleClose(Transition):
    def __init__(self, width, height, speed=5):
        super().__init__(width, height)
        self.speed = speed
        self.shape = sf.CircleShape(width+height/2)
        self.shape.origin = (self.shape.radius, self.shape.radius)
        self.shape.position = (width/2, height/2)
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


class CircleOpen(Transition):
    def __init__(self, width, height, speed=5):
        super().__init__(width, height)
        self.speed = speed
        self.limit = math.sqrt(width**2+height**2)/2
        self.shape = sf.CircleShape(0.1)
        self.shape.origin = (0.1, 0.1)
        self.shape.position = (width/2, height/2)
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
