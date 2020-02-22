from . import resource_path
from .resource_loader import load_resources


class TexturesLoader:
    @classmethod
    def load(cls):
        load_resources(cls, resource_path.resource_path(resource_path.RES_DIR), ".png")

