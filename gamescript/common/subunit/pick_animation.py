import random

equip_set = ("Main", "Sub")


def pick_animation(self):
    try:
        if self.current_action:  # pick animation with current action
            if "Action " in self.current_action[0]:
                equip = int(self.current_action[0][-1])
                weapon = self.weapon_name[self.equipped_weapon][equip]
                animation_name = self.animation_race_name + "_" + equip_set[equip] + "_" + self.action_list[weapon]["Common"] + "_" + self.action_list[weapon]["Attack"]
            elif "Charge" in self.current_action[0]:
                animation_name = self.animation_race_name + "_" + self.current_action[0]
            else:
                animation_name = self.animation_race_name + "_" + self.current_action[0]
        else:
            state_name = self.subunit_state[0]  # use idle state
            if self.state not in (10, 11, 12, 13):  # melee and shoot state use Action to attack
                state_name = self.subunit_state[self.state]  # use state to pick animation
            animation_name = self.animation_race_name + "_" + state_name
            if animation_name not in self.animation_pool:  # use animation with weapon prefix
                animation_name = self.animation_race_name + "_" + \
                                 self.action_list[self.weapon_name[self.equipped_weapon][0]]["Common"] + "_" + \
                                 state_name
        self.current_animation = {key: value for key, value in self.animation_pool.items() if animation_name in key}
        self.current_animation = {key: value for key, value in self.current_animation.items() if
                                  "/" + str(self.equipped_weapon) == key[-2:]}  # pick animation of current weapon set
        self.current_animation = self.current_animation[random.choice(list(self.current_animation.keys()))]

    except KeyError:  # animation not found, use default
        self.current_animation = self.animation_pool[self.animation_race_name + "_Default"]

    # except IndexError:
    #     print(animation_name)
    #     print(self.animation_pool)
    #     print(self.current_animation)
    #     asdf

