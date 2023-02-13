def use_skill(self, which_skill):
    skill_stat = self.skill[which_skill]
    aoe = skill_stat["Area of Effect"]

    group_to_do = []
    if skill_stat["Type"] in (0, 2):
        group_to_do.append(self.near_ally)
        self.apply_effect(which_skill, skill_stat, self.skill_effect, self.skill_duration)
    if skill_stat["Type"] in (1, 2):
        group_to_do.append(self.near_enemy)

    if aoe > 1:
        for group in group_to_do:
            for subunit in group:
                if aoe >= subunit[1]:  # only apply to exist and alive
                    subunit[0].apply_effect(which_skill, skill_stat, subunit[0].skill_effect, subunit[0].skill_duration)

                    if self.team == subunit[0].team:  # apply status to friend if there is one in skill effect
                        for status in skill_stat["Status"]:
                            subunit[0].apply_effect(status, self.status_list[status],
                                                    subunit[0].status_effect, subunit[0].status_duration)
                    if self.team != subunit[0].team:  # apply status to enemy if there is one in skill effect
                        for status in skill_stat["Enemy Status"]:
                            subunit[0].apply_effect(status, self.status_list[status],
                                                    subunit[0].status_effect, subunit[0].status_duration)
                else:  # exceed distance from this subunit onward in list
                    break

    self.skill_cooldown[which_skill] = skill_stat["Cooldown"]  # add skill cooldown
    self.stamina -= skill_stat["Stamina Cost"]
