from random import randint, uniform

combat_side_cal = (1, 0.5, 0.1)  # for melee attack target defend side modifier 0 = Front, 1 = Side, 2 = Rear
infinity = float("inf")


def cal_melee_hit(self, target, hit_side, hit_angle):
    """Calculate melee attack hit chance and defence chance, then damage"""
    attacker_luck = uniform(0.4, 1)  # attacker luck
    target_dodge_luck = uniform(0.6, 1)  # luck of the defender unit

    hit_side_mod = combat_side_cal[hit_side]  # defender defend side

    attacker_hit = (self.accuracy * attacker_luck) + (self.attacker.height - target.height)
    target_dodge = (target.melee_dodge * target_dodge_luck) * hit_side_mod  # calculate defence
    if target_dodge < 0:
        target_dodge = 0  # cannot be negative

    hit_chance = attacker_hit - target_dodge  # chance to hit
    if hit_chance < 10:  # no less than 10 % chance to hit
        hit_chance = 10
    elif hit_chance > 90:  # no more than 90% chance to hit
        hit_chance = 90

    if hit_chance > randint(0, 100):  # not miss, now cal def and dmg
        if target.check_special_effect("All Side Full Defence"):
            hit_side_mod = 1

        target_def_luck = uniform(0.7, 1.1)  # luck of the defender unit
        target_defence = (target.melee_def * target_def_luck) * hit_side_mod

        if target_defence < 0 or (self.attacker.check_special_effect("Rear Attack Bonus") and hit_side == 2) or \
                (self.attacker.check_special_effect("No Rear Defence") and hit_side == 2) or \
                (self.attacker.check_special_effect("Flank Attack Bonus") and hit_side in (1, 3)):
            target_defence = 0

        attacker_dmg, attacker_morale_dmg, element_effect, impact = self.cal_dmg(target, attacker_hit,
                                                                                 target_defence,
                                                                                 self.weapon, hit_side=hit_side)

        target.cal_loss(attacker_dmg, impact, attacker_morale_dmg, element_effect, hit_angle)  # inflict dmg to defender
        target.take_melee_dmg = 3  # start defender taking melee timer

        if self.attacker.check_special_effect("Reflect Damage"):
            target_dmg = attacker_dmg / 10
            target_morale_dmg = attacker_dmg / 50
            if target.full_reflect:
                target_dmg = attacker_dmg
                target_morale_dmg = attacker_dmg / 10
            self.attacker.cal_loss(target_dmg, target_morale_dmg, element_effect, hit_angle)  # reflect dmg to attacker
