import random

battle_side_cal = (1, 0.4, 0.1, 0.4)  # battle_side_cal is for melee combat side modifier
infinity = float("inf")


def hit_register(self, target, attacker_side, target_side, status_list, target_hit_back=True):
    """base_target position 0 = Front, 1 = Side, 3 = Rear, attacker_side and target_side is the side attacking and defending respectively"""
    attacker_luck = random.randint(-50, 50)  # attacker luck
    target_luck = random.randint(-50, 50)  # defender luck
    attacker_mod = battle_side_cal[attacker_side]  # attacker attack side modifier

    """34 battle master full_def or 91 all round defence status = no flanked penalty"""
    if self.full_def or 91 in self.status_effect:
        attacker_mod = 1
    target_percent = battle_side_cal[target_side]  # defender defend side

    if target.full_def or 91 in target.status_effect:
        target_percent = 1

    dmg_effect = self.front_dmg_effect
    target_dmg_effect = target.front_dmg_effect

    if attacker_side != 0 and attacker_mod != 1:  # if attack or defend from side will use discipline to help reduce penalty a bit
        attacker_mod = battle_side_cal[attacker_side] + (self.discipline / 300)
        dmg_effect = self.side_dmg_effect  # use side dmg effect as some skill boost only front dmg
        if attacker_mod > 1:
            attacker_mod = 1

    if target_side != 0 and target_percent != 1:  # same for the base_target defender
        target_percent = battle_side_cal[target_side] + (target.discipline / 300)
        target_dmg_effect = target.side_dmg_effect
        if target_percent > 1:
            target_percent = 1

    attacker_hit = float(self.melee_attack * attacker_mod) + attacker_luck
    attacker_defence = float(self.melee_def * attacker_mod) + attacker_luck
    target_hit = float(self.melee_attack * target_percent) + target_luck
    target_defence = float(target.melee_def * target_percent) + target_luck

    """33 backstabber ignore def when attack rear side, 55 Oblivious To Unexpected can't defend from rear at all"""
    if (self.backstab and target_side == 2) or (target.oblivious and target_side == 2) or (
            target.flanker and attacker_side in (1, 3)):  # Apply only for attacker
        target_defence = 0

    attacker_dmg, attacker_morale_dmg, attacker_leader_dmg = self.dmg_cal(target, attacker_hit, target_defence, "melee", target_side)  # get dmg by attacker

    self.loss_cal(target, attacker_dmg, attacker_morale_dmg, attacker_leader_dmg, dmg_effect)  # Inflict dmg to defender
    # inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy subunit, 4 entire unit
    if self.inflict_status != {}:
        apply_status_to_enemy(status_list, self.inflict_status, target, attacker_side, target_side)

    if target_hit_back:
        target_dmg, target_morale_dmg, target_leader_dmg = target.dmg_cal(self, target_hit, attacker_defence, "melee",
                                                                   attacker_side)  # get dmg by defender
        target.loss_cal(self, target_dmg, target_morale_dmg, target_leader_dmg, target_dmg_effect)  # Inflict dmg to attacker
        if target.inflict_status != {}:
            apply_status_to_enemy(status_list, target.inflict_status, self, target_side, attacker_side)

    if target.reflect:
        target_dmg = attacker_dmg / 10
        target_morale_dmg = attacker_dmg / 50
        if target.full_reflect:
            target_dmg = attacker_dmg
            target_morale_dmg = attacker_dmg / 10
        target.loss_cal(self, target_dmg, target_morale_dmg, target_dmg_effect)  # Inflict dmg to attacker

    # Attack corner (side) of self with aoe attack
    if self.corner_atk:
        loop_list = [target.nearby_subunit_list[2], target.nearby_subunit_list[5]]  # Side attack get (2) front and (5) rear nearby subunit
        if target_side in (0, 2):
            loop_list = target.nearby_subunit_list[0:2]  # Front/rear attack get (0) left and (1) right nearby subunit
        for this_subunit in loop_list:
            if this_subunit != 0 and this_subunit.state != 100:
                target_hit, target_defence = float(self.melee_attack * target_percent) + target_luck, float(
                    this_subunit.melee_def * target_percent) + target_luck
                attacker_dmg, attacker_morale_dmg = self.dmg_cal(this_subunit, attacker_hit, target_defence, "melee")
                self.loss_cal(this_subunit, attacker_dmg, attacker_morale_dmg, attacker_leader_dmg, dmg_effect)
                if self.inflict_status != {}:
                    apply_status_to_enemy(status_list, self.inflict_status, this_subunit, attacker_side, target_side)


def apply_status_to_enemy(status_list, inflict_status, target, attacker_side, receiver_side):
    """apply aoe status effect to enemy subunits"""
    for status in inflict_status.items():
        if status[1] == 1 and attacker_side == 0:  # only front enemy
            target.status_effect[status[0]] = status_list[status[0]].copy()
        elif status[1] == 2:  # aoe effect to side enemy
            target.status_effect[status[0]] = status_list[status[0]].copy()
            if status[1] == 3:  # apply to corner enemy subunit (left and right of self front enemy subunit)
                corner_enemy_apply = target.nearby_subunit_list[0:2]
                if receiver_side in (1, 2):  # attack on left/right side means corner enemy would be from front and rear side of the enemy
                    corner_enemy_apply = [target.nearby_subunit_list[2], target.nearby_subunit_list[5]]
                for this_subunit in corner_enemy_apply:
                    if this_subunit != 0:
                        this_subunit.status_effect[status[0]] = status_list[status[0]].copy()
        elif status[1] == 3:  # whole unit aoe
            for this_subunit in target.unit.subunits:
                if this_subunit.state != 100:
                    this_subunit.status_effect[status[0]] = status_list[status[0]].copy()

