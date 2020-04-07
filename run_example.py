import os
from sfml import sf
import src.NasNas as ns

# showing a custom loading screen
loading_window = sf.RenderWindow(sf.VideoMode(160, 90), "Loading", sf.Style.NONE)
found = True
try:
    l = sf.Sprite(sf.Texture.from_file(ns.find_resource(os.path.join("assets", "loading.png"))))
    loading_window.draw(l)
except:
    print("loading.png not found")
    found = False
if not found:
    try:
        l = sf.Text("Loading")
        l.font = sf.Font.from_file(ns.find_resource(os.path.join("assets", "arial.ttf")))
        loading_window.draw(l)
    except:
        print("arial.ttf not found")
loading_window.display()

ns.Res.load()

from example.src.game import MyGame
game = MyGame()

loading_window.close()

game.run()
