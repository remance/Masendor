import pygame

from engine.uibattle.uibattle import TimeUI, Timer, BattleScaleUI, WheelUI, FollowerUI, HealthBar, \
    StaminaBar, WeaponUI, StatusUI


def make_battle_ui(battle_ui_image):
    from engine.game.game import Game
    from engine.battle.battle import Battle
    team_colour = Game.team_colour
    screen_scale = Game.screen_scale
    battle_camera_size = Battle.battle_camera_size
    time_ui = TimeUI(battle_ui_image["timebar"])
    time_number = Timer(time_ui.rect.topleft)  # time number on time ui

    image = pygame.Surface((battle_ui_image["timebar"].get_width(), 15))
    battle_scale_ui = BattleScaleUI(image, team_colour)

    # Right top bar ui that show rough information of selected battalions
    wheel_ui = WheelUI(battle_ui_image["wheel"], battle_ui_image["wheel_selected"],
                       (battle_camera_size[0] / 2, battle_camera_size[1] / 2))

    health_bar = HealthBar(battle_ui_image["health_bar"],  # TODO Change pos later when box UI is more final
                           (battle_ui_image["health_bar"].get_width(), 300 * screen_scale[1]))

    stamina_bar = StaminaBar(battle_ui_image["stamina_bar"],
                             (battle_ui_image["stamina_bar"].get_width() * 2.5, 300 * screen_scale[1]))

    weapon_ui = WeaponUI((battle_ui_image["weapon_box_primary"], battle_ui_image["weapon_box_secondary"]),
                         (90 * screen_scale[0], 500 * screen_scale[1]))

    follower_ui = FollowerUI((20 * screen_scale[0], 700 * screen_scale[1]))
    status_ui = StatusUI(battle_ui_image["status_box"], (0, 800 * screen_scale[1]))

    return {"time_ui": time_ui, "time_number": time_number, "battle_scale_ui": battle_scale_ui,
            "wheel_ui": wheel_ui, "follower_ui": follower_ui, "health_bar": health_bar, "stamina_bar": stamina_bar,
            "weapon_ui": weapon_ui, "status_ui": status_ui}
