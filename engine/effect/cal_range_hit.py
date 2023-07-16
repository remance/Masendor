from random import randint, uniform

combat_side_cal = (1, 0.3, 0.1)  # for range attack target defend side modifier 0 = Front, 1 = Side, 2 = Rear


def cal_range_hit(self, target, target_side, hit_angle):
    """Calculate range attack hit chance and defence chance, then damage"""
    attacker_luck = uniform(0.8, 1.2)  # attacker luck
    target_dodge_luck = uniform(0.7, 1.1)  # luck of the defender unit

    # calculate hit chance with height advantage being less than melee since range attack can have more difference
    attacker_hit = self.accuracy + attacker_luck + (
            self.attacker.height - target.height) / 2
    if attacker_hit < 0:
        attacker_hit = 0  # hit_chance cannot be negative

    if attacker_hit > randint(0, 50):  # attack land, now check if target can dodge
        hit_side_mod = combat_side_cal[target_side]  # side penalty
        target_dodge = (target.range_dodge * target_dodge_luck) * hit_side_mod  # calculate defence
        if target_dodge < 0:
            target_dodge = 0  # cannot be negative
        if target_dodge < 0:
            target_dodge = 0  # cannot be negative

        hit_chance = attacker_hit - target_dodge  # chance to hit
        if hit_chance < 10:  # no less than 10 % chance to hit
            hit_chance = 10
        elif hit_chance > 90:  # no more than 90% chance to hit
            hit_chance = 90

        if hit_chance > randint(0, 100):  # not miss, now cal def and dmg
            target_def_luck = uniform(0.7, 1.1)  # luck of the defender unit
            if target.check_special_effect("All Side Full Defence"):
                hit_side_mod = 1  # no side penalty for all round defend

            target_def = (target.range_def * target_def_luck) * hit_side_mod  # calculate defence
            if target_def < 0:
                target_def = 0  # cannot be negative

            attacker_dmg, attacker_morale_dmg, element_effect, impact = \
                self.cal_dmg(target, attacker_hit, target_def, self.weapon)

            target.cal_loss(attacker_dmg, impact, attacker_morale_dmg, element_effect, hit_angle)

            target.take_range_dmg = 3
