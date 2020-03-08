from sfml import sf
from os.path import join

from .data.game_obj import GameObject
from .data import const

from .reslib.resource_path import resource_path, RES_DIR
from .reslib import Res

from . import camera
from . import scenes
from . import debug
from .data.rect import Rect


class GameEngine:

    def __init__(self, title: str = None, w_width: int = 960, w_height: int = 540,
                 v_width: int = 960, v_height: int = 540, desired_fps: int = 60):
        """
        Initializes the engine and creates:
            - a window
            - a main scene
            - cameras (game, minimap and UI)
        Args:
            title (str): title of the game window
            w_width (int): window width
            w_height (int): window height
            v_width (int): game view width
            v_height (int): game view height
            desired_fps (int): desired fps
        """
        GameObject.game = self

        self.W_WIDTH, self.W_HEIGHT = w_width, w_height
        self.V_WIDTH, self.V_HEIGHT = v_width, v_height

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
        # list of all cameras/view used in the game
        self.cameras = {}
        # list of all scenes used in the game, usually 1 is enough
        self.scenes = []

        # Scene is where everything is drawn on
        self.scene = self.create_scene(w_width, w_height)

        # camera made to look at the GUI and HUD scene
        self.ui_camera = self.create_camera("default", 1, Rect((0, 0), (w_width, w_height)))

        # game camera, usually looks at the main scene (world map, scrolling level ...)
        self.game_camera = self.create_camera("game", 0, Rect((0, 0), (v_width, v_height)))

        # minimap, looks at the main scene but sees a larger area than the game camera
        self.minimap_camera = self.create_camera("minimap", 2, Rect((0, 0), (v_width*3, v_height*3)), Rect((0.8, 0), (0.2, 0.2)))
        self.minimap_camera.frames_delay = 0

        # clock and dt used for FPS calculation
        self.clock = sf.Clock()
        self.dt = 0

        self.debug = True
        self.debug_texts = []  #: list of DebugText

        self.scale_view()

    @staticmethod
    def load_resources(loading_image: bool = False):
        """
        Initialize the resources manager Res and load all resources in RES_DIR

        Args:
            loading_image (bool): Set to True to show a small Loading window when Res is loading assets.
        """
        if loading_image:
            window = sf.RenderWindow(sf.VideoMode(160, 90), "Game Base", sf.Style.NONE)
            l = sf.Sprite(sf.Texture.from_file(resource_path(join(RES_DIR, "loading.png"))))
            window.draw(l)
            window.display()
            Res.load()
            window.close()
        else:
            Res.load()

    def create_scene(self, width: int, height: int) -> scenes.Scene:
        """
        Creates a new Scene and returns it.

        Args:
            width (int): width of the new scene
            height (int): height of the new scene

        Returns:
            Returns the created Scene.
        """
        s = scenes.Scene(width, height)
        self.scenes.append(s)
        return s

    def create_camera(self, name: str, order: int, camwindow: Rect, viewport: Rect = Rect((0, 0), (1, 1))) -> camera.Camera:
        """
        Creates a new Camera and returns it

        Args:
            name (str):
                The name of the new Camera, should be unique.
            order (int):
                The order of display. 0 will be displayed first, 1 will be displayed over 0, etc
            camwindow (Rect):
                The window the Camera is looking at.
                For exemple, a Camera with a window=sf.Rect((0, 10), (20, 20)) will look at a square 20x20 located at (0, 10)
            viewport (Rect):
                The place and surface the Camera will take on the window.
                If we take the previous window, and a viewport of sf.Rect((0.5, 0), (0.2, 0.2)), the window looked at will
                be displayed on a surface equal to 20% x 20% of the window located at (50%, 0) of the window size.

        Returns:
            Returns the created Camera.
        """
        cam = camera.Camera(name)
        cam.reset(camwindow.topleft, camwindow.size)
        cam.viewport = viewport
        cam.vp_base_size = viewport.size
        cam.vp_base_pos = viewport.topleft
        self.cameras[order] = cam
        return cam

    def add_debug_text(self, instance:object, attr_name: str, position: tuple, float_round: int = None):
        """
        Adds a DebugText to self.debug_texts. The text will be drawn at the given position

        Args:
            instance (object):
                An instance of any object.
            attr_name (str):
                Attribute name of the instance.
            position (tuple):
                The position where the text will be drawn
            float_round (int):
                If the attribute value is a float, rounds that float using round(instance.attr_name, float_round)
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
        Scales all Cameras to keep a good apsect ratio and avoid deformation when resizing the window.
        """
        # larger than usual window
        if float(self.window.size.x) / float(self.window.size.y) > self.W_WIDTH / self.W_HEIGHT:
            viewport_w = (float(self.window.size.y) * (self.W_WIDTH / self.W_HEIGHT)) / float(self.window.size.x)
            viewport_h = 1
            viewport_x = (1-viewport_w)/2
            viewport_y = 0
        # higher than usual window
        else:
            viewport_w = 1
            viewport_h = (float(self.window.size.x) / (self.W_WIDTH / self.W_HEIGHT)) / float(self.window.size.y)
            viewport_x = 0
            viewport_y = (1-viewport_h)/2
        for cam in self.cameras.values():
            cam.viewport = sf.Rect(
                (viewport_x + cam.vp_base_pos.x*(1-2*viewport_x), viewport_y + cam.vp_base_pos.y*(1-2*viewport_y)),
                (viewport_w * cam.vp_base_size.x, viewport_h * cam.vp_base_size.y)
            )


    def _key_handler(self, key: int, event_type: str):
        """
        Update inputs list.
        Args:
            key (int): code of a key.
            event_type (str): equals "pressed" when a key is pressed or "released" when it is released.
        """
        if key not in self.inputs and event_type == "pressed":
            self.inputs.insert(0, key)
        else:
            if key in self.inputs and event_type == "released":
                self.inputs.remove(key)

    def _store_inputs(self, event: sf.Event):
        """
        Add all pressed keys to self.inputs
        Calls self.scale_view() when the window is resized

        Args:
            event (sf.Event): a window event
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
        """
        event_handler is called evry time there is an event happening (key pressed, mouse move, lost focus ...)
        Override this method to make your own event handling

        Args:
            event (sf.Event): a window event
        """
        pass

    def update(self):
        """
        Update all Cameras used.
        Override this method without forgetting to call super().update()
        """
        for cam in self.cameras.values():
            cam.update(self.dt)

    def _render(self):
        """
        Draw all Scenes and Layers in order.
        Layer 0 will be drawn first, layer 1 will be drawn over layer 0 etc
        Internal usage only, do not override or call this method.
        """
        for scene in self.scenes:
            scene.update()

        sorted_cameras = [cam for order, cam in sorted(self.cameras.items(), key=lambda item: item[0])]
        for cam in sorted_cameras:
            if cam.visible:
                self.window.view = cam
                if cam.has_scene():
                    self.window.draw(cam.scene)

    def run(self):
        """
        Starts the game loop.
        """
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

            self._render()

            self.window.view = self.window.default_view
            if self.debug:
                for txt in self.debug_texts:
                    txt.update()
                    self.window.draw(txt)

            self.window.display()