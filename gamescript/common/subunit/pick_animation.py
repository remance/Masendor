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
                else:
                    if self.walk:
                        animation_name += "Walk" + self.action_list[weapon]["Attack"]
                    elif self.run:
                        animation_name += "Run" + self.action_list[weapon]["Attack"]
            elif "Charge" in self.current_action["name"]:
                animation_name = self.animation_race_name + "_" + self.current_action["name"]
            else:
                animation_name = self.animation_race_name + "_" + self.current_action["name"]
        else:
            state_name = self.subunit_state[0]  # use idle state
            if self.state not in (10, 11, 12, 13):  # melee and shoot state use Action to attack
                state_name = self.subunit_state[self.state]  # use state to pick animation
            animation_name = self.animation_race_name + "_" + state_name
            if animation_name not in self.animation_pool:  # instead use state animation and main weapon
                animation_name = self.animation_race_name + "_" + \
                                 self.action_list[0]["Common"] + "_" + \
                                 state_name
        self.current_animation = {key: value for key, value in self.animation_pool.items() if animation_name in key}
        self.current_animation = {key: value for key, value in self.current_animation.items() if
                                  "/" + str(self.equipped_weapon) == key[-2:]}  # pick animation of current weapon set
        self.current_animation = self.current_animation[random.choice(list(self.current_animation.keys()))]

    except KeyError:  # animation not found, use default
        self.current_animation = self.animation_pool[self.animation_race_name + "_Default/0"]

    except IndexError:  # animation not found, use default
        self.current_animation = self.animation_pool[self.animation_race_name + "_Default/0"]
        print(animation_name)
        print(self.animation_pool)
    #     print(self.current_animation)
    #     asdf
