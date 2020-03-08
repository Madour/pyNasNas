from .resource_loader import load_resources
from .resource_path import find_resource, RES_DIR


class ResMeta(type):
    """A Resource manager. Automatically loads all resources found in `assets` directory"""

    ready = False
    assets = resource_loader.Dir("assets")
    assets._textures = resource_loader.Dir("textures")
    assets._maps = resource_loader.Dir("maps")
    assets._fonts = resource_loader.Dir("fonts")

    @property
    def Textures(cls):
        return cls._textures

    @property
    def Maps(cls):
        return cls._maps

    @property
    def Fonts(cls):
        return cls._fonts

    def __iter__(cls):
        for x in cls.__dict__["assets"]:
            yield x

    def __getattr__(cls, item):
        return getattr(cls.assets, item)


class Res(metaclass=ResMeta):
    @classmethod
    def load(cls):
        """Load all resources into Res.
        You need to call this methode once at the start of your game (via GameEngine.load_resources() )
        if you want to use the resource manager.
        """

        load_resources(cls.assets, find_resource(RES_DIR))
        for asset in cls.assets.all_files():
            if asset.__class__.__name__ == "TileMap":
                asset.load()
        cls.ready = True



