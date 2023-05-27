def hit_register(self, unit):
    """Calculate hit and damage"""
    if self.aoe:  # aoe angle use pos instead
        hit_angle = self.set_rotate(unit.base_pos)
    else:
        hit_angle = self.angle
    angle_check = abs(hit_angle - unit.angle)  # calculate which side damage sprite hit the unit
    if angle_check >= 135:  # front
        hit_side = 0
    elif angle_check >= 45:  # side
        hit_side = 1
    else:  # rear
        hit_side = 2

    # calculate damage
    if self.attack_type == "range":
        self.cal_range_hit(self.attacker, unit, hit_side, hit_angle)
    elif self.attack_type == "effect":
        self.cal_effect_hit(unit, hit_angle)
    elif self.attack_type == "charge":
        self.cal_charge_hit(self.attacker, unit, hit_side, hit_angle)
    else:
        self.cal_melee_hit(self.attacker, self.weapon, unit, hit_side, hit_angle)
