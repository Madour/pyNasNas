from sfml import sf
import os
from .resource_path import resource_path
from . import tile_mapping as tm


def load_resources(obj, path, ext):
    for filename in os.listdir(resource_path(path)):
        if filename.endswith(ext):
            if ext == ".png":
                setattr(obj, filename[:-4], sf.Texture.from_file(resource_path(os.path.join(path, filename))))
            elif ext == ".tmx":
                setattr(obj, filename[:-4], tm.TileMap(resource_path(os.path.join(path, filename))))
            elif ext == ".ttf":
                font = sf.Font.from_file(resource_path(os.path.join(path, filename)))
                font.get_texture(8).smooth = False
                font.get_texture(16).smooth = False
                font.get_texture(32).smooth = False
                setattr(obj, filename[:-4], font)

            # print(f"Loaded {ext} : {filename}")
        else:
            if '.' in filename:
                continue
            dir = Dir()
            load_resources(dir, os.path.join(path, filename), ext)
            setattr(obj, filename, dir)


class Dir:
    pass
