from random import choice

from gamescript import effectsprite


def use_skill(self, which_skill):
    skill_stat = self.skill[which_skill]
    aoe = skill_stat["Area of Effect"]

    if self.current_animation[self.show_frame]["dmg_sprite"] and which_skill != self.charge_skill:
        effectsprite.EffectSprite(self, self.base_pos, self.pos, self.pos, 0, 0, skill_stat["Effect Sprite"],
                                  self.current_animation[self.show_frame]["dmg_sprite"])
    if skill_stat["Sound Effect"] in self.sound_effect_pool:  # add attack sound to playlist
        self.battle.add_sound_effect_queue(choice(self.sound_effect_pool[skill_stat["Sound Effect"]]),
                                           self.base_pos, skill_stat["Sound Distance"],
                                           skill_stat["Shake Power"])

    if skill_stat["Receiver"] in (0, 2):
        self.apply_effect(which_skill, skill_stat, self.skill_effect, self.skill_duration)

    if aoe > 1:
        group_to_do = []
        if skill_stat["Receiver"] in (0, 2):
            group_to_do.append(self.near_ally)
        if skill_stat["Receiver"] in (1, 2):
            group_to_do.append(self.near_enemy)
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
