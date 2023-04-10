import pygame

from gamescript import battleui


def make_battle_ui(battle_ui_image, battle_icon_image, team_colour, screen_size, screen_scale):
    time_ui = battleui.TimeUI(battle_ui_image["timebar"])
    time_number = battleui.Timer(time_ui.rect.topleft)  # time number on time ui

    image = pygame.Surface((battle_ui_image["timebar"].get_width(), 15))
    battle_scale_ui = battleui.BattleScaleUI(image, team_colour)

    # Right top bar ui that show rough information of selected battalions
    wheel_ui = battleui.WheelUI(battle_ui_image["wheel"], battle_ui_image["wheel_selected"],
                                (screen_size[0] / 2, screen_size[1] / 2), screen_size)

    # Hero ui that show leader weapon, health, and portrait
    command_ui = battleui.HeroUI(screen_scale, (battle_ui_image["weapon_box_primary"],
                                                battle_ui_image["weapon_box_secondary"]),
                                 battle_ui_image["status_box"])

    return {"time_ui": time_ui, "time_number": time_number, "battle_scale_ui": battle_scale_ui,
            "wheel_ui": wheel_ui, "command_ui": command_ui}
