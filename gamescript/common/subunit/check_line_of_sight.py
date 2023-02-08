def check_line_of_sight(self, target_pos):
    clip_friend = False
    for this_subunit in self.battle.all_team_subunit[self.team]:
        if this_subunit != self:
            clip = this_subunit.rect.clipline(target_pos, self.base_pos)
            if clip:
                clip_friend = True
                break
    return clip_friend
