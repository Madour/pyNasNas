import src.sfmlGameEngine as ge
from sfml import sf


class Sprites:
    character = ge.Sprite(
        name="adventurer",
        texture=ge.Res.textures.adventurer,
        anims={
            "idle": ge.Anim(
                [
                    sf.Rect((14, 7), (19, 29)),
                    sf.Rect((14, 7), (19, 29)),
                    sf.Rect((66, 6), (17, 30)),
                    sf.Rect((115, 6), (19, 30)),
                    sf.Rect((163, 7), (20, 29)),
                    sf.Rect((115, 6), (19, 30)),
                    sf.Rect((66, 6), (17, 30)),
                ],
                [1, 299, 300, 300, 300, 300, 300],
                [(11, 29), (11, 29), (9, 30), (10, 30), (12, 29), (10, 30), (9, 30)],
                loop=True
            ),
            "walk": ge.Anim(
                [
                    sf.Rect((67, 45), (20, 28)),
                    sf.Rect((117, 46), (20, 27)),
                    sf.Rect((166, 48), (20, 25)),
                    sf.Rect((217, 45), (23, 28)),
                    sf.Rect((266, 46), (20, 27)),
                    sf.Rect((316, 48), (20, 25)),
                ],
                [100, 100, 100, 100, 100, 100],
                [(12, 28), (15, 27), (15, 25), (13, 28), (14, 27), (15, 25)],
            ),
        }
    )
