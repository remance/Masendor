from random import randint

combat_side_cal = (1, 0.3, 0.3, 0)  # for range side that hit target modifier


def cal_range_hit(self, attacker, target, target_side, hit_angle):
    """Calculate range attack hit chance and defence chance, side_percent is more punishing than melee attack"""
    attacker_luck = randint(-20, 20)  # luck of the attacker subunit
    target_def_luck = randint(-20, 20)  # luck of the defender subunit
    target_dodge_luck = randint(-30, 30)  # luck of the defender subunit

    attacker_hit = self.accuracy + attacker_luck + (attacker.height - target.height) / 2  # calculate hit chance with height advantage
    if attacker_hit < 0:
        attacker_hit = 0  # hit_chance cannot be negative

    hit_side_mod = combat_side_cal[target_side]  # side penalty
    target_dodge = (target.melee_dodge * hit_side_mod) + target_dodge_luck  # calculate defence
    if target_dodge < 0:
        target_dodge = 0  # cannot be negative

    hit_chance = attacker_hit - target_dodge

    if hit_chance > 100 or hit_chance > randint(0, 100):  # not miss, now cal def and dmg
        if target.check_special_effect("All Side Full Defence"):
            hit_side_mod = 1  # no side penalty for all round defend

        target_def = (target.range_def * hit_side_mod) + target_def_luck  # calculate defence
        if target_def < 0:
            target_def = 0  # cannot be negative

        target_dodge = (target.range_dodge * hit_side_mod) + target_dodge_luck  # calculate defence
        if target_dodge < 0:
            target_dodge = 0  # cannot be negative

        attacker_dmg, attacker_morale_dmg, element_effect, impact = \
            self.cal_dmg(attacker, target, attacker_hit, target_def, self.weapon)

        self.attacker.cal_loss(target, attacker_dmg, impact, attacker_morale_dmg, element_effect, hit_angle)

        target.take_range_dmg = 3
