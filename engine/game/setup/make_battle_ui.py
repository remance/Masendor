import pygame

from engine.uibattle import uibattle


def make_battle_ui(battle_ui_image, team_colour, screen_size):
    time_ui = uibattle.TimeUI(battle_ui_image["timebar"])
    time_number = uibattle.Timer(time_ui.rect.topleft)  # time number on time ui

    image = pygame.Surface((battle_ui_image["timebar"].get_width(), 15))
    battle_scale_ui = uibattle.BattleScaleUI(image, team_colour)

    # Right top bar ui that show rough information of selected battalions
    wheel_ui = uibattle.WheelUI(battle_ui_image["wheel"], battle_ui_image["wheel_selected"],
                                (screen_size[0] / 2, screen_size[1] / 2))

    # Hero ui that show leader weapon, health, and portrait
    command_ui = uibattle.HeroUI((battle_ui_image["weapon_box_primary"],
                                  battle_ui_image["weapon_box_secondary"]),
                                 battle_ui_image["status_box"])

    return {"time_ui": time_ui, "time_number": time_number, "battle_scale_ui": battle_scale_ui,
            "wheel_ui": wheel_ui, "command_ui": command_ui}
