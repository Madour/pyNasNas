# pySFML Game Engine
### A simple game engine to get started quickly with python and sfml.

#### Features :
 - [x] Automatic resource loader and  manager system
 - [x] Scene and Layers system
 - [x] Entities, sprites and animations 
 - [x] Camera and minimap
 - [x] Text and bitmap fonts
 - [x] Tiled map loader (.tmx)
 - [x] Debug text display in-game
 
#### In progress :
 - [x] Transitions
 
#### To do :
 - [ ] Menus and UI
 - [ ] Splash screens
 - [ ] Levels and game events management
 - [ ] In-game command line for debugging
 - [ ] Particles system


#### Install

Let's say your project has the following structure
```
YourProject
    |_ assets
    |_ src
    main.py
```

Download the repository and copy the sfmlGameEngine folder into your project src folder.
```
YourProject
    |_ assets
    |_ src
        |_ sfmlGameEngine
    main.py
```
Then you can, import the engine with:
 ```python 
import src.sfmlGameEngine as ge
```

#### How to use

Visit the [wiki](https://github.com/Madour/pySFMLGameEngine/wiki) to learn how to use it.

You can also take a look at the example project to see how to use it.

Be sure to run run_example.py from example folder like this : `python3 ../run_example.py`
