import pygame
from gamescript import battleui
from gamescript.common import utility

load_image = utility.load_image


def make_battle_ui(battle_ui_image, battle_icon_image, team_colour, screen_size):
    time_ui = battleui.TimeUI(battle_ui_image["timebar.png"])
    time_number = battleui.Timer(time_ui.rect.topleft)  # time number on time ui
    speed_number = battleui.TextSprite(1)  # self speed number on the time ui

    image = pygame.Surface((battle_ui_image["timebar.png"].get_width(), 15))
    battle_scale_ui = battleui.BattleScaleUI(image, team_colour)

    time_button = [battleui.UIButton(battle_ui_image["pause.png"], "pause"),  # time pause button
                        battleui.UIButton(battle_ui_image["timedec.png"], "decrease"),  # time decrease button
                        battleui.UIButton(battle_ui_image["timeinc.png"], "increase")]  # time increase button

    # Army select list ui
    unit_selector = battleui.UnitSelector((0, 0), battle_ui_image["unit_select_box.png"], icon_scale=0.6)
    battleui.UIScroll(unit_selector, unit_selector.rect.topright)  # scroll for unit select ui

    # Right top bar ui that show rough information of selected battalions
    unitstat_ui = battleui.TopBar(battle_ui_image["topbar.png"], battle_icon_image)

    eight_wheel_ui = battleui.WheelUI((battle_ui_image["8_wheel_top.png"], battle_ui_image["8_wheel_side.png"]),
                                      (battle_ui_image["8_wheel_top_selected.png"], battle_ui_image["8_wheel_side_selected.png"]),
                                      (screen_size[0] / 2, screen_size[1] / 2), screen_size)
    four_wheel_ui = battleui.WheelUI((battle_ui_image["4_wheel.png"],), (battle_ui_image["4_wheel_selected.png"],),
                                     (screen_size[0] / 2, screen_size[1] / 2), screen_size)

    return {"time_ui": time_ui, "time_number": time_number, "speed_number": speed_number,
            "battle_scale_ui": battle_scale_ui, "time_button": time_button, "unit_selector": unit_selector,
            "unitstat_ui": unitstat_ui, "eight_wheel_ui": eight_wheel_ui, "four_wheel_ui": four_wheel_ui}
