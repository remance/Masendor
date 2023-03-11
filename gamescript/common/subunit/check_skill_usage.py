def check_skill_usage(self):
    # Check which skill can be used, cooldown, discipline, stamina are checked. charge skill is excepted from this check
    if self.not_broken and "uncontrollable" not in self.current_action:
        if self.momentum == 1 and "charge" in self.current_action:  # use charge skill when momentum reach 1
            self.use_skill(self.charge_skill)
        elif self.command_action:
            target_pos = None
            if "skill" in self.command_action:  # use by AI
                skill = self.command_action["skill"]
                if "pos" in self.command_action:
                    target_pos = self.command_action["pos"]
            elif "Skill" in self.command_action["name"]:  # use by player
                if self.available_skill:  # no current action and has skill command waiting
                    skill = int(self.command_action["name"][-1])
                    if len(self.input_skill) > skill:
                        skill = tuple(self.input_skill.keys())[skill]
                    else:
                        self.command_action = {}
                        return
                else:
                    self.command_action = {}
                    return

            else:
                return

            if skill in self.available_skill:
                skill_data = self.input_skill[skill]
                action = skill_data["Action"].copy()
                weapon = None
                if "Action" in action[0]:
                    action[0] += " 0"  # use main hand by default for Action type animation skill
                    weapon = 0
                else:
                    action[0] = "Skill_" + action[0]
                self.command_action = {"name": action[0], "skill": skill}
                for key in self.weapon_skill:
                    if skill == self.weapon_skill[key]:
                        weapon = key

                if self.player_control and skill_data["Range"]:  # skill that require player target
                    self.command_action["require input"] = True
                if weapon is not None:  # skill use weapon
                    self.command_action["weapon"] = weapon
                if target_pos:
                    self.command_action["pos"] = target_pos

                self.available_skill.remove(skill)
                if len(action) > 1:
                    self.command_action |= {this_prop: True for this_prop in action[1:]}
            else:
                self.command_action = {}

