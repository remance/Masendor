def check_skill_usage(self):
    # Check which skill can be used, cooldown, discipline, stamina are checked. charge skill is excepted from this check
    if self.not_broken and "uncontrollable" not in self.current_action:
        if self.momentum == 1 and "charge" in self.current_action:  # use charge skill when momentum reach 1
            self.use_skill(self.charge_skill)
        elif self.command_action:
            if "skill" in self.command_action:  # use by AI
                skill = self.command_action["skill"]
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
                action = self.input_skill[skill]["Action"].copy()
                if "Action" in action[0]:
                    action[0] += " 0"  # use main hand by default for Action type animation skill
                else:
                    action[0] = "Skill_" + action[0]
                self.command_action = {"name": action[0], "skill": skill}
                self.available_skill.remove(skill)
                if len(action) > 1:
                    self.command_action |= {this_prop: True for this_prop in action[1:]}
                if "hold" in self.command_action or "repeat" in self.command_action:
                    self.idle_action = self.command_action
            else:
                self.command_action = {}

