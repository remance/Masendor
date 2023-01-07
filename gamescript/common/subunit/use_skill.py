def use_skill(self, which_skill):
    skill_stat = self.skill[which_skill]
    self.apply_effect(which_skill, self.skill, self.skill_effect, self.skill_duration)
    self.skill_cooldown[which_skill] = skill_stat["Cooldown"]  # add skill cooldown
    self.stamina -= skill_stat["Stamina Cost"]
