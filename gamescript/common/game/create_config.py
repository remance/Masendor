import configparser
import os

import pygame
import screeninfo


def create_config(self):
    config = configparser.ConfigParser()

    screen = screeninfo.get_monitors()[0]
    screen_width = int(screen.width)
    screen_height = int(screen.height)
    config["VERSION"] = {"ver": self.game_version}
    config["DEFAULT"] = {"screen_width": screen_width, "screen_height": screen_height, "full_screen": 0,
                         "player_Name": "Noname", "master_volume": 100.0, "music_volume": 100.0,
                         "voice_volume": 100.0, "effect_volume": 50.0, "max_fps": 60, "ruleset": 0,
                         "language": "en", "control player 1": "keyboard", "control player 2": "joystick",
                         "keybind player 1": {"keyboard": {"Main Weapon Attack": "left click",
                                                           "Sub Weapon Attack": "right click",
                                                           "Move Left": pygame.K_a, "Move Right": pygame.K_d,
                                                           "Move Up": pygame.K_w, "Move Down": pygame.K_s,
                                                           "Menu/Cancel": pygame.K_ESCAPE,
                                                           "Order Menu": pygame.K_TAB, "Run Input": pygame.K_LSHIFT,
                                                           "Skill 1": pygame.K_q, "Skill 2": pygame.K_e,
                                                           "Skill 3": pygame.K_r, "Skill 4": pygame.K_t,
                                                           "Swap Weapon Set 1": pygame.K_1,
                                                           "Swap Weapon Set 2": pygame.K_2,
                                                           "Toggle Run": pygame.K_z,
                                                           "Auto Move": pygame.K_x},
                                              "joystick": {"Main Weapon Attack": 4,
                                                           "Sub Weapon Attack": 5,
                                                           "Move Left": "axis-0", "Move Right": "axis+0",
                                                           "Move Up": "axis-1", "Move Down": "axis+1",
                                                           "Menu/Cancel": 9,
                                                           "Order Menu": 8, "Run Input": 10,
                                                           "Skill 1": 0, "Skill 2": 1,
                                                           "Skill 3": 2, "Skill 4": 3,
                                                           "Swap Weapon Set 1": 6,
                                                           "Swap Weapon Set 2": 7,
                                                           "Toggle Run": "hat-0",
                                                           "Auto Move": "hat+0"}}}

    config["USER"] = {key: value for key, value in config["DEFAULT"].items()}
    with open(os.path.join(self.main_dir, "configuration.ini"), "w") as cf:
        config.write(cf)
    config.read_file(open(os.path.join(self.main_dir, "configuration.ini")))
    return config
