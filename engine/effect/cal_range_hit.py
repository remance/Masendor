from random import randint

combat_side_cal = (1, 0.3, 0.3, 0)  # for range side that hit target modifier


def cal_range_hit(self, target, target_side, hit_angle):
    """Calculate range attack hit chance and defence chance, side_percent is more punishing than melee attack"""
    attacker_luck = randint(-20, 20)  # luck of the attacker unit
    target_def_luck = randint(-20, 20)  # luck of the defender unit
    target_dodge_luck = randint(-30, 30)  # luck of the defender unit

    attacker_hit = self.accuracy + attacker_luck + (
            self.attacker.height - target.height) / 2  # calculate hit chance with height advantage
    if attacker_hit < 0:
        attacker_hit = 0  # hit_chance cannot be negative

    if attacker_hit > randint(0, 50):  # attack land, now check if target can dodge
        hit_side_mod = combat_side_cal[target_side]  # side penalty
        target_dodge = (target.melee_dodge * hit_side_mod) + target_dodge_luck  # calculate defence
        if target_dodge < 0:
            target_dodge = 0  # cannot be negative

        hit_chance = attacker_hit - target_dodge

        if hit_chance > 100 or hit_chance > randint(0, 100):  # not dodge, now cal def and dmg
            if target.check_special_effect("All Side Full Defence"):
                hit_side_mod = 1  # no side penalty for all round defend

            target_def = (target.range_def * hit_side_mod) + target_def_luck  # calculate defence
            if target_def < 0:
                target_def = 0  # cannot be negative

            attacker_dmg, attacker_morale_dmg, element_effect, impact = \
                self.cal_dmg(target, attacker_hit, target_def, self.weapon)

            target.cal_loss(attacker_dmg, impact, attacker_morale_dmg, element_effect, hit_angle)

            target.take_range_dmg = 3
