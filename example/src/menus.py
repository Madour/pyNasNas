from sfml import sf

import src.NasNas as ns
from example.src.fonts import bitmap_font

# defining a btn_style
btn_anim = ns.Anim([
    ns.AnimFrame(ns.Rect((0, 0), (64, 32)), 400),
    ns.AnimFrame(ns.Rect((0, 32), (64, 32)), 400)
])
btn_style = ns.ui.ButtonStyle(width=64, height=32, background=ns.Res.ui_texture, font=bitmap_font,
                              anim=btn_anim, margin=(0, 0, 8, 0))

play_btn = ns.ui.Button("PLAY", style=btn_style)


@play_btn.on_press
def btn_press_action():
    play_btn.game.menu_exit_transition.start()
@play_btn.on_hover
def btn_hover():
    play_btn.anim_player.resume()
@play_btn.on_unhover
def btn_unhover():
    play_btn.anim_player.stop()

resume_btn = ns.ui.Button("RESUME", style=btn_style)

@resume_btn.on_press
def resume_btn_on_press():
    resume_btn.game.game_menu.close()
@resume_btn.on_hover
def btn_hover():
    resume_btn.anim_player.resume()
@resume_btn.on_unhover
def btn_unhover():
    resume_btn.anim_player.stop()

quit_btn = ns.ui.Button("QUIT", style=btn_style)

@quit_btn.on_press
def quit_btn_press_action():
    quit_btn.game.quit_transition.start()
@quit_btn.on_hover
def btn_hover():
    quit_btn.anim_player.resume()
@quit_btn.on_unhover
def btn_unhover():
    quit_btn.anim_player.stop()

# BoxBorder can generate a box of any size with the given texture pattern
menu_border = ns.ui.BoxBorder(ns.Res.ui_texture, (0, 64), (8, 8))

# defining a style for the menus
menu_style = ns.ui.MenuStyle(width=btn_style.bounds.x, height=btn_style.bounds.y*2 - btn_style.margin[2],
                             padding=(16, 16, 16, 16),
                             background=menu_border)


class MainMenu(ns.ui.VerticalMenu):
    def __init__(self):
        super().__init__("main_menu", menu_style, play_btn, quit_btn)
        self.center = self.game.window.ui_view.center

    def event_handler(self, event: sf.Event):
        if event == sf.Event.KEY_RELEASED:
            if event['code'] == ns.Keyboard.DOWN:
                self._buttons[self.cursor_index].anim_player.stop()
                self.cursor_index = (self.cursor_index + 1) % len(self.buttons)
                self._buttons[self.cursor_index].anim_player.resume()

            elif event['code'] == ns.Keyboard.UP:
                self._buttons[self.cursor_index].anim_player.stop()
                self.cursor_index = (self.cursor_index - 1) % len(self.buttons)
                self._buttons[self.cursor_index].anim_player.resume()

            elif event['code'] in [ns.Keyboard.SPACE, ns.Keyboard.RETURN]:
                self.buttons[self.cursor_index].press()
