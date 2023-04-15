from math import sin, cos, radians
from pygame import Vector2

from gamescript.common.damagesprite import cal_melee_hit

combat_side_cal = cal_melee_hit.combat_side_cal
infinity = float("inf")


def cal_dmg(self, attacker, target, hit, defence, weapon, hit_side=None):
    """
    Calculate dmg, melee attack will use attacker subunit stat,
    other types will use the type object stat instead (mostly used for range attack)
    :param self: DamageSprite object
    :param attacker: Subunit object
    :param target: Target subunit object
    :param hit: Hit chance value
    :param defence: Defence chance value
    :param weapon: Weapon index (0 for main, 1 for sub)
    :param hit_side: Side that the target got hit, use only for melee attack to calculate charge
    :return: Damage on health, morale, leader and element effect
    """
    # attack pass through dodge now calculate defence
    if attacker.check_special_effect("Ignore Defence", weapon=weapon):  # Ignore def trait
        defence = 0

    hit_chance = hit - defence
    if hit_chance < 0:
        hit_chance = 0
    elif hit_chance > 80:  # Critical hit
        hit_chance *= attacker.crit_effect  # modify with crit effect further
        if hit_chance > 200:
            hit_chance = 200

    hit_score = round(hit_chance / 100, 1)
    if hit_score == 0:  # scrape instead of no damage
        hit_score = 0.1

    impact = self.knock_power

    if hit_score < 0.2:  # reduce impact for low hit score
        impact /= 2
    elif hit_score > 1:  # critical hit, double impact
        impact *= 2

    if self.attack_type == "range":  # Range or other type of damage
        troop_dmg, element_effect = cal_dmg_penetrate(self, target)

    else:  # Melee or charge dmg
        if self.attack_type == "charge":  # Include charge in dmg if charging
            troop_dmg, element_effect = cal_dmg_penetrate(self, target, reduce_penetrate=False)
            if not attacker.check_special_effect("Ignore Charge Defence",
                                                 weapon=weapon):
                side_cal = combat_side_cal[hit_side]
                if target.check_special_effect("All Side Full Defence"):  # defence all side
                    side_cal = 1
                target_charge_def = target.charge_def_power * side_cal
                charge_power_diff = attacker.charge_power + self.charge_power - target_charge_def
                if charge_power_diff > 0:
                    troop_dmg += troop_dmg * charge_power_diff / 100
                    impact *= 2
                else:
                    troop_dmg = 0
                    impact = 0
                    attacker.interrupt_animation = True
                    attacker.command_action = attacker.damaged_command_action
                    attacker.move_speed = attacker.walk_speed
                    attacker.momentum = 0
                    attacker.charging = False
                    attacker.forced_target = Vector2(attacker.base_pos[0] - (5 * sin(radians(attacker.angle))),
                                                     attacker.base_pos[1] - (5 * cos(radians(attacker.angle))))

                    attacker.battle.add_sound_effect_queue(attacker.sound_effect_pool["Damaged"][0], attacker.base_pos,
                                                           attacker.dmg_sound_distance,
                                                           attacker.dmg_sound_shake,
                                                           volume_mod=attacker.hit_volume_mod)

            else:  # ignore charge defence if have trait
                troop_dmg += troop_dmg * attacker.charge_power / 100
        else:
            troop_dmg, element_effect = cal_dmg_penetrate(self, target, reduce_penetrate=False)
            self.penetrate -= target.troop_mass  # melee use troop mass to reduce penetrate

        if target.charging:  # also include its own charge defence in dmg if enemy also charging
            if not attacker.check_special_effect("Ignore Charge Defence", weapon=weapon):
                charge_def_cal = attacker.charge_def_power - target.charge_power
                if charge_def_cal > 0:  # charge def is higher than enemy charge then deal additional dmg
                    impact *= 2
                    troop_dmg += troop_dmg * charge_def_cal / 100

        troop_dmg *= hit_score

    # troop_dmg on subunit is dmg multiply by troop number with addition from leader combat
    if (attacker.check_special_effect("Anti Infantry", weapon=weapon) and target.subunit_type < 2 or
            (attacker.check_special_effect("Anti Cavalry", weapon=weapon) and target.subunit_type == 2)):
        troop_dmg *= 1.25  # Anti trait dmg bonus
        impact *= 1.25

    morale_dmg = troop_dmg / 10

    # Damage cannot be negative (it would heal instead), same for morale dmg
    if troop_dmg < 0:
        troop_dmg = 0
    if morale_dmg < 0:
        morale_dmg = 0

    return troop_dmg, morale_dmg, element_effect, impact


def cal_dmg_penetrate(self, target, reduce_penetrate=True):
    troop_dmg = 0
    element_effect = {}
    for key, value in self.dmg.items():
        if self.penetrate < target.element_resistance[key]:
            dmg = value - (value * (target.element_resistance[key] - self.penetrate) / 100)
            troop_dmg += dmg
            element_effect[key] = dmg / 10
        else:
            troop_dmg += value
            element_effect[key] = value / 10
        if reduce_penetrate:
            self.penetrate -= target.element_resistance[key]
    return troop_dmg, element_effect
