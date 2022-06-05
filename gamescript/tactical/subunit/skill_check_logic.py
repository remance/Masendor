import random


def skill_check_logic(self):
    if self.skill_cond != 3:  # any skill condition behaviour beside 3 (forbid skill) will check available skill to use
        if self.skill_cond == 1 and self.stamina_state < 50:  # reserve 50% stamina, don't use any skill
            self.available_skill = []
        elif self.skill_cond == 2 and self.stamina_state < 25:  # reserve 25% stamina, don't use any skill
            self.available_skill = []
        else:  # check all skill for cooldown, condition state, discipline, stamina are checked. charge skill is excepted from this check"""
            self.available_skill = [skill for skill in self.skill if skill not in self.skill_cooldown.keys()
                                    and self.state in self.skill[skill]["Condition"] and self.discipline >=
                                    self.skill[skill]["Discipline Requirement"]
                                    and self.stamina > self.skill[skill]["Stamina Cost"] and skill != 0]

    if len(self.available_skill) > 0 and random.randint(0, 10) >= 6:  # random chance to use random available skill
        self.use_skill(self.available_skill[random.randint(0, len(self.available_skill) - 1)])
