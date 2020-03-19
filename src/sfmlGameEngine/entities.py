from sfml import sf
from .data.game_obj import GameObject
from .data import rect, keys


class BaseEntity(GameObject, sf.Drawable):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.name = data.name
        self._state = "idle"

        self.anims = self.data.anims

        self.sprite = sf.Sprite(self.data.texture)
        self.sprite.texture_rectangle = self.anims[self.state].frames[0]
        if self.anims[self.state].frames_origin:
            self.sprite.origin = self.anims[self.state].frames_origin[0]
        self.direction = sf.Vector2(1, 1)

        self.gx = self.sprite.position.x
        self.gy = self.sprite.position.y

        self.rx = 0
        self.ry = 0

        self.collision_box = self.global_bounds
        self.collision_box_shape = sf.RectangleShape((self.collision_box.width, self.collision_box.height))
        self.collision_box_shape.position = (self.collision_box.left, self.collision_box.top)
        self.collision_box_shape.fill_color = sf.Color(200, 0, 0, 150)

        self.animate = False
        if self.anims is not None:
            self.anim_index = 0
            self.anim_clock = sf.Clock()
            self.animate = True

    @property
    def state(self):
        return  self._state

    @state.setter
    def state(self, value: str):
        if self._state != value:
            if value in self.anims:
                self._state = value
                self.anim_index = 0
                self.anim_clock.restart()
                self.sprite.texture_rectangle = self.anims[value].frames[0]
                if self.anims[value].frames_origin:
                    self.sprite.origin = self.anims[value].frames_origin[0]
                else:
                    self.sprite.origin = (0, 0)
            else:
                raise KeyError(f"Entity {self.name} has no animation state called {value}")

    @property
    def position(self):
        return sf.Vector2(self.x, self.y)

    @position.setter
    def position(self, value: tuple):
        if isinstance(value, sf.Vector2):
            self.x = value.x
            self.y = value.y
        else:
            self.x = value[0]
            self.y = value[1]

    @property
    def x(self):
        return (self.gx + self.rx) * 16

    @x.setter
    def x(self, value):
        self.gx = value // 16
        self.rx = (value - self.gx*16)/16

    @property
    def y(self):
        return (self.gy + self.ry) * 16

    @y.setter
    def y(self, value):
        self.gy = value // 16
        self.ry = (value - self.gy*16)/16

    @property
    def global_bounds(self):
        bounds = self.sprite.global_bounds
        x, y, width, height = bounds.left, bounds.top, bounds.width, bounds.height
        return rect.Rect((x, y), (width, height))

    def update(self, dt: float, keys: list = None):
        self.sprite.position = (self.x, self.y)
        self.sprite.position = (round(self.x), round(self.y))
        self.sprite.ratio = self.direction
        self.collision_box = self.global_bounds
        self.collision_box_shape.size = (self.global_bounds.width, self.global_bounds.height)
        self.collision_box_shape.position = (self.global_bounds.left, self.global_bounds.top)

        self.update_anim()

    def update_anim(self):
        ended = False
        if self.anim_clock.elapsed_time.milliseconds >= self.anims[self.state].frames_duration[self.anim_index]:
            self.anim_index += 1
            if self.anim_index >= self.anims[self.state].frames_count:
                if self.anims[self.state].loop:
                    self.anim_index = 0
                else:
                    ended = True
                    self.anim_index -= 1

            if not ended:
                self.sprite.texture_rectangle = self.anims[self.state].frames[self.anim_index]
                # adjusting sprite origin based on the new texture_rectangle
                if self.anims[self.state].frames_origin:
                    if self.anims[self.state].frames_origin[self.anim_index]:
                        self.sprite.origin = self.anims[self.state].frames_origin[self.anim_index]

            self.anim_clock.restart()

    def draw(self, target, states):
        target.draw(self.sprite, states)
        if self.game.debug:
            target.draw(self.collision_box_shape)


class PlatformerEntity(BaseEntity):
    def __init__(self, data):
        super().__init__(data)
        self.sprite.origin = (self.sprite.texture_rectangle.width / 2, self.sprite.texture_rectangle.height)
        if self.anims[self.state].frames_origin:
            if self.anims[self.state].frames_origin[0]:
                self.sprite.origin = self.anims[self.state].frames_origin[0]

        self.controls = {
            'right': keys.Keyboard.RIGHT,
            'left': keys.Keyboard.LEFT,
            'up': keys.Keyboard.UP,
            'down': keys.Keyboard.DOWN
        }

        self.velocity = sf.Vector2(0, 0)
        self.jump_velocity = sf.Vector2(0, -18)
        self.gravity = sf.Vector2(0, 1)
        self.onground = False
        self.jumping = False
        self.jump_count = 2
        self.remaining_jumps = 2
        self.falling = True

    def jump(self):
        col_over = []
        if self.onground:
            # these 2 lines get the nearest collision box over the entity
            self.game.level.collisions.sort(key=lambda b:abs(b.bottom-self.collision_box.top))
            col_over = [x for x in self.game.level.collisions if x.bottom < self.collision_box.top and x.left <= self.x <= x.right]

        if not col_over or (col_over and self.collision_box.top // 16 != col_over[0].bottom // 16):
            self.jumping = True
            self.onground = False
            self.velocity.y = self.jump_velocity.y
            self.remaining_jumps -= 1

    def land(self):
        self.jumping = False
        self.onground = True
        self.falling = False
        self.remaining_jumps = self.jump_count

    def idle(self):
        if -0.05 < self.velocity.x < 0.05:
            self.velocity.x = 0
        else:
            if self.onground:
                self.velocity.x = self.velocity.x * 0.80
            else:
                if self.velocity.x < 0:
                    self.velocity.x += 0.3
                else:
                    self.velocity.x -= 0.3
        self.state = "idle"

    def walk_right(self):
        self.velocity.x = min(self.velocity.x + 0.5, 12)
        self.direction.x = 1
        self.state = "walk"

    def walk_left(self):
        self.velocity.x = max(self.velocity.x - 0.5, -12)
        self.direction.x = -1
        self.state = "walk"

    def update(self, dt: float, keys: list = None):
        if not self.onground:
            self.velocity += self.gravity
        if self.velocity.y > 0 and not self.onground:
            self.falling = True
        else:
            self.falling = False
        self.rx += self.velocity.x * dt

        for box in self.game.level.collisions:
            if box.top <= self.collision_box.top < box.bottom or box.top < self.collision_box.bottom <= box.bottom \
                    or self.collision_box.top <= box.top < self.collision_box.bottom or self.collision_box.top < box.bottom <= self.collision_box.bottom:
                # left collision
                if self.velocity.x < 0:
                    if self.collision_box.left//16 == (box.right -1) // 16 and self.rx < 0.3:
                        self.rx -= self.velocity.x*dt
                        self.velocity.x = 0
                # rigth collision
                if self.velocity.x > 0:
                    if self.collision_box.right//16 == box.left // 16 and self.rx > 0.7:
                        self.rx -= self.velocity.x*dt
                        self.velocity.x = 0

        while self.rx > 1: self.rx -= 1; self.gx += 1
        while self.rx < 0: self.rx += 1; self.gx -= 1

        self.ry += self.velocity.y * dt
        for box in self.game.level.collisions:
            if box.left / 16 <= self.gx < (box.right) / 16:
                # top collision
                if self.velocity.y < 0:
                    if self.collision_box.top//16 == (box.bottom - 1) // 16 and self.ry < 0.99:
                        self.y = box.bottom + self.sprite.origin.y
                        self.falling = True
                        self.velocity.y = 0
                # bottom collision
                if self.gy + 1 == box.top / 16 and self.ry >= 0.99:
                    self.ry = 0.99
                    self.velocity.y = 0
                    self.land()
                    break
            else:
                self.onground = False

        while self.ry > 1: self.ry -= 1; self.gy += 1
        while self.ry < 0: self.ry += 1; self.gy -= 1

        super().update(dt)