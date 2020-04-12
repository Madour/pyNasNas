from typing import Union, Tuple

from sfml import sf


def to_Vector2(arg: Union[Tuple[int, int], sf.Vector2]) -> sf.Vector2:
    if isinstance(arg, sf.Vector2):
        return arg
    else:
        return sf.Vector2(arg[0], arg[1])