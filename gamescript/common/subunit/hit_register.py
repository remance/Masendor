import random

combat_side_cal = (1, 0.4, 0.1, 0.4)  # for melee combat side modifier
infinity = float("inf")


def hit_register(self, weapon, target, attacker_side, hit_side, status_list):
    """base_target position 0 = Front, 1 = Side, 3 = Rear, attacker_side and target_side is the side attacking and defending respectively"""
    attacker_luck = random.randint(-50, 20)  # attacker luck
    target_luck = random.randint(-20, 30)  # defender luck
    attacker_side_mod = combat_side_cal[attacker_side]  # attacker attack side modifier

    if self.check_special_effect("All Side Full Attack"):
        attacker_side_mod = 1

    hit_side_mod = combat_side_cal[hit_side]  # defender defend side
    if self.check_special_effect("All Side Full Defence", weapon=weapon):
        hit_side_mod = 1

    if attacker_side != 0 and attacker_side_mod != 1:  # if attack or defend from side will use discipline to help reduce penalty a bit
        attacker_side_mod += (self.discipline / 300)
        if attacker_side_mod > 1:
            attacker_side_mod = 1

    if hit_side != 0 and hit_side_mod != 1:  # same for the base_target defender
        hit_side_mod += (target.discipline / 300)
        if hit_side_mod > 1:
            hit_side_mod = 1

    attacker_hit = float(self.melee_attack * attacker_side_mod) + attacker_luck
    target_defence = float(target.melee_def * hit_side_mod) + target_luck

    if (self.check_special_effect("Rear Attack Bonus") and hit_side == 2) or \
            (self.check_special_effect("No Rear Defence") and hit_side == 2) or \
            (self.check_special_effect("Flank Attack Bonus") and attacker_side in (1, 3)):  # apply only for attacker
        target_defence = 0

    attacker_dmg, attacker_morale_dmg, attacker_leader_dmg, \
        element_effect, _ = self.dmg_cal(target, attacker_hit, target_defence, weapon,
                                         self.weapon_penetrate[self.equipped_weapon][weapon], weapon,
                                         hit_side)  # get dmg by attacker

    self.loss_cal(target, attacker_dmg, attacker_morale_dmg, attacker_leader_dmg,
                  element_effect)  # inflict dmg to defender

    if self.inflict_status != {}:  # inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy subunit, 4 entire unit
        apply_status_to_enemy(status_list, self.inflict_status, target, attacker_side, hit_side)

    if self.check_special_effect("Reflect Damage"):
        target_dmg = attacker_dmg / 10
        target_morale_dmg = attacker_dmg / 50
        if target.full_reflect:
            target_dmg = attacker_dmg
            target_morale_dmg = attacker_dmg / 10
        target.loss_cal(self, target_dmg, target_morale_dmg, element_effect)  # inflict dmg to attacker

    # Attack corner (side) of self with aoe attack
    if self.corner_atk:
        loop_list = [target.nearby_subunit_list[2],
                     target.nearby_subunit_list[5]]  # Side attack get (2) front and (5) rear nearby subunit
        if hit_side in (0, 2):
            loop_list = target.nearby_subunit_list[0:2]  # Front/rear attack get (0) left and (1) right nearby subunit
        for this_subunit in loop_list:
            if this_subunit != 0 and this_subunit.state != 100:
                target_hit, target_defence = float(self.melee_attack * hit_side_mod) + target_luck, float(
                    this_subunit.melee_def * hit_side_mod) + target_luck
                attacker_dmg, attacker_morale_dmg, attacker_leader_dmg, \
                    element_effect, _ = self.dmg_cal(this_subunit, attacker_hit, target_defence, weapon,
                                                     self.weapon_penetrate[self.equipped_weapon][weapon], "melee")

                self.loss_cal(this_subunit, attacker_dmg, attacker_morale_dmg, attacker_leader_dmg, element_effect)
                if self.inflict_status != {}:
                    apply_status_to_enemy(status_list, self.inflict_status, this_subunit, attacker_side, hit_side)


def apply_status_to_enemy(status_list, inflict_status, target, attacker_side, receiver_side):
    """apply aoe status effect to enemy subunits"""
    for status in inflict_status.items():
        if status[1] == 1 and attacker_side == 0:  # only front enemy
            target.status_effect[status[0]] = status_list[status[0]].copy()
        elif status[1] == 2:  # aoe effect to side enemy
            target.status_effect[status[0]] = status_list[status[0]].copy()
            if status[1] == 3:  # apply to corner enemy subunit (left and right of self front enemy subunit)
                corner_enemy_apply = target.nearby_subunit_list[0:2]
                if receiver_side in (
                1, 2):  # attack on left/right side means corner enemy would be from front and rear side of the enemy
                    corner_enemy_apply = [target.nearby_subunit_list[2], target.nearby_subunit_list[5]]
                for this_subunit in corner_enemy_apply:
                    if this_subunit != 0:
                        this_subunit.status_effect[status[0]] = status_list[status[0]].copy()
        elif status[1] == 3:  # whole unit aoe
            for this_subunit in target.unit.alive_subunit_list:
                if this_subunit.state != 100:
                    this_subunit.status_effect[status[0]] = status_list[status[0]].copy()
