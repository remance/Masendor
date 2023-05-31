from random import choice

from pygame import Vector2

from engine.effect.effect import Effect


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
                Effect(self, base_pos, pos, skill_stat["Effect Sprite"][0],
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
            for this_unit in group:
                if skill_stat["Range"]:
                    distance = this_unit[0].base_pos.distance_to(self.current_action["pos"])
                    use_center = False
                else:  # use center of unit for calculation distance of aoe skill
                    distance = this_unit[1]
                    use_center = True
                if aoe >= distance:
                    this_unit[0].apply_effect(which_skill, skill_stat, this_unit[0].skill_effect,
                                              this_unit[0].skill_duration)

                    if self.team == this_unit[0].team:  # apply status to friend if there is one in skill effect
                        for status in skill_stat["Status"]:
                            this_unit[0].apply_effect(status, self.status_list[status],
                                                      this_unit[0].status_effect, this_unit[0].status_duration)
                    if self.team != this_unit[0].team:  # apply status to enemy if tfhere is one in skill effect
                        for status in skill_stat["Enemy Status"]:
                            this_unit[0].apply_effect(status, self.status_list[status],
                                                      this_unit[0].status_effect, this_unit[0].status_duration)
                    if "Action" in skill_stat["Action Type"]:  # effect that is use only when unit perform attack
                        if "Melee" in skill_stat["Action Type"] and which_skill not in this_unit[0].active_action_skill[
                            "melee"]:
                            this_unit[0].active_action_skill["melee"].append(which_skill)
                        elif "Range" in skill_stat["Action Type"] and which_skill not in \
                                this_unit[0].active_action_skill[
                                    "range"]:
                            this_unit[0].active_action_skill["range"].append(which_skill)

                elif use_center:  # exceed distance from this unit pos center onward in list
                    break

        self.skill_cooldown[which_skill] = skill_stat["Cooldown"]  # add skill cooldown
        self.stamina -= skill_stat["Stamina Cost"]
