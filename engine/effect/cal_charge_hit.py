from random import randint

combat_side_cal = (1, 0.4, 0.1, 0.4)  # for melee combat side modifier
infinity = float("inf")


def cal_charge_hit(self, target, hit_side, hit_angle):
    """base_target position 0 = Front, 1 = Side, 3 = Rear,
    attacker_side and target_side is the side attacking and defending respectively"""
    attacker_luck = randint(-50, 20)  # attacker luck
    target_dodge_luck = randint(-30, 30)  # luck of the defender unit

    hit_side_mod = combat_side_cal[hit_side]  # defender defend side

    attacker_hit = self.attacker.melee_attack + attacker_luck + (self.attacker.height - target.height)
    target_dodge = (target.melee_dodge * hit_side_mod) + target_dodge_luck  # calculate defence
    if target_dodge < 0:
        target_dodge = 0  # cannot be negative

    hit_chance = attacker_hit - target_dodge

    if hit_chance > 100 or hit_chance > randint(0, 100):  # not miss, now cal def and dmg
        if target.check_special_effect("All Side Full Defence"):
            hit_side_mod = 1

        target_def_luck = randint(-20, 20)  # luck of the defender unit
        target_defence = (target.melee_def * hit_side_mod) + target_def_luck

        if target_defence < 0 or (self.attacker.check_special_effect("Rear Attack Bonus") and hit_side == 2) or \
                (self.attacker.check_special_effect("No Rear Defence") and hit_side == 2) or \
                (self.attacker.check_special_effect("Flank Attack Bonus") and hit_side in (1, 3)):
            target_defence = 0

        attacker_dmg, attacker_morale_dmg, element_effect, impact = self.cal_dmg(target, attacker_hit,
                                                                                 target_defence, None,
                                                                                 hit_side=hit_side)

        target.cal_loss(attacker_dmg, impact, attacker_morale_dmg, element_effect, hit_angle)  # inflict dmg to defender
        target.take_melee_dmg = 3

        if self.attacker.check_special_effect("Reflect Damage"):
            target_dmg = attacker_dmg / 2
            target_morale_dmg = attacker_dmg / 50
            if target.full_reflect:
                target_dmg = attacker_dmg
                target_morale_dmg = attacker_dmg / 10
            self.attacker.cal_loss(target_dmg, target_morale_dmg, element_effect, hit_angle)  # inflict dmg to attacker
