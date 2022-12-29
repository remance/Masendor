def hit_register(self, subunit=None):
    """Calculate hit and damage"""
    if subunit is not None:
        angle_check = abs(self.angle - subunit.angle)  # calculate which side damage sprite hit the subunit
        if angle_check >= 135:  # front
            hit_side = 0
        elif angle_check >= 45:  # side
            hit_side = 1
        else:  # rear
            hit_side = 2
        # calculate damage
        if self.attack_type == "range":
            self.range_dmg_cal(self.attacker, subunit, hit_side)
        elif self.attack_type == "melee":  # use attacker hit register instead
            self.attacker.hit_register(self.weapon, subunit, 0, hit_side,
                                       self.attacker.battle.troop_data.status_list)
