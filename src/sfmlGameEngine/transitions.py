from sfml import sf


class Transition(sf.Drawable):
    def __init__(self, width, height):
        super().__init__()
        self.render_texture = sf.RenderTexture(width, height)
        self.sprite = sf.Sprite(self.render_texture.texture)
        self.ended = False
        self.started = False

    def start(self):
        self.started = True
        self.on_start()

    def on_start(self):
        pass

    def end(self):
        self.ended = True
        self.on_end()

    def on_end(self):
        pass

    def update(self):
        pass

    def draw(self, target, transformations):
        target.draw(self.sprite)


class FadeIn(Transition):
    """ Transition from black screen to transparent"""
    def __init__(self, width, height, speed=5):
        super().__init__(width, height)
        self.opacity = 255
        self.speed = speed
        self.render_texture.clear(sf.Color(0, 0, 0, self.opacity))
        self.render_texture.display()
        self.sprite.texture = self.render_texture.texture

    def update(self):
        if self.started and not self.ended:
            self.render_texture.clear(sf.Color(0, 0, 0, self.opacity))
            self.render_texture.display()
            self.sprite.texture = self.render_texture.texture

            self.opacity -= self.speed
            if self.opacity <= 0:
                self.opacity = 0
                self.end()


class FadeOut(Transition):
    """ Transition from transparent to black screen"""
    def __init__(self, width, height, speed=5):
        super().__init__(width, height)
        self.opacity = 0
        self.speed = speed
        self.render_texture.clear(sf.Color(0, 0, 0, self.opacity))
        self.render_texture.display()
        self.sprite.texture = self.render_texture.texture

    def update(self):
        if self.started and not self.ended:
            self.render_texture.clear(sf.Color(0, 0, 0, self.opacity))
            self.render_texture.display()
            self.sprite.texture = self.render_texture.texture

            self.opacity += self.speed
            if self.opacity >= 255:
                self.opacity = 255
                self.end()
