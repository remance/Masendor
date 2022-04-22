def use_skill(self, which_skill):
    skill_stat = self.skill[which_skill].copy()  # get skill stat
    self.skill_effect[which_skill] = skill_stat  # add stat to skill effect
    self.skill_cooldown[which_skill] = skill_stat["Cooldown"]  # add skill cooldown
    self.stamina -= skill_stat["Stamina Cost"]

