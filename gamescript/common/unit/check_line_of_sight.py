def check_line_of_sight(self, target_pos):
    for this_unit in self.battle.all_team_unit[self.team]:
        if this_unit != self:
            clip = this_unit.hitbox.rect.clipline(target_pos, self.base_pos)
            if clip:
                return True
    return False
