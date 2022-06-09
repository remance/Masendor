import random

equip_set = ("Main", "Sub")


def pick_animation(self):
    try:
        if self.current_action:  # pick animation with current action
            if "Action " in self.current_action[0]:
                equip = int(self.current_action[0][-1])
                weapon = self.weapon_name[self.equipped_weapon][equip]
                animation_name = self.race_name + "_" + equip_set[equip] + "_" + self.action_list[weapon]["Common"] + "_" + self.action_list[weapon]["Attack"]
            else:
                animation_name = self.race_name + "_" + self.current_action[0]
        else:  # use state to pick animation
            state_name = self.subunit_state[self.state]
            animation_name = self.race_name + "_" + self.action_list[self.weapon_name[0][0]]["Common"] + "_" + state_name + "/" + str(self.equipped_weapon)  #TODO change when add change equip

        self.current_animation = {key: value for key, value in self.animation_pool.items() if animation_name in key}
        self.current_animation = self.current_animation[random.choice(list(self.current_animation.keys()))]
    except:  # animation not found, use default
        self.current_animation = self.animation_pool[self.race_name + "_Default"]
