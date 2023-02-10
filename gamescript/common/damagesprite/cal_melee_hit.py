import random

combat_side_cal = (1, 0.4, 0.1, 0.4)  # for melee combat side modifier
infinity = float("inf")


def cal_melee_hit(self, attacker, weapon, target, hit_side):
    """base_target position 0 = Front, 1 = Side, 3 = Rear, attacker_side and target_side is the side attacking and defending respectively"""
    attacker_luck = random.randint(-50, 20)  # attacker luck
    target_luck = random.randint(-20, 30)  # defender luck

    hit_side_mod = combat_side_cal[hit_side]  # defender defend side
    if attacker.check_special_effect("All Side Full Defence", weapon=weapon):
        hit_side_mod = 1


    attacker_hit = attacker.melee_attack + attacker_luck
    target_defence = float(target.melee_def * hit_side_mod) + target_luck

    if (attacker.check_special_effect("Rear Attack Bonus") and hit_side == 2) or \
            (attacker.check_special_effect("No Rear Defence") and hit_side == 2) or \
            (attacker.check_special_effect("Flank Attack Bonus") and hit_side in (
            1, 3)):
        target_defence = 0

    attacker_dmg, attacker_morale_dmg, element_effect, self.penetrate = self.cal_dmg(attacker, target, attacker_hit,
                                                                                     target_defence, weapon,
                                                                                     self.penetrate, hit_side=hit_side)

    attacker.cal_loss(target, attacker_dmg, attacker_morale_dmg, element_effect)  # inflict dmg to defender

    if attacker.check_special_effect("Reflect Damage"):
        target_dmg = attacker_dmg / 10
        target_morale_dmg = attacker_dmg / 50
        if target.full_reflect:
            target_dmg = attacker_dmg
            target_morale_dmg = attacker_dmg / 10
        target.cal_loss(attacker, target_dmg, target_morale_dmg, element_effect)  # inflict dmg to attacker


def apply_status_to_enemy(inflict_status, target, attacker_side, receiver_side):
    """apply aoe status effect to enemy subunits"""
    for status in inflict_status.items():
        if status[1] == 1 and attacker_side == 0:  # only front enemy
            target.apply_effect(status[0], target.status_list, target.status_effect, target.status_duration)
        elif status[1] >= 2:  # aoe effect to side enemy
            target.apply_effect(status[0], target.status_list, target.status_effect, target.status_duration)
            if status[1] == 3:  # apply to corner enemy subunit (left and right of self front enemy subunit)
                corner_enemy_apply = target.nearby_subunit_list[0:2]
                if receiver_side in (
                1, 2):  # attack on left/right side means corner enemy would be from front and rear side of the enemy
                    corner_enemy_apply = [target.nearby_subunit_list[2], target.nearby_subunit_list[5]]
                for this_subunit in corner_enemy_apply:
                    if this_subunit != 0:
                        this_subunit.apply_effect(status[0], this_subunit.status_list, this_subunit.status_effect,
                                                  this_subunit.status_duration)
            elif status[1] == 4:  # whole unit aoe
                for this_subunit in target.unit.alive_subunit_list:
                    this_subunit.apply_effect(status[0], this_subunit.status_list, this_subunit.status_effect,
                                              this_subunit.status_duration)
