from sfml import sf

from .data.game_obj import GameObject
from .data import const

from . import camera
from . import scenes
from . import debug
from . import transitions
from . import window
from .data.rect import Rect

from typing import List, Optional


class App:
    def __init__(self, title: str = "NasNas game", w_width: int = 960, w_height: int = 540,
                 v_width: float = 960, v_height: float = 540, fps: Optional[int] = 60):
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
            fps (int): desired fps
        """
        GameObject.game = self

        self.W_WIDTH, self.W_HEIGHT = w_width, w_height
        self.V_WIDTH, self.V_HEIGHT = v_width, v_height

        # Game name, displayed in window title
        self.name = title

        self.desired_fps = fps
        self._window = window.RenderWindow(sf.VideoMode(w_width, w_height), self.name)

        if self.desired_fps:
            self.window.framerate_limit = self.desired_fps

        self._fullscreen = False

        # inputs from keyboard are stored in this list
        self._inputs: List[int] = []
        # list of all cameras/view used in the game
        self._cameras: List[camera.Camera] = []
        # list of all scenes used in the game, usually 1 is enough
        self._scenes: List[scenes.Scene] = []
        # list of all playing transitions
        self._transitions: List[transitions.Transition] = []

        self._default_view: camera.Camera = camera.Camera("default_view", -1)
        self._default_view.reset((0, 0), (v_width, v_height))
        self._default_view.reset_viewport((0, 0), (1, 1))

        # Scene is where everything is drawn on
        self.scene = self.create_scene(w_width, w_height)

        # game camera, usually looks at the main scene (world map, scrolling level ...)
        self.game_camera = self.create_camera("game", 0, Rect((0, 0), (v_width, v_height)))

        # clock and dt used for FPS calculation
        self.clock = sf.Clock()
        self.dt = 0

        self.debug = True
        self.debug_texts = []  # list of DebugText

        self.scale_view()

    @property
    def window(self) -> window.RenderWindow:
        return self._window

    @property
    def fullscreen(self) -> bool:
        return self._fullscreen

    @property
    def inputs(self) -> List[int]:
        return self._inputs

    @property
    def cameras(self) -> List[camera.Camera]:
        return self._cameras

    @property
    def scenes(self) -> List[scenes.Scene]:
        return self._scenes

    @property
    def transitions(self) -> List[transitions.Transition]:
        return self._transitions

    def create_scene(self, width: int, height: int):
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
        cam = camera.Camera(name, order)
        cam.reset(camwindow.topleft, camwindow.size)
        cam.reset_viewport(viewport.topleft, viewport.size)
        self.cameras.append(cam)
        return cam

    def add_debug_text(self, instance: object, attr_name: str, position: tuple, float_round: int = None):
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

    def toggle_fullscreen(self):
        if not self.fullscreen:
            self.window.close()
            self._window = sf.RenderWindow(sf.VideoMode(const.SCREEN_W, const.SCREEN_H), self.name, sf.Style.NONE)
            self.window.framerate_limit = self.desired_fps
            self.window.mouse_cursor_visible = False
            self.window.vertical_synchronization = True
            self._fullscreen = True
            self._inputs = []
            self.scale_view()
        else:
            self.window.close()
            self._window = sf.RenderWindow(sf.VideoMode(self.W_WIDTH, self.W_HEIGHT), self.name, sf.Style.DEFAULT)
            self.window.framerate_limit = self.desired_fps
            self.window.mouse_cursor_visible = True
            self.window.vertical_synchronization = True
            self._fullscreen = False
            self._inputs = []
            self.scale_view()

    def scale_view(self):
        """
        Scales all Cameras to keep a good aspect ratio and avoid deformation when resizing the window.
        """
        # wider than usual window
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
        for cam in self.cameras:
            cam.viewport = sf.Rect(
                (viewport_x + cam.vp_base_pos.x*(1-2*viewport_x), viewport_y + cam.vp_base_pos.y*(1-2*viewport_y)),
                (viewport_w * cam.vp_base_size.x, viewport_h * cam.vp_base_size.y)
            )

    def _store_inputs(self, event: sf.Event):
        """
        Handles window close event.
        Calls self.scale_view() when the window is resized
        Update inputs list.

        Args:
            event (sf.Event): a window event
        """
        if event == sf.Event.CLOSED:
            self.window.close()
        elif event == sf.Event.KEY_PRESSED:
            if event['code'] not in self.inputs:
                self.inputs.insert(0, event['code'])
        elif event == sf.Event.KEY_RELEASED:
            if event['code'] in self.inputs:
                self.inputs.remove(event['code'])

    def event_handler(self, event: sf.Event):
        """
        event_handler is called every time there is an event happening (key pressed, mouse move, lost focus ...)
        Override this method to make your own event handling

        Args:
            event (sf.Event): a window event
        """
        pass

    def update(self):
        """
        Write here your game logic
        """

    def _render(self):
        """
        Draw all Scenes and Layers in order.
        Layer 0 will be drawn first, layer 1 will be drawn over layer 0 etc
        Internal usage only, do not override or call this method.
        """
        for scene in self.scenes:
            scene._render()
        for cam in self.cameras:
            cam.update(self.dt)
        self.cameras.sort(key=lambda x: x.render_order)
        for cam in self.cameras:
            if cam.visible:
                self.window.view = cam
                if cam.has_scene():
                    self.window.draw(cam.scene)

        # drawing transitions on top of everything else directly on the window
        self.window.view = self._default_view
        for transition in self.transitions:
            transition.update()
            self.window.draw(transition)

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

            self.window.clear(sf.Color.BLACK)

            self._render()

            self.window.view = self.window.default_view
            if self.debug:
                for txt in self.debug_texts:
                    txt.update()
                    self.window.draw(txt)

            self.window.display()
