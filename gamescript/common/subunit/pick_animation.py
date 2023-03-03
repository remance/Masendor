from random import choice

equip_set = ("Main", "Sub")


def pick_animation(self):
    if self.current_action:  # pick animation with current action
        if "Action " in self.current_action["name"]:
            weapon = self.current_action["weapon"]
            animation_name = self.animation_race_name + "_" + equip_set[weapon] + "_" + self.action_list[weapon][
                "Common"] + "_"
            if "run" in self.current_action:
                animation_name += "Run" + self.action_list[weapon]["Attack"]
            elif "walk" in self.current_action:
                animation_name += "Walk" + self.action_list[weapon]["Attack"]
            else:
                animation_name += self.action_list[weapon]["Attack"]

        elif "charge" in self.current_action:
            weapon = self.current_action["weapon"]
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
    if self.current_animation:
        self.current_animation = self.current_animation[choice(list(self.current_animation.keys()))]
    else:  # animation not found, use default
        self.current_animation = self.animation_pool[self.animation_race_name + "_Default"]
        # print(animation_name)
        # print(list(self.animation_pool.keys()))
        # asdf

    self.current_animation["name"] = animation_name
    self.max_show_frame = len(self.current_animation[self.sprite_direction]) - 1

    self.animation_play_time = self.default_animation_play_time  # get new play speed
    if "play_time_mod" in self.current_animation[self.show_frame]["frame_property"]:
        self.animation_play_time *= self.current_animation[self.show_frame]["frame_property"]["play_time_mod"]
    elif "play_time_mod" in self.current_animation[self.show_frame]["animation_property"]:
        self.animation_play_time *= self.current_animation[self.show_frame]["animation_property"]["play_time_mod"]
