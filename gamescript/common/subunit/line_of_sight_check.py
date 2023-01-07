def line_of_sight_check(self):
    for subunit in self.battle.subunit_list[self.team]:  # Check if line of sight collide with any friendly subunit
        clip = subunit.rect.clipline(self.attack_pos, self.base_pos)
    return clip
