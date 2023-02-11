import random

equip_set = ("Main", "Sub")


def pick_animation(self):
    try:
        if self.current_action:  # pick animation with current action
            if "Action " in self.current_action["name"]:
                weapon = int(self.current_action["name"][-1])
                animation_name = self.animation_race_name + "_" + equip_set[weapon] + "_" + self.action_list[weapon][
                    "Common"] + "_"
                if "move attack" not in self.current_action:
                    animation_name += self.action_list[weapon]["Attack"]
            elif "Charge" in self.current_action["name"]:
                weapon = int(self.current_action["name"][-1])
                animation_name = self.animation_race_name + "_" + equip_set[weapon] + "_" + self.action_list[weapon][
                    "Common"] + "_Charge"
            elif "main_weapon" in self.current_action:  # animation that use main weapon specifically like walk, run
                animation_name = self.animation_race_name + "_" + self.action_list[0]["Common"] + "_" + \
                                 self.current_action["name"]
            else:
                animation_name = self.animation_race_name + "_" + self.current_action["name"]
        else:  # idle animation
            animation_name = self.animation_race_name + "_" + self.action_list[0]["Common"] + "_Idle"

        self.current_animation = {key: value for key, value in self.animation_pool.items() if animation_name in key}
        self.current_animation = {key: value for key, value in self.current_animation.items() if "/" not in key or
                                  "/" + str(self.equipped_weapon) == key[-2:]}  # pick animation of current weapon set
        self.current_animation = self.current_animation[random.choice(list(self.current_animation.keys()))]

    except (KeyError, IndexError):  # animation not found, use default
        self.current_animation = self.animation_pool[self.animation_race_name + "_Default"]
        # if self.leader is not None:
        #     print(animation_name)
        #     print(list(self.animation_pool.keys()))
        #     asdf

    self.current_animation["name"] = animation_name

    self.animation_play_speed = self.default_animation_play_speed  # get new play speed
    if "player_speed_mod" in self.current_animation[self.show_frame]["frame_property"]:
        self.animation_play_speed *= self.current_animation[self.show_frame]["frame_property"]["player_speed_mod"]
    elif "player_speed_mod" in self.current_animation[self.show_frame]["animation_property"]:
        self.animation_play_speed *= self.current_animation[self.show_frame]["animation_property"]["player_speed_mod"]
