import random


def cal_range_hit(self, attacker, target, target_side, side_percent=(1, 0.3, 0.3, 0)):
    """Calculate range attack hit chance and defence chance, side_percent is more punishing than melee attack"""
    attacker_luck = random.randint(-20, 20)  # luck of the attacker subunit
    target_luck = random.randint(-20, 20)  # luck of the defender subunit

    target_percent = side_percent[target_side]  # side penalty
    if target.check_special_effect("All Side Full Defence"):
        target_percent = 1  # no side penalty for all round defend
    attacker_hit = float(self.accuracy) + attacker_luck  # calculate hit chance
    if attacker_hit < 0:
        attacker_hit = 0  # hit_chance cannot be negative

    target_def = float(target.range_def * target_percent) + target_luck  # calculate defence
    if target_def < 0:
        target_def = 0  # defence cannot be negative

    attacker_dmg, attacker_morale_dmg, element_effect, self.penetrate = \
        self.cal_dmg(attacker, target, attacker_hit, target_def, self.weapon, self.penetrate, self)

    self.attacker.cal_loss(target, attacker_dmg, attacker_morale_dmg, element_effect)
