import random

equip_set = ("Main", "Sub")


def pick_animation(self):
    try:
        add_equip_number_later = False
        if self.current_action:  # pick animation with current action
            if "Action " in self.current_action[0]:
                equip = int(self.current_action[0][-1])
                weapon = self.weapon_name[self.equipped_weapon][equip]
                animation_name = self.race_name + "_" + equip_set[equip] + "_" + self.action_list[weapon]["Common"] + "_" + self.action_list[weapon]["Attack"]
                add_equip_number_later = True
            elif "Charge" in self.current_action[0]:
                animation_name = self.race_name + "_" + self.current_action[0] + "/" + str(self.equipped_weapon)
            else:
                animation_name = self.race_name + "_" + self.current_action[0] + "/" + str(self.equipped_weapon)
        else:  # use state to pick animation
            state_name = self.subunit_state[self.state]
            animation_name = self.race_name + "_" + state_name
            if animation_name not in self.animation_pool:  # use animation with weapon prefix
                animation_name = self.race_name + "_" + self.action_list[self.weapon_name[self.equipped_weapon][0]]["Common"] + "_" + state_name + "/" + str(self.equipped_weapon)

        self.current_animation = {key: value for key, value in self.animation_pool.items() if animation_name in key}
        if add_equip_number_later:
            self.current_animation = {key: value for key, value in self.current_animation.items() if "/" + str(self.equipped_weapon) == key[-2:]}
        self.current_animation = self.current_animation[random.choice(list(self.current_animation.keys()))]

    except KeyError:  # animation not found, use default
        self.current_animation = self.animation_pool[self.race_name + "_Default"]
    #
    # except IndexError:
    #     print(animation_name)
    #     print(self.animation_pool)
    #     print(self.current_animation)
    #     asdf

