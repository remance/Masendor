def check_line_of_sight(self, target_pos):
    clip_friend = False
    for this_unit in self.battle.all_team_unit[self.team]:
        for this_subunit in this_unit.alive_subunit_list:
            if this_subunit != self:
                clip = this_subunit.hitbox_rect.clipline(target_pos, self.base_pos)
                if clip:
                    if self.player_manual_control:
                        print(clip, this_subunit.game_id, this_unit.name, this_subunit.base_pos)
                    clip_friend = True
                    break
    return clip_friend
