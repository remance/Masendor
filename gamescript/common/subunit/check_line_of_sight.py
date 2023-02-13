def check_line_of_sight(self, target_pos):
    for this_subunit in self.battle.all_team_subunit[self.team]:
        if this_subunit != self:
            clip = this_subunit.hitbox.rect.clipline(target_pos, self.base_pos)
            if clip:
                return True
    return False
