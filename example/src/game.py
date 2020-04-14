from sfml import sf
import src.NasNas as ns

from example.src.fonts import bitmap_font
from example.src import entities
from example.src import menus


class MyGame(ns.App):
    def __init__(self):
        super().__init__("NasNas - Example Game", 960, 576, 320, 192, 60)

        self.window.key_repeat_enabled = False
        self.window.vertical_synchronization = True

        # defining window on_close callback
        @self.window.on_close
        def closing_window():
            # when window.close() is called, this message will be printed
            print("Window will close now !")

        # loading level and setting the collisions
        self.level = ns.Res.Maps.level
        self.level.set_collisions_objectgroup("collisions")

        tileset = [t for t in self.level.tilesets if t.name == "Assets"][0]
        self.coins = []
        # Creating coin sprite from tileset properties
        # 15 is the tile ID of the coin on the tileset
        coin_anim = ns.Anim([])
        for frame in tileset.animations[15]:
            coin_anim.add(ns.AnimFrame(
                ns.Rect(tileset.get_tile_tex_coord(frame['id']), (tileset.tile_width, tileset.tile_height)),
                frame['duration'])
            )
        coin_spr = ns.Sprite(name="coin", texture=ns.Res.tilesets.Assets, anims={"idle": coin_anim})

        for point in self.level.objectgroups['coins'].points:
            new_coin = ns.BaseEntity("coin", coin_spr)
            new_coin.position = point
            self.coins.append(new_coin)

        # recreating the scene, same size as the level
        self.scene = self.create_scene(self.level.width * 16, self.level.height * 16)

        # creating the players
        self.player1 = entities.Player("Player 1")
        self.player1.controls = {'right': ns.Keyboard.D, 'left': ns.Keyboard.Q, 'up': ns.Keyboard.Z, 'down': ns.Keyboard.S}
        self.player1.position = (2 * 16, 8 * 16)

        self.player2 = entities.Player("Player 2")
        self.player2.controls = {'right': ns.Keyboard.RIGHT, 'left': ns.Keyboard.LEFT, 'up': ns.Keyboard.UP, 'down': ns.Keyboard.DOWN}
        self.player2.position = (25 * 16, 8 * 16)

        # creating a camera for each player, the two cameras look at the same scene
        self.game_camera.reset((0, 0), (self.V_WIDTH / 2, self.V_HEIGHT))
        self.game_camera.reset_viewport((0, 0), (0.5, 1))
        self.game_camera.follow(self.player1)

        self.game_camera2 = self.create_camera("player2", 0, ns.Rect((0, 0), (self.V_WIDTH / 2, self.V_HEIGHT)), ns.Rect((0.5, 0), (0.5, 1)))
        self.game_camera2.follow(self.player2)

        # writing texts using the bitmap font
        self.text_bitmap = ns.BitmapText("PRESS L TO DISPLAY MASK", bitmap_font)
        self.text_bitmap.position = sf.Vector2(2 * 16, 7 * 16) + sf.Vector2(0, -28)
        self.text_bitmap2 = ns.BitmapText("PRESS G TO SWITCH DEBUG MODE", bitmap_font)
        self.text_bitmap2.position = sf.Vector2(2 * 16, 7 * 16) + sf.Vector2(0, -6)
        self.text_bitmap3 = ns.BitmapText("PRESS M TO QUAKE CAMERA", bitmap_font)
        self.text_bitmap3.position = sf.Vector2(2 * 16, 7 * 16) + sf.Vector2(0, -18)
        self.text_bitmap4 = ns.BitmapText("PRESS F TO ENTER OR EXIT FULLSCREEN", bitmap_font)
        self.text_bitmap4.position = sf.Vector2(2 * 16, 7 * 16) + sf.Vector2(0, -60)

        # creating the layers
        map_back_layer = ns.Layer("map_back", self.level.layers["back"])
        map_front_layer = ns.Layer("map_front", self.level.layers["front"])
        texts_layers = ns.Layer("texts", self.text_bitmap, self.text_bitmap2, self.text_bitmap3, self.text_bitmap4)
        self.entities_layer = ns.Layer("entities", self.player1, self.player2, *self.coins)
        self.map_collisions_layer = ns.Layer("map_collisions", self.level.objectgroups["collisions"], self.level.objectgroups["coins"], self.level.objectgroups["path"])

        # creating a mask layer and adding drawables to it
        self.mask = ns.Mask("light", self.level.width * 16, self.level.height * 16, sf.Color(20, 10, 50, 240))

        self.p1_light = entities.Light(self.player1.position, self.mask.fill_color)
        self.p2_light = entities.Light(self.player2.position, self.mask.fill_color)

        self.mask.add(self.p1_light)
        self.mask.add(self.p2_light)

        # adding the created layer to the scene
        self.scene.add_layer(self.entities_layer, 4)
        self.scene.add_layer(texts_layers, 2)
        self.scene.add_layer(map_front_layer, 1)
        self.scene.add_layer(map_back_layer, 0)

        # creating HUD scene and camera
        self.HUD_scene = self.create_scene(self.window.ui_view.size.x, self.window.ui_view.size.y)
        self.HUD_camera = self.create_camera("HUD_camera", 5, ns.Rect((0, 0), self.window.ui_view.size))

        # players scores text
        self.p1_score_text = sf.Text(str(self.player1.score))
        self.p1_score_text.font = ns.Res.arial
        self.p1_score_text.character_size = 16
        self.p2_score_text = sf.Text(str(self.player2.score))
        self.p2_score_text.font = ns.Res.arial
        self.p2_score_text.character_size = 16
        self.p2_score_text.position = sf.Vector2(self.window.ui_view.size.x - self.window.ui_view.size.x/2, 0)

        # adding the text to HUD_scene
        self.HUD_scene.add_layer(ns.Layer("scores", self.p1_score_text, self.p2_score_text), 0)

        # creating the menus
        self.main_menu = menus.MainMenu()
        self.main_menu.open()
        self.game_menu = ns.ui.VerticalMenu("game_menu", menus.menu_style, menus.resume_btn, menus.quit_btn)
        self.game_menu.center = self.window.ui_view.center

        # creating the opening transition and starting it
        self.window_open_transition = ns.FadeInTransition(speed=4)
        self.window_open_transition.start()

        self.menu_exit_transition = ns.FadeOutTransition(speed=4)

        @self.menu_exit_transition.on_end
        def menu_exit_on_end():
            self.main_menu.close()
            self.game_camera.scene = self.scene
            self.game_camera2.scene = self.scene
            self.HUD_camera.scene = self.HUD_scene
            self.game_start_transition.start()

        self.game_start_transition = ns.RotatingSquareOpenTransition(speed=5)

        # creating the closing transition
        self.quit_transition = ns.RotatingSquareCloseTransition(speed=5)

        # defining on_end callback of the closing transition
        @self.quit_transition.on_end
        def quit_transition_ending():
            # when the transition ends, the window will close
            self.window.close()

        # adding some debug texts, can be seen on screen when debug mode is active
        self.add_debug_text(self.player1, "onground", (0, 0))
        self.add_debug_text(self, "transitions", (150, 0))
        self.add_debug_text(self, "inputs", (0, 16))
        self.add_debug_text(self.player1, "velocity", (0, 32))
        self.add_debug_text(self.player1, "jumping", (150, 32))
        self.add_debug_text(self.player1, "falling", (300, 32))

    def event_handler(self, event):
        if event == sf.Event.CLOSED:
            self.window.close()

        elif event == sf.Event.KEY_RELEASED:
            if event["code"] == sf.Keyboard.ESCAPE:     # closing the game
                self.game_menu.open()

        elif event == sf.Event.KEY_PRESSED:
            if event["code"] == ns.Keyboard.R:        # restarting the game
                self.window.close()
                self.__init__()
                self.run()

            elif event["code"] == ns.Keyboard.F:        # fullscreen mode
                self.toggle_fullscreen()

            elif event["code"] == ns.Keyboard.G:        # debug mode
                if self.debug:
                    self.scene.remove_layer(layer=self.scene.get_layer("map_collisions"))
                else:
                    self.scene.add_layer(self.map_collisions_layer, 9)
                self.debug = not self.debug

            elif event["code"] == ns.Keyboard.M:        # camera quake
                self.game_camera.quake(duration=5, amplitude=2)
                self.game_camera2.quake(5, 2)

            elif event["code"] == ns.Keyboard.L:        # show mask layer
                if self.scene.masks:
                    self.scene.remove_mask(self.mask)
                else:
                    self.scene.add_mask(self.mask, 10)

    def update(self):
        # updating the TiledMap
        self.level.update()

        # updating entities
        for layer in self.scene.layers.values():
            for drawable in layer:
                if isinstance(drawable, ns.BaseEntity):
                    drawable.update(self.dt, self.inputs)
            layer.ysort()

        # updating score texts
        self.p1_score_text.string = str(self.player1.score)
        self.p2_score_text.string = str(self.player2.score)

        # updating lights
        self.p1_light.update()
        self.p1_light.position = self.player1.position - sf.Vector2(0, 5)
        self.p2_light.update()
        self.p2_light.position = self.player2.position - sf.Vector2(0, 5)
