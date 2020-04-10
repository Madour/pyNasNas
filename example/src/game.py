from sfml import sf
import src.NasNas as ns

from example.src import entities


class MyGame(ns.App):
    def __init__(self):
        super().__init__("pySFML Game Engine - Example Game", 960, 576, 320, 192, 60)

        self.window.key_repeat_enabled = False
        self.window.vertical_synchronization = True

        self.level = ns.Res.Maps.level

        self.level.set_collisions_objectgroup("collisions")

        self.scene = self.create_scene(self.level.width * 16, self.level.height * 16)

        self.player = entities.Player()
        self.player.controls = {'right': ns.Keyboard.RIGHT, 'left': ns.Keyboard.LEFT, 'up': ns.Keyboard.UP, 'down': ns.Keyboard.DOWN}
        self.player.position = (2*16, 7*16)

        self.player2 = entities.Player()
        self.player2.controls = {'right': ns.Keyboard.D, 'left': ns.Keyboard.Q, 'up': ns.Keyboard.Z, 'down': ns.Keyboard.S}
        self.player2.position = (25 * 16, 7 * 16)

        bitmap_font = ns.BitmapFont(ns.Res.Textures.font, (8, 8), spacings_map={"O": 8})
        self.text_bitmap = ns.BitmapText("PRESS L TO DISPLAY MASK", bitmap_font)
        self.text_bitmap.position = self.player.position+sf.Vector2(0, -28)
        self.text_bitmap2 = ns.BitmapText("PRESS D TO SWITCH DEBUG MODE", bitmap_font)
        self.text_bitmap2.position = self.player.position+sf.Vector2(0, -6)
        self.text_bitmap3 = ns.BitmapText("PRESS M TO TOGGLE MINIMAP", bitmap_font)
        self.text_bitmap3.position = self.player.position + sf.Vector2(0, -18)
        self.text_bitmap4 = ns.BitmapText("PRESS F TO ENTER OR EXIT FULLSCREEN", bitmap_font)
        self.text_bitmap4.position = self.player.position + sf.Vector2(0, -60)

        self.game_camera.reset((0, 0), (self.V_WIDTH/2, self.V_HEIGHT))
        self.game_camera.reset_viewport((0, 0), (0.5, 1))
        self.game_camera.follow(self.player2)
        self.game_camera.scene = self.scene

        self.game_camera2 = self.create_camera("player2", 0, ns.Rect((0, 0), (self.V_WIDTH/2, self.V_HEIGHT)), ns.Rect((0.5, 0), (0.5, 1)))
        self.game_camera2.follow(self.player)
        self.game_camera2.scene = self.scene

        map_back_layer = ns.Layer("map_back", self.level.layers["back"])
        map_front_layer = ns.Layer("map_front", self.level.layers["front"])
        map_coins_layer = ns.Layer("map_coins", self.level.layers["coins"])
        self.map_collisions_layer = ns.Layer("map_collisions", self.level.objectgroups["collisions"], self.level.objectgroups["coins"])
        texts_layers = ns.Layer("texts", self.text_bitmap, self.text_bitmap2, self.text_bitmap3, self.text_bitmap4)
        entities_layer = ns.Layer("entities", self.player, self.player2)

        self.mask = ns.Mask("light", self.level.width * 16, self.level.height * 16, sf.Color(20, 10, 50, 220))
        self.light_growing = True
        self.player_light = sf.CircleShape(33)
        self.player_light.fill_color = sf.Color(self.mask.fill_color.r, self.mask.fill_color.g, self.mask.fill_color.b, 50)
        self.player_light.position = self.player.position - sf.Vector2(0, 5)
        self.player_light2 = sf.CircleShape(50)
        self.player_light2.fill_color = sf.Color(self.mask.fill_color.r, self.mask.fill_color.g, self.mask.fill_color.b, 150)
        self.player_light2.position = self.player.position - sf.Vector2(0, 5)

        self.mask.add(self.player_light2)
        self.mask.add(self.player_light)

        self.scene.add_layer(entities_layer, 4)
        #self.scene.add_layer(map_coins_layer, 3)
        self.scene.add_layer(texts_layers, 2)
        self.scene.add_layer(map_front_layer, 1)
        self.scene.add_layer(map_back_layer, 0)

        self.tr_in = ns.transitions.CircleOpen(speed=8)
        self.tr_in.start()

        self.tr_out = ns.transitions.RotatingSquareClose(speed=5)

        @self.tr_out.on_start
        def tr_out_starting():
            self.window.capture().to_file("screen.png")

        @self.tr_out.on_end
        def tr_out_ending():
            self.window.close()

        self.debug = False
        self.add_debug_text(self.player, "onground", (0, 0))
        self.add_debug_text(self, "transitions", (150, 0))
        self.add_debug_text(self, "inputs", (0, 16))
        self.add_debug_text(self.player, "velocity", (0, 32))
        self.add_debug_text(self.player, "jumping", (150, 32))
        self.add_debug_text(self.player, "falling", (300, 32))

        @self.window.on_close
        def closing_window():
            print("Window will close now !")

    def event_handler(self, event):
        if event == sf.Event.KEY_PRESSED:
            if event["code"] == sf.Keyboard.ESCAPE:
                self.tr_out.start()
            elif event["code"] == ns.Keyboard.R:
                self.window.close()
                self.__init__()
                self.run()
            elif event["code"] == ns.Keyboard.F:
                self.toggle_fullscreen()
            elif event["code"] == ns.Keyboard.G:
                if self.debug:
                    self.scene.remove_layer(layer=self.scene.get_layer("map_collisions"))
                else:
                    self.scene.add_layer(self.map_collisions_layer, 9)
                self.debug = not self.debug
            elif event["code"] == ns.Keyboard.M:
                self.game_camera.quake(duration=5, amplitude=2)
                self.game_camera2.quake(5, 2)
            elif event["code"] == ns.Keyboard.L:
                if self.scene.masks:
                    self.scene.remove_mask(self.mask)
                else:
                    self.scene.add_mask(self.mask, 10)

    def update(self):
        self.level.update()

        for layer in self.scene.layers.values():
            for ent in layer:
                if isinstance(ent, ns.entities.BaseEntity):
                    ent.update(self.dt, self.inputs)
            layer.ysort()

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
