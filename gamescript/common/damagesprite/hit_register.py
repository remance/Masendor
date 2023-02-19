def hit_register(self, subunit=None):
    """Calculate hit and damage"""
    if subunit:
        if self.aoe:  # aoe angle use pos instead
            hit_angle = self.set_rotate(subunit.base_pos)
        else:
            hit_angle = self.angle
        angle_check = abs(hit_angle - subunit.angle)  # calculate which side damage sprite hit the subunit
        if angle_check >= 135:  # front
            hit_side = 0
        elif angle_check >= 45:  # side
            hit_side = 1
        else:  # rear
            hit_side = 2
        # calculate damage

        if self.attack_type == "range":
            self.cal_range_hit(self.attacker, subunit, hit_side, hit_angle)
        else:
            self.cal_melee_hit(self.attacker, self.weapon, subunit, hit_side, hit_angle)
