import random
equip_set = ("Main", "Sub")


def pick_animation(self):
    try:
        if self.state == 10:  # melee animation
            equip = random.randint(0, 1)
            weapon = self.weapon_name[random.randint(0, 1)][equip]
            animation_name = self.race_name + "_" + equip_set[equip] + "_" + self.action_list[weapon]["Common"] + "_" + self.action_list[weapon]["Attack"]
        elif self.state in (4, 13) and self.charge_skill in self.skill_effect:  # charge animation
            animation_name = self.race_name + "_" + "Main" + self.action_list[self.weapon_name[0][0]]["Common"] + "_" + "Charge"
        else:
            state_name = self.subunit_state[self.state]
            animation_name = self.race_name + "_" + self.action_list[self.weapon_name[0][0]]["Common"] + "_" + state_name + "/" + str(self.equipped_weapon)  #TODO change when add change equip
        self.current_animation = {key: value for key, value in self.animation_pool.items() if animation_name in key}
        self.current_animation = self.current_animation[random.choice(list(self.current_animation.keys()))]
    except:  # animation not found, use default
        self.current_animation = self.animation_pool[self.race_name + "_Default"]
