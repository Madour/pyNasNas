import src.NasNas as ns

# loading a BitmapFont from a texture
bitmap_font = ns.BitmapFont(
    ns.Res.Textures.font, (8, 8),
    chars_map=" ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    spacings_map={"O": 8}
)
