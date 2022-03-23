def use_skill(self, which_skill):
    if which_skill == 0:  # charge skill need to separate since charge power will be used only for charge skill
        skill_stat = self.skill[list(self.skill)[0]].copy()  # get skill stat
        self.skill_effect[self.charge_skill] = skill_stat  # add stat to skill effect
        self.skill_cooldown[self.charge_skill] = skill_stat["Cooldown"]  # add skill cooldown
    else:  # other skill
        skill_stat = self.skill[which_skill].copy()  # get skill stat
        self.skill_effect[which_skill] = skill_stat  # add stat to skill effect
        self.skill_cooldown[which_skill] = skill_stat["Cooldown"]  # add skill cooldown
    self.stamina -= skill_stat["Stamina Cost"]
    # self.skill_cooldown[which_skill] =


def check_skill_condition(self):
    """Check which skill can be used, cooldown, condition state, discipline, stamina are checked.
    charge skill is excepted from this check"""
    if self.skill_cond == 1 and self.stamina_state < 50:  # reserve 50% stamina, don't use any skill
        self.available_skill = []
    elif self.skill_cond == 2 and self.stamina_state < 25:  # reserve 25% stamina, don't use any skill
        self.available_skill = []
    else:  # check all skill
        self.available_skill = [skill for skill in self.skill if skill not in self.skill_cooldown.keys()
                                and self.state in self.skill[skill]["Condition"] and self.discipline >=
                                self.skill[skill][
                                    "Discipline Requirement"]
                                and self.stamina > self.skill[skill]["Stamina Cost"] and skill != self.charge_skill]
