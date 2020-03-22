from .resource_loader import load_resources
from .resource_path import find_resource, RES_DIR


class ResMeta(type):
    """
    To use the res manager, there are some naming convention you should follow:
        - your files and folders should respect python variable naming rules
        - your files and folders names should not start with an underscore
        - " Textures " , " Maps " and " Fonts " are reserved. Avoid using those as a name.
    """
    _ready = False
    _assets = resource_loader.Dir("assets")
    _textures = resource_loader.Dir("textures")
    _maps = resource_loader.Dir("maps")
    _fonts = resource_loader.Dir("fonts")
    _parent = None

    @property
    def Textures(cls):
        return cls._textures

    @property
    def Maps(cls):
        return cls._maps

    @property
    def Fonts(cls):
        return cls._fonts

    @property
    def is_ready(cls):
        return cls._ready

    def __iter__(cls):
        for x in cls._assets:
            yield x

    def values(cls):
        return cls._assets.values()

    def items(cls):
        return cls._assets.items()

    def __getattr__(cls, item):
        if item[0] == "_":
            return cls.__dict__[item]
        return getattr(cls._assets, item)

    def __setattr__(cls, key, value):
        if key[0] != "_":
            raise AttributeError("You can not set attribute for Res class.")
        else:
            super().__setattr__(key, value)

    def all_files(cls):
        return cls._assets.all_files()

    def print_tree(cls):
        print(f"\n{RES_DIR}")
        cls._assets.print_tree(indent=1)
        print("")


class Res(metaclass=ResMeta):
    """
    A Resource manager. Automatically loads all resources found in `assets` directory
    To access a resource, you can use : `Res.folder_name.resource_name`
    Res loads all assets recursively, so you can access nested directories this way :
    `Res.folder1.folder2.foldeer3.resource_name`
    Res.Textures contains all textures at the same level.
    Res.Maps contains all tiled maps.
    Res.Fonts contains all fonts.
    """
    @classmethod
    def load(cls):
        """Load all resources into Res.
        You need to call this methode once at the start of your game (via App.load_resources() )
        if you want to use the resource manager.
        """
        cls._assets._parent = cls
        load_resources(cls._assets, find_resource(RES_DIR))

        for tile_map in cls.Maps.values():
            tile_map.load()

        cls._ready = True
