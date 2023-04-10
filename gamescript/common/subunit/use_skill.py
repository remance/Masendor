from random import choice

from pygame import Vector2

from gamescript import effectsprite


def use_skill(self, which_skill):
    if which_skill in self.skill:
        skill_stat = self.skill[which_skill]
        aoe = skill_stat["Area Of Effect"]

        if which_skill != self.charge_skill and "weapon" not in self.current_action:
            base_pos = self.base_pos
            pos = self.pos
            if "pos" in self.current_action:
                base_pos = self.current_action["pos"]
                pos = Vector2(base_pos[0] * self.screen_scale[0], base_pos[1] * self.screen_scale[1]) * 5
            if skill_stat["Effect Sprite"]:
                effectsprite.EffectSprite(self, base_pos, pos, pos, skill_stat["Effect Sprite"][0],
                                          skill_stat["Effect Sprite"][1])
            if skill_stat["Sound Effect"] in self.sound_effect_pool:  # add attack sound to playlist
                self.battle.add_sound_effect_queue(choice(self.sound_effect_pool[skill_stat["Sound Effect"]]),
                                                   base_pos, skill_stat["Sound Distance"],
                                                   skill_stat["Shake Power"])

        group_to_do = []
        if skill_stat["Receiver"] in (0, 2):
            if aoe > 1 or skill_stat["Range"]:  # skill that can target somewhere or has aoe, add friend to check
                group_to_do.append(self.near_ally)
            group_to_do.append(((self, 0),))
        if skill_stat["Receiver"] in (1, 2):
            group_to_do.append(self.near_enemy)

        for group in group_to_do:
            for subunit in group:
                if skill_stat["Range"]:
                    distance = subunit[0].base_pos.distance_to(self.current_action["pos"])
                    use_center = False
                else:  # use center of subunit for calculation distance of aoe skill
                    distance = subunit[1]
                    use_center = True
                if aoe >= distance:
                    subunit[0].apply_effect(which_skill, skill_stat, subunit[0].skill_effect,
                                            subunit[0].skill_duration)

                    if self.team == subunit[0].team:  # apply status to friend if there is one in skill effect
                        for status in skill_stat["Status"]:
                            subunit[0].apply_effect(status, self.status_list[status],
                                                    subunit[0].status_effect, subunit[0].status_duration)
                    if self.team != subunit[0].team:  # apply status to enemy if there is one in skill effect
                        for status in skill_stat["Enemy Status"]:
                            subunit[0].apply_effect(status, self.status_list[status],
                                                    subunit[0].status_effect, subunit[0].status_duration)
                    if "Action" in skill_stat["Type"]:  # effect that is use only when subunit perform attack
                        if "Melee" in skill_stat["Type"] and which_skill not in subunit[0].active_action_skill["melee"]:
                            subunit[0].active_action_skill["melee"].append(which_skill)
                        elif "Range" in skill_stat["Type"] and which_skill not in subunit[0].active_action_skill[
                            "range"]:
                            subunit[0].active_action_skill["range"].append(which_skill)

                elif use_center:  # exceed distance from this subunit pos center onward in list
                    break

        self.skill_cooldown[which_skill] = skill_stat["Cooldown"]  # add skill cooldown
        self.stamina -= skill_stat["Stamina Cost"]
