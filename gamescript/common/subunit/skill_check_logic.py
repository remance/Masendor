def skill_check_logic(self):
    # Check which skill can be used, cooldown, discipline, stamina are checked. charge skill is excepted from this check
    if self.not_broken:
        self.available_skill = [skill for skill in self.skill if skill not in self.skill_cooldown.keys()
                                and self.discipline >= self.skill[skill]["Discipline Requirement"]
                                and self.stamina > self.skill[skill]["Stamina Cost"] and skill != self.charge_skill]
        if self.command_action and self.available_skill:  # no current action and has skill command waiting
            command_action = self.command_action["name"]
            if "Skill" in command_action:  # use skill and convert command action into skill action name
                if "Charge" in command_action:
                    action = self.skill[self.charge_skill]["Action"].copy()
                    weapon = int(command_action[-1])
                    action[0] = ("Main_", "Sub_")[weapon] + self.action_list[weapon]["Common"] + "_" + \
                                action[0]
                    self.command_action = {"name": action[0]} | {key: True for key in action[1:]}
                else:
                    skill = int(self.command_action["name"][-1])
                    skill_command = None
                    action = None
                    if "Weapon" in command_action:  # weapon skill
                        skill = self.weapon_skill[self.equipped_weapon][
                            skill]  # TODO check if this work properly for leader
                        if skill != 0:
                            skill_command = skill
                            action = self.skill[skill]["Action"].copy() + [skill]
                            action[0] += " " + command_action[-1]
                    else:  # self skill
                        if len(self.skill) > skill:
                            skill = self.troop_skill[skill]
                            action = self.skill[skill]["Action"].copy() + [skill]
                        if action is not None:
                            if "Action" in action[0]:
                                action[0] += " 0"  # use main hand by default for Action type animation skill
                            else:
                                action[0] = "_Skill_" + action[0]

                    if skill != 0 and skill in self.available_skill:
                        self.skill_effect = {}  # arcade mode allows only 1 skill active at a time
                        self.use_skill(skill)
                        self.command_action = {"name": action[0]} | {key: True for key in action[1:]}
                        if skill_command is not None:
                            self.command_action["skill"] = skill
                        if "hold" in self.command_action or "repeat" in self.command_action:
                            self.idle_action = self.command_action
                        self.input_delay = 1
                    else:
                        self.command_action = {}
