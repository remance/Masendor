def skill_check_logic(self):
    # Check which skill can be used, cooldown, discipline, stamina are checked. charge skill is excepted from this check
    if self.not_broken and "uncontrollable" not in self.current_action:
        if self.momentum == 1 and self.current_action and "Charge" in self.current_action["name"]:  # use charge skill when momentum reach 1
            self.use_skill(self.charge_skill)
        elif self.command_action and "Skill" in self.command_action["name"]:
            available_skill = [skill for skill in self.skill if skill not in self.skill_cooldown.keys()
                               and self.discipline >= self.skill[skill]["Discipline Requirement"]
                               and self.stamina > self.skill[skill]["Stamina Cost"] and skill != self.charge_skill]
            if available_skill:  # no current action and has skill command waiting
                command_action = self.command_action["name"]
                if "Skill" in command_action:  # use skill and convert command action into skill action name
                    skill = int(self.command_action["name"][-1])
                    if len(self.skill) > skill:
                        skill = tuple(self.skill.keys())[skill]
                        if skill in available_skill:
                            self.use_skill(skill)
                            action = self.skill[skill]["Action"].copy() + [skill]
                            if "Action" in action[0]:
                                action[0] += " 0"  # use main hand by default for Action type animation skill
                            else:
                                action[0] = "Skill_" + action[0]
                            self.command_action = {"name": action[0], "skill": skill}
                            if "hold" in self.command_action or "repeat" in self.command_action:
                                self.idle_action = self.command_action
                            self.input_delay = 1
                        else:
                            self.command_action = {}
            else:
                self.command_action = {}
