import random

combat_side_cal = (1, 0.4, 0.1, 0.4)  # for melee combat side modifier
infinity = float("inf")


def cal_melee_hit(self, attacker, weapon, target, hit_side, hit_angle):
    """base_target position 0 = Front, 1 = Side, 3 = Rear,
    attacker_side and target_side is the side attacking and defending respectively"""
    attacker_luck = random.randint(-50, 20)  # attacker luck
    target_dodge_luck = random.randint(-30, 30)  # luck of the defender subunit

    hit_side_mod = combat_side_cal[hit_side]  # defender defend side

    attacker_hit = attacker.melee_attack + attacker_luck + (attacker.height - target.height)
    target_dodge = (target.melee_dodge * hit_side_mod) + target_dodge_luck  # calculate defence
    if target_dodge < 0:
        target_dodge = 0  # cannot be negative

    hit_chance = attacker_hit - target_dodge

    if hit_chance > 100 or hit_chance > random.randint(0, 100):  # not miss, now cal def and dmg
        if target.check_special_effect("All Side Full Defence"):
            hit_side_mod = 1

        target_def_luck = random.randint(-20, 20)  # luck of the defender subunit
        target_defence = (target.melee_def * hit_side_mod) + target_def_luck

        if target_defence < 0 or (attacker.check_special_effect("Rear Attack Bonus") and hit_side == 2) or \
                (attacker.check_special_effect("No Rear Defence") and hit_side == 2) or \
                (attacker.check_special_effect("Flank Attack Bonus") and hit_side in (1, 3)):
            target_defence = 0

        attacker_dmg, attacker_morale_dmg, element_effect, impact = self.cal_dmg(attacker, target, attacker_hit,
                                                                                 target_defence,
                                                                                 weapon, hit_side=hit_side)

        attacker.cal_loss(target, attacker_dmg, impact, attacker_morale_dmg, element_effect, hit_angle)  # inflict dmg to defender

        if attacker.check_special_effect("Reflect Damage"):
            target_dmg = attacker_dmg / 10
            target_morale_dmg = attacker_dmg / 50
            if target.full_reflect:
                target_dmg = attacker_dmg
                target_morale_dmg = attacker_dmg / 10
            target.cal_loss(attacker, target_dmg, target_morale_dmg, element_effect, hit_angle)  # inflict dmg to attacker
