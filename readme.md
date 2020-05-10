# pyNasNas
### A simple game framework to get started quickly with python and sfml.

### Features :
 - [x] Automatic resource loader and  manager system
 - [x] Scene and Layers system
 - [x] Entities, sprites and animations 
 - [x] Cameras
 - [x] Text and bitmap fonts
 - [x] Tiled map loader (.tmx)
 - [x] Debug text display in-game
 - [x] Transitions
 
### In progress :
 - [x] Menus and UI
 
### To do :
 - [ ] Splash screens
 - [ ] Levels and game events management
 - [ ] In-game command line for debugging
 - [ ] Particles system


### Install

#### From pip
``` 
python3 -m pip install NasNas
```
Then you can import NasNas anywhere in your projects
```python
import NasNas as ns
```

#### From source
Download and extract the repository. Then run 
```
python3 setup.py install
```

#### Local install
Let's say your project has the following structure
```
YourProject
    |_ assets
    |_ src
    main.py
```

Download the repository and copy the NasNas folder into your project src folder.
```
YourProject
    |_ assets
    |_ src
        |_ NasNas
    main.py
```
Then you can, import NasNas with:
 ```python 
import src.NasNas as ns
```

### Get started

Visit the [wiki](https://github.com/Madour/pySFMLGameEngine/wiki) to get started.

You can also take a look at the example project to see how to use it.

Be sure to run run_example.py from example folder like this : `python3 ../run_example.py`

### Other

A C++ version of NasNas is under development, you can check it out [here](https://github.com/Madour/NasNas)

### Author

 - Modar Nasser