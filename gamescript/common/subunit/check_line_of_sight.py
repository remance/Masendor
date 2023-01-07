def check_line_of_sight(self):
    clip_friend = False
    for subunit in self.battle.subunit_list[self.team]:  # Check if line of sight collide with any friendly subunit
        clip = subunit.dmg_rect.clipline(self.attack_pos, self.base_pos)
        if len(clip) > 0:
            clip_friend = True
            break
    return clip_friend
