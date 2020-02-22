from sfml import sf

desktop_mode = sf.VideoMode.get_desktop_mode()
all_modes = sf.VideoMode.get_fullscreen_modes()

fullscreen_mode = all_modes[0]
SCREEN_W = float(fullscreen_mode.width)  # 1600
SCREEN_H = float(fullscreen_mode.height)  # 900
