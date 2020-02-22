from . import resource_path
from .resource_loader import load_resources


class FontsLoader:
    @classmethod
    def load(cls):
        load_resources(cls, resource_path.resource_path(resource_path.RES_DIR), ".ttf")

