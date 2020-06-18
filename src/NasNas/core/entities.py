from typing import Dict

from sfml import sf

from ..data.game_obj import GameObject
from ..data import rect, keys
from .sprites import Anim, AnimPlayer


class BaseEntity(GameObject, sf.Drawable):
    def __init__(self, name: str, data, gridsize : int = 16):
        super().__init__()
        self.data = data
        self.name = name
        self._anim_state = "idle"

        self.anims: Dict[str, Anim] = self.data.anims
        self.anim_player: AnimPlayer = AnimPlayer(self.anims[self._anim_state])
        self.animate = False if self.anims is None else True

        self.sprite = sf.Sprite(self.data.texture)
        self.sprite.texture_rectangle = self.anims[self.anim_state].frames[0].rectangle
        self.sprite.origin = self.anims[self.anim_state].frames[0].origin
        self.direction = sf.Vector2(1, 1)

        self.gx = self.sprite.position.x
        self.gy = self.sprite.position.y

        self.rx = 0
        self.ry = 0

        self.collision_box = self.global_bounds
        self.collision_box_shape = sf.RectangleShape((self.collision_box.width, self.collision_box.height))
        self.collision_box_shape.position = (self.collision_box.left, self.collision_box.top)
        self.collision_box_shape.fill_color = sf.Color(200, 0, 0, 150)

        self.gridsize = gridsize
            
    @property
    def anim_state(self):
        return self._anim_state

    @anim_state.setter
    def anim_state(self, value: str):
        if self._anim_state != value:
            if value in self.anims:
                self._anim_state = value
                self.anim_player.play(self.anims[self._anim_state])
                self.sprite.texture_rectangle = self.anim_player.active_frame.rectangle
                self.sprite.origin = self.anim_player.active_frame.origin
            else:
                raise KeyError(f"Entity named {self.name} has no animation anim_state named {value}")

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
        return (self.gx + self.rx) * self.gridsize

    @x.setter
    def x(self, value):
        self.gx = value // self.gridsize
        self.rx = (value - self.gx*self.gridsize)/self.gridsize

    @property
    def y(self):
        return (self.gy + self.ry) * self.gridsize

    @y.setter
    def y(self, value):
        self.gy = value // self.gridsize
        self.ry = (value - self.gy*self.gridsize)/self.gridsize

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
        self.anim_player.update()
        if self.sprite.texture_rectangle != self.anim_player.active_frame.rectangle:
            self.sprite.texture_rectangle = self.anim_player.active_frame.rectangle
            self.sprite.origin = self.anim_player.active_frame.origin

    def draw(self, target, anim_states):
        target.draw(self.sprite, anim_states)
        if self.game.debug:
            target.draw(self.collision_box_shape)


class PlatformerEntity(BaseEntity):
    def __init__(self, name: str, data):
        super().__init__(name, data)
        self.sprite.origin = self.anims[self.anim_state].frames[0].origin

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

        if not col_over or (col_over and self.collision_box.top // self.gridsize != col_over[0].bottom // self.gridsize):
            self.jumping = True
            self.onground = False
            self.velocity.y = self.jump_velocity.y
            self.remaining_jumps -= 1

    def land(self):
        if not self.onground:
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
        self.anim_state = "idle"

    def walk_right(self):
        self.velocity.x = min(self.velocity.x + 0.5, 12)
        self.direction.x = 1
        self.anim_state = "walk"

    def walk_left(self):
        self.velocity.x = max(self.velocity.x - 0.5, -12)
        self.direction.x = -1
        self.anim_state = "walk"

    def update(self, dt: float, keys: list = None):
        if not self.onground:
            self.velocity += self.gravity
        if self.velocity.y > 0 and not self.onground:
            self.falling = True
        else:
            self.falling = False
        self.rx += self.velocity.x * dt

        if self.game.level:
            for box in self.game.level.collisions:
                if box.top <= self.collision_box.top < box.bottom or box.top < self.collision_box.bottom <= box.bottom \
                        or self.collision_box.top <= box.top < self.collision_box.bottom or self.collision_box.top < box.bottom <= self.collision_box.bottom:
                    # left collision
                    if self.velocity.x < 0:
                        if self.collision_box.left//self.gridsize == (box.right -1) // self.gridsize and self.rx < 0.3:
                            self.rx -= self.velocity.x*dt
                            self.velocity.x = 0
                    # rigth collision
                    if self.velocity.x > 0:
                        if self.collision_box.right//self.gridsize == box.left // self.gridsize and self.rx > 0.7:
                            self.rx -= self.velocity.x*dt
                            self.velocity.x = 0

        while self.rx > 1: self.rx -= 1; self.gx += 1
        while self.rx < 0: self.rx += 1; self.gx -= 1

        self.ry += self.velocity.y * dt
        bot_collision = False

        if self.game.level:
            for box in self.game.level.collisions:
                if box.left / self.gridsize <= self.gx < (box.right) / self.gridsize:
                    # top collision
                    if self.velocity.y < 0:
                        if self.collision_box.top//self.gridsize == (box.bottom - 1) // self.gridsize and self.ry < 0.99:
                            self.y = box.bottom + self.sprite.origin.y
                            self.falling = True
                            self.velocity.y = 0
                    # bottom collision
                    if self.gy + 1 == box.top / self.gridsize and self.ry >= 0.99:
                        self.ry = 0.99
                        self.velocity.y = 0
                        self.land()
                        bot_collision = True
                        break

        if not bot_collision:
            self.onground = False
        while self.ry > 1: self.ry -= 1; self.gy += 1
        while self.ry < 0: self.ry += 1; self.gy -= 1

        super().update(dt)