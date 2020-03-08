from sfml import sf
import src.sfmlGameEngine as ge

# always call this static method before you do anything if you want to use the resource manage Res
ge.GameEngine.load_resources(True)

from example.src import entities


class MyGame(ge.GameEngine):
    def __init__(self):
        super().__init__("pySFML Game Engine - Example Game", 960, 576, 320, 192, 60)
        ge.game.debug.Logger.log()
        self.window.key_repeat_enabled = False
        self.window.vertical_synchronization = True
        self.window.framerate_limit = 60

        self.level = ge.Res.maps.level

        self.scene = self.create_scene(self.level.width * 16, self.level.height * 16)

        self.player = entities.Player()
        self.player.position = (2*16, 7*16)
        bitmap_font = ge.BitmapFont(ge.Res.textures.font, (8, 8), spacings_map={"O": 8})
        self.text_bitmap = ge.BitmapText("PRESS L TO DISPLAY MASK", bitmap_font)
        self.text_bitmap.position = self.player.position+sf.Vector2(0, -28)
        self.text_bitmap2 = ge.BitmapText("PRESS D TO SWITCH DEBUG MODE", bitmap_font)
        self.text_bitmap2.position = self.player.position+sf.Vector2(0, -6)
        self.text_bitmap3 = ge.BitmapText("PRESS M TO TOGGLE MINIMAP", bitmap_font)
        self.text_bitmap3.position = self.player.position + sf.Vector2(0, -18)
        self.text_bitmap4 = ge.BitmapText("PRESS F TO ENTER OR EXIT FULLSCREEN", bitmap_font)
        self.text_bitmap4.position = self.player.position + sf.Vector2(0, -60)
        self.light_growing = True

        self.game_camera.follow(self.player)
        self.game_camera.scene = self.scene

        self.minimap_camera.follow(self.player)
        self.minimap_camera.scene = self.scene

        map_back_layer = ge.Layer("map_back", self.level.layers["back"])
        map_front_layer = ge.Layer("map_front", self.level.layers["front"])
        self.map_collisions_layer = ge.Layer("map_collisions", self.level.layers["collisions"])
        entities_layer = ge.Layer("entities", self.player, self.text_bitmap, self.text_bitmap2, self.text_bitmap3, self.text_bitmap4)

        self.mask = ge.Mask("light", self.level.width * 16, self.level.height * 16, sf.Color(20, 10, 50, 255))
        self.player_light = sf.CircleShape(33)
        self.player_light.fill_color = sf.Color(self.mask.fill_color.r, self.mask.fill_color.g, self.mask.fill_color.b, 50)
        self.player_light.position = self.player.position - sf.Vector2(0, 5)
        self.player_light2 = sf.CircleShape(50)
        self.player_light2.fill_color = sf.Color(self.mask.fill_color.r, self.mask.fill_color.g, self.mask.fill_color.b, 150)
        self.player_light2.origin = (50, 60)
        self.player_light2.position = self.player.position - sf.Vector2(0, 5)

        self.mask.add(self.player_light2)
        self.mask.add(self.player_light)

        self.scene.add_layer(entities_layer, 3)
        self.scene.add_layer(map_front_layer, 1)
        self.scene.add_layer(map_back_layer, 0)

        self.ui_scene = self.create_scene(self.window.size.x, self.window.size.y)
        minimap_bg = sf.RectangleShape()
        minimap_bg.size = (0.2*self.window.size.x, 0.2*self.window.size.y)
        minimap_bg.position = (0.8*self.window.size.x, 0)
        minimap_bg.fill_color = sf.Color.BLACK
        self.ui_scene.add_layer(ge.Layer("ui", minimap_bg), 10)
        self.ui_camera.scene = self.ui_scene

        self.debug = False
        self.add_debug_text(self.player, "onground", (0, 0))
        self.add_debug_text(self.player, "remaining_jumps", (150, 0))
        self.add_debug_text(self, "inputs", (0, 16))
        self.add_debug_text(self.player, "velocity", (0, 32))

    def event_handler(self, event):
        if event == sf.Event.KEY_PRESSED:
            if event["code"] == sf.Keyboard.ESCAPE:
                self.window.close()
            elif event["code"] == ge.Keyboard.R:
                self.window.close()
                self.__init__()
                self.run()
            elif event["code"] == ge.Keyboard.F:
                if not self.fullscreen:
                    self.enter_fullscreen()
                else:
                    self.quit_fullscreen()
            elif event["code"] == ge.Keyboard.D:
                if self.debug:
                    self.scene.remove_layer(layer=self.scene.get_layer("map_collisions"))
                else:
                    self.scene.add_layer(self.map_collisions_layer, 2)
                self.debug = not self.debug
            elif event["code"] == ge.Keyboard.M:
                self.minimap_camera.visible = not self.minimap_camera.visible
            elif event["code"] == ge.Keyboard.L:
                if self.scene.masks:
                    self.scene.remove_mask(self.mask)
                else:
                    self.scene.add_mask(self.mask)

    def update(self):
        super().update()
        self.level.layers["front"].update()

        for layer in self.scene.layers.values():
            for ent in layer:
                layer.ysort()
                if isinstance(ent, ge.entities.BaseEntity):
                    ent.update(self.dt, self.inputs)

        if self.player_light.radius < 33 and self.light_growing:
            self.player_light.radius += 0.015
            self.player_light2.radius += 0.05
            self.player_light.origin = (self.player_light.radius, self.player_light.radius+10)
            self.player_light2.origin = (self.player_light2.radius, self.player_light2.radius+10)
        else:
            self.light_growing = False

        if not self.light_growing and self.player_light.radius > 30:
            self.player_light.radius -= 0.015
            self.player_light2.radius -= 0.05
            self.player_light.origin = (self.player_light.radius, self.player_light.radius+10)
            self.player_light2.origin = (self.player_light2.radius, self.player_light2.radius+10)
        else:
            self.light_growing = True
        self.player_light.position = self.player.position - sf.Vector2(0, 5)
        self.player_light2.position = self.player.position - sf.Vector2(0, 5)


