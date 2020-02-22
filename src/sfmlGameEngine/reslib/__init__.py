from . import textures_loader, maps_loader, fonts_loader


class Res:
    """A Resource manager. Automatically loads all resources found in `assets` directory

    """

    textures = textures_loader.TexturesLoader
    "Stores all sf.Texture loaded from .png files"

    maps = maps_loader.MapsLoader
    "Store all ge.TileMap loaded from .tmx files"

    fonts = fonts_loader.FontsLoader
    "Store all sf.Font loaded from .ttf files"

    ready = False

    @classmethod
    def load(cls):
        """Load all resources into Res.
        You need to call this methode once at the start of your game (via GameEngine.load_resources() )
        if you want to use the resource manager.
        """
        textures_loader.TexturesLoader.load()
        maps_loader.MapsLoader.load()
        fonts_loader.FontsLoader.load()
        cls.ready = True
