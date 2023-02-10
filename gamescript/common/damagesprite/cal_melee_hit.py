import random

combat_side_cal = (1, 0.4, 0.1, 0.4)  # for melee combat side modifier
infinity = float("inf")


def cal_melee_hit(self, attacker, weapon, target, attacker_side, hit_side):
    """base_target position 0 = Front, 1 = Side, 3 = Rear, attacker_side and target_side is the side attacking and defending respectively"""
    attacker_luck = random.randint(-50, 20)  # attacker luck
    target_luck = random.randint(-20, 30)  # defender luck
    attacker_side_mod = combat_side_cal[attacker_side]  # attacker attack side modifier

    if attacker.check_special_effect("All Side Full Attack"):
        attacker_side_mod = 1

    hit_side_mod = combat_side_cal[hit_side]  # defender defend side
    if attacker.check_special_effect("All Side Full Defence", weapon=weapon):
        hit_side_mod = 1

    if attacker_side != 0 and attacker_side_mod != 1:  # if attack or defend from side will use discipline to help reduce penalty a bit
        attacker_side_mod += (attacker.discipline / 300)
        if attacker_side_mod > 1:
            attacker_side_mod = 1

    if hit_side != 0 and hit_side_mod != 1:  # same for the base_target defender
        hit_side_mod += (target.discipline / 300)
        if hit_side_mod > 1:
            hit_side_mod = 1

    attacker_hit = float(attacker.melee_attack * attacker_side_mod) + attacker_luck
    target_defence = float(target.melee_def * hit_side_mod) + target_luck

    if (attacker.check_special_effect("Rear Attack Bonus") and hit_side == 2) or \
            (attacker.check_special_effect("No Rear Defence") and hit_side == 2) or \
            (attacker.check_special_effect("Flank Attack Bonus") and attacker_side in (
            1, 3)):  # apply only for attacker
        target_defence = 0

    attacker_dmg, attacker_morale_dmg, attacker_leader_dmg, \
    element_effect, _ = attacker.cal_dmg(target, attacker_hit, target_defence, weapon,
                                         attacker.weapon_penetrate[attacker.equipped_weapon][weapon], weapon,
                                         hit_side)  # get dmg by attacker

    attacker.cal_loss(target, attacker_dmg, attacker_morale_dmg, attacker_leader_dmg,
                      element_effect)  # inflict dmg to defender

    if attacker.check_special_effect("Reflect Damage"):
        target_dmg = attacker_dmg / 10
        target_morale_dmg = attacker_dmg / 50
        if target.full_reflect:
            target_dmg = attacker_dmg
            target_morale_dmg = attacker_dmg / 10
        target.cal_loss(attacker, target_dmg, target_morale_dmg, element_effect)  # inflict dmg to attacker

    # Attack corner (side) of self with aoe attack
    if attacker.corner_atk:
        loop_list = [target.nearby_subunit_list[2],
                     target.nearby_subunit_list[5]]  # Side attack get (2) front and (5) rear nearby subunit
        if hit_side in (0, 2):
            loop_list = target.nearby_subunit_list[0:2]  # Front/rear attack get (0) left and (1) right nearby subunit
        for this_subunit in loop_list:
            if this_subunit != 0 and this_subunit.alive:
                target_hit, target_defence = float(attacker.melee_attack * hit_side_mod) + target_luck, float(
                    this_subunit.melee_def * hit_side_mod) + target_luck
                attacker_dmg, attacker_morale_dmg, element_effect, _ = \
                    attacker.cal_dmg(this_subunit, attacker_hit, target_defence, weapon,
                                     attacker.weapon_penetrate[attacker.equipped_weapon][weapon], "melee")

                attacker.cal_loss(this_subunit, attacker_dmg, attacker_morale_dmg, element_effect)


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
