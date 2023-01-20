import pygame
from gamescript import battleui


def make_battle_ui(battle_ui_image, battle_icon_image, team_colour, screen_size):
    time_ui = battleui.TimeUI(battle_ui_image["timebar"])
    time_number = battleui.Timer(time_ui.rect.topleft)  # time number on time ui
    speed_number = battleui.TextSprite(1)  # self speed number on the time ui

    image = pygame.Surface((battle_ui_image["timebar"].get_width(), 15))
    battle_scale_ui = battleui.BattleScaleUI(image, team_colour)

    time_button = (battleui.UIButton(battle_ui_image["pause"], "pause"),  # time pause button
                   battleui.UIButton(battle_ui_image["timedec"], "decrease"),  # time decrease button
                   battleui.UIButton(battle_ui_image["timeinc"], "increase"))  # time increase button

    # Army select list ui
    unit_selector = battleui.UnitSelector((0, 0), battle_ui_image["unit_select_box"], icon_scale=0.25)
    battleui.UIScroll(unit_selector, unit_selector.rect.topright)  # scroll for unit select ui

    # Right top bar ui that show rough information of selected battalions
    unitstat_ui = battleui.TopBar(battle_ui_image["topbar"], battle_icon_image)

    wheel_ui = battleui.WheelUI(battle_ui_image["wheel"], battle_ui_image["wheel_selected"],
                                (screen_size[0] / 2, screen_size[1] / 2), screen_size)

    return {"time_ui": time_ui, "time_number": time_number, "speed_number": speed_number,
            "battle_scale_ui": battle_scale_ui, "time_button": time_button, "unit_selector": unit_selector,
            "unitstat_ui": unitstat_ui, "wheel_ui": wheel_ui}
