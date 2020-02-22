from sfml import sf
from os.path import join
from .data.game_obj import GameObject
from .data import const
from .reslib.resource_path import resource_path, RES_DIR
from .reslib import Res

from . import camera
from . import layers
from . import scene
from . import debug


class GameEngine:
    W_WIDTH = 160*6     # window width
    W_HEIGHT = 90*6     # window height
    V_WIDTH = 160*2     # view width
    V_HEIGHT = 90*2     # view height

    def __init__(self, title: str = None, w_width: int = 960, w_height: int = 540,
                 v_width: int = 320, v_height: int = 180, desired_fps: int = 60):
        GameObject.game = self

        # Game name, displayed in window title
        if not title:
            self.name = "pySFML Game Engine"
        else:
            self.name = title

        self.desired_fps = desired_fps
        self.window = sf.RenderWindow(sf.VideoMode(w_width, w_height), self.name)
        self.window.framerate_limit = self.desired_fps
        self.fullscreen = False

        # inputs from keyboard are stored in this list
        self.inputs = []

        # Scene is where everything is drawn on
        self.create_scene(w_width, w_height)

        # a view used to keep aspect ratio of the game when the window is resized
        self.screen_view = camera.Camera()
        self.screen_view.reset((0, 0), (v_width, v_height))

        self.show_minimap = True
        self.minimap = camera.Camera()
        self.minimap.reset((0, 0), (v_width*3, v_height*3))
        self.minimap.viewport = sf.Rect((0.8, 0), (0.2, 0.2))
        self.minimap.frames_delay = 0

        # clock and dt used for FPS calculation
        self.clock = sf.Clock()
        self.dt = 0

        self.debug = False
        self.debug_texts = [] #: list of DebugText

        self.scale_view()

    @staticmethod
    def load_resources(loading_image=None):
        """Static method that load all resources

        Initialize Res and load all resources in RES_DIR
        """
        if loading_image:
            import time
            window = sf.RenderWindow(sf.VideoMode(160, 90), "Game Base", sf.Style.NONE)
            l = sf.Sprite(sf.Texture.from_file(resource_path(join(RES_DIR, "loading.png"))))
            window.draw(l)
            window.display()
            Res.load()
            window.close()
        else:
            Res.load()

    def create_scene(self, width: int, height: int):
        self.scene = scene.Scene(width, height)

    def add_debug_text(self, instance:object, attr_name: str, position: tuple, float_round: int = None):
        """
        Adds a DebugText to self.debug_texts. The text will be drawn at the given position
        instance         : Any object instance
        attr_name :str   : Attribute of the given object you want to draw its value
        position : tuple : The position where the text will be drawn
        """
        if float_round:
            self.debug_texts.append(debug.DebugText(instance, attr_name, position, float_round))
        else:
            self.debug_texts.append(debug.DebugText(instance, attr_name, position))


    def enter_fullscreen(self):
        self.window.close()
        self.window = sf.RenderWindow(sf.VideoMode(const.SCREEN_W, const.SCREEN_H), self.name, sf.Style.NONE)
        self.window.framerate_limit = self.desired_fps
        self.window.mouse_cursor_visible = False
        self.window.vertical_synchronization = True
        self.fullscreen = True
        self.scale_view()

    def quit_fullscreen(self):
        self.window.close()
        self.window = sf.RenderWindow(sf.VideoMode(self.W_WIDTH, self.W_HEIGHT), self.name, sf.Style.DEFAULT)
        self.window.framerate_limit = self.desired_fps
        self.window.mouse_cursor_visible = True
        self.window.vertical_synchronization = True
        self.fullscreen = False
        self.scale_view()

    def scale_view(self):
        """
        Scales self.screen_view to keep aspect ratio of the game when the window is resized
        """
        # larger than usual window
        if float(self.window.size.x) / float(self.window.size.y) > self.W_WIDTH / self.W_HEIGHT:
            viewport_h = 1
            viewport_w = (float(self.window.size.y) * (self.W_WIDTH / self.W_HEIGHT)) / float(self.window.size.x)
            viewport_y = 0
            viewport_x = (1-viewport_w)/2
        # higher than usual window
        else:
            viewport_w = 1
            viewport_h = (float(self.window.size.x) / (self.W_WIDTH / self.W_HEIGHT)) / float(self.window.size.y)
            viewport_x = 0
            viewport_y = (1-viewport_h)/2
        if self.screen_view:
            self.screen_view.viewport = sf.Rect((viewport_x, viewport_y), (viewport_w, viewport_h))

    def _key_handler(self, key: int, event_type: str):
        if key not in self.inputs and event_type == "pressed":
            self.inputs.insert(0, key)
        else:
            if key in self.inputs and event_type == "released":
                self.inputs.remove(key)

    def _store_inputs(self, event: sf.Event):
        """
        Add all key pressed to self.inputs
        Calls self.scale_view() when the window is resized
        """
        if event == sf.Event.CLOSED:
            self.window.close()
        elif event == sf.Event.KEY_PRESSED:
            self._key_handler(event["code"], "pressed")
        elif event == sf.Event.KEY_RELEASED:
            self._key_handler(event["code"], "released")
        elif event == sf.Event.RESIZED:
            self.scale_view()

    def event_handler(self, event: sf.Event):
        pass

    def update(self):
        pass

    def render(self):
        """
        Draw all Layers in order.
        Layer 0 will be drawn first, layer 1 will be drawn over layer 0 etc
        Internal use only, do not override this method.
        """
        self.scene.update()

        self.window.view = self.screen_view
        self.window.draw(self.scene)

        if self.show_minimap:
            self.window.view = self.minimap
            self.window.draw(self.scene)

    def run(self):
        while self.window.is_open:
            self.dt = self.clock.restart().seconds
            self.window.title = self.name+" - FPS:" + str(round(1 / self.dt))

            for event in self.window.events:
                self._store_inputs(event)
                self.event_handler(event)

            self.update()

            # if (1/self.dt) <= self.desired_fps/2:
            #     self.update()

            self.window.clear(sf.Color.BLACK)
            self.render()

            self.window.view = self.window.default_view
            if self.debug:
                for txt in self.debug_texts:
                    txt.update()
                    self.window.draw(txt)

            self.window.display()
