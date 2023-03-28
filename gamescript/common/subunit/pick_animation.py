from random import choice

equip_set = ("Main", "Sub")


def pick_animation(self):
    if self.current_action:  # pick animation with current action
        if "Action " in self.current_action["name"]:
            weapon = self.current_action["weapon"]
            animation_name = equip_set[weapon] + "_"
            if "run" in self.current_action:
                animation_name += "Run" + self.action_list[weapon]["Attack"]
            elif "walk" in self.current_action:
                animation_name += "Walk" + self.action_list[weapon]["Attack"]
            else:
                animation_name += self.action_list[weapon]["Attack"]

        elif "charge" in self.current_action:
            weapon = self.current_action["weapon"]
            animation_name = equip_set[weapon] + "_Charge"
        else:
            animation_name = self.current_action["name"]
    else:  # idle animation
        animation_name = "Idle"

    self.current_animation = {key: value for key, value in self.animation_pool.items() if animation_name in key}
    self.current_animation = {key: value for key, value in self.current_animation.items() if "/" not in key or
                              str(self.equipped_weapon_str) == key[-1]}
    if self.current_animation:
        self.current_animation = self.current_animation[choice(tuple(self.current_animation.keys()))]
    else:  # animation not found, use default
        self.current_animation = self.animation_pool["Default"]
        # print(self.name, animation_name)
        # print(list(self.animation_pool.keys()))
        # asdf

    self.current_animation_direction = self.current_animation[self.sprite_direction]

    self.max_show_frame = self.current_animation["frame_number"]

    current_animation = self.current_animation_direction[self.show_frame]
    self.image = current_animation["sprite"]
    self.offset_pos = self.pos - current_animation["center_offset"]
    self.rect = self.image.get_rect(center=self.offset_pos)
    self.effectbox.rect.center = self.offset_pos

    self.animation_play_time = self.default_animation_play_time  # get new play speed
    if "play_time_mod" in self.current_animation[self.show_frame]["frame_property"]:
        self.animation_play_time *= self.current_animation[self.show_frame]["frame_property"]["play_time_mod"]
    elif "play_time_mod" in self.current_animation[self.show_frame]["animation_property"]:
        self.animation_play_time *= self.current_animation[self.show_frame]["animation_property"]["play_time_mod"]
