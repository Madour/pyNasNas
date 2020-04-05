import src.NasNas as ns


class Sprites:
    character = ns.Sprite(
        name="adventurer",
        texture=ns.Res.adventurer,
        anims={
            "idle": ns.Anim(
                frames=[
                    ns.AnimFrame(ns.Rect((14, 7), (19, 29)), 299, (11, 29)),
                    ns.AnimFrame(ns.Rect((66, 6), (17, 30)), 300, (9, 30)),
                    ns.AnimFrame(ns.Rect((115, 6), (19, 30)), 300, (10, 30)),
                    ns.AnimFrame(ns.Rect((163, 7), (20, 29)), 300, (12, 29)),
                    ns.AnimFrame(ns.Rect((115, 6), (19, 30)), 300, (10, 30)),
                    ns.AnimFrame(ns.Rect((66, 6), (17, 30)), 300, (9, 30)),
                ],
                loop=True
            ),
            "walk": ns.Anim(
                frames=[
                    ns.AnimFrame(ns.Rect((67, 45), (20, 28)), 100, (12, 28)),
                    ns.AnimFrame(ns.Rect((117, 46), (20, 27)), 100, (15, 27)),
                    ns.AnimFrame(ns.Rect((166, 48), (20, 25)), 100, (15, 25)),
                    ns.AnimFrame(ns.Rect((217, 45), (23, 28)), 100, (13, 28)),
                    ns.AnimFrame(ns.Rect((266, 46), (20, 27)), 100, (14, 27)),
                    ns.AnimFrame(ns.Rect((316, 48), (20, 25)), 100, (15, 25)),
                ],
                loop=True
            ),
        }
    )
