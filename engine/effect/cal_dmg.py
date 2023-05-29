from math import sin, cos, radians

from pygame import Vector2

from engine.effect import cal_melee_hit

combat_side_cal = cal_melee_hit.combat_side_cal
infinity = float("inf")


def cal_dmg(self, target, hit, defence, weapon, hit_side=None):
    """
    Calculate dmg, melee attack will use attacker unit stat,
    other types will use the type object stat instead (mostly used for range attack)
    :param self: DamageEffect object
    :param target: Target unit object
    :param hit: Hit chance value
    :param defence: Defence chance value
    :param weapon: Weapon index (0 for main, 1 for sub)
    :param hit_side: Side that the target got hit, use only for melee attack to calculate charge
    :return: Damage on health, morale, and element effect
    """
    # attack pass through dodge now calculate defence
    if self.attacker.check_special_effect("Ignore Defence", weapon=weapon):  # Ignore def trait
        defence = 0

    hit_score = cal_hit_score(self, hit, defence)

    if self.attack_type == "range":  # Range or other type of damage
        impact = self.knock_power
        troop_dmg, element_effect = cal_dmg_penetrate(self, target)

    elif self.attack_type == "charge":
        troop_dmg, element_effect, impact = cal_charge_dmg(self, target, hit_side)

    else:  # Melee dmg
        impact = self.knock_power
        troop_dmg, element_effect = cal_dmg_penetrate(self, target, reduce_penetrate=False)
        self.penetrate -= target.troop_mass  # melee use troop mass to reduce penetrate

        if target.momentum:  # also include its own charge defence in dmg if enemy also charging
            if not self.attacker.check_special_effect("Ignore Charge Defence", weapon=weapon):
                if self.attacker.charge_def > 0:  # add charge def as additional dmg modifier
                    troop_dmg += troop_dmg * self.attacker.charge_def / 100

        troop_dmg *= hit_score

    if hit_score < 0.2:  # reduce impact for low hit score
        impact /= 2
    elif hit_score > 1:  # critical hit, double impact
        impact *= 2

    # troop_dmg on unit is dmg multiply by troop number with addition from leader combat
    if (self.attacker.check_special_effect("Anti Infantry", weapon=weapon) and target.unit_type < 2 or
            (self.attacker.check_special_effect("Anti Cavalry", weapon=weapon) and target.unit_type == 2)):
        troop_dmg *= 1.25  # Anti trait dmg bonus
        impact *= 1.25

    morale_dmg = troop_dmg / 10

    # Damage cannot be negative (it would heal instead), same for morale dmg
    if troop_dmg < 0:
        troop_dmg = 0
    if morale_dmg < 0:
        morale_dmg = 0

    return troop_dmg, morale_dmg, element_effect, impact


def cal_hit_score(self, hit, defence):
    hit_chance = hit - defence
    if hit_chance < 0:
        hit_chance = 0
    elif hit_chance > 80:  # Critical hit
        hit_chance *= self.attacker.crit_effect  # modify with crit effect further
        if hit_chance > 200:
            hit_chance = 200

    hit_score = round(hit_chance / 100, 1)
    if hit_score <= 0:  # scrape instead of no damage
        hit_score = 0.1
    return hit_score


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


def cal_charge_dmg(self, target, hit_side):
    if "weapon" in self.attacker.current_action:
        weapon = self.attacker.current_action["weapon"]
        dmg = {key: value[0] for key, value in self.attacker.weapon_dmg[weapon].items() if value[0]}
        impact = self.attacker.weapon_impact[self.attacker.equipped_weapon][weapon]
        penetrate = self.attacker.weapon_penetrate[self.attacker.equipped_weapon][weapon]
    else:  # charge without using weapon (by running)
        weapon = None
        dmg = self.attacker.body_weapon_damage
        impact = self.attacker.body_weapon_impact
        penetrate = self.attacker.body_weapon_penetrate

    troop_dmg = 0
    element_effect = {}
    for key, value in dmg.items():
        if penetrate < target.element_resistance[key]:
            dmg = value - (value * (target.element_resistance[key] - penetrate) / 100)
            troop_dmg += dmg
            element_effect[key] = dmg / 10
        else:
            troop_dmg += value
            element_effect[key] = value / 10

    charge_power = (self.attacker.charge + self.attacker.speed) * self.attacker.momentum

    if not self.attacker.check_special_effect("Ignore Charge Defence",
                                              weapon=weapon):
        side_cal = combat_side_cal[hit_side]
        if target.check_special_effect("All Side Full Defence"):  # defence all side
            side_cal = 1
        target_charge_def = target.charge_def * side_cal
        charge_power_diff = charge_power - target_charge_def
        if charge_power_diff > 0:
            troop_dmg += troop_dmg * charge_power_diff / 100
            impact *= charge_power_diff / 100
        else:  # enemy charge def is higher
            troop_dmg = 0
            impact = 0
            self.attacker.interrupt_animation = True
            self.attacker.command_action = self.attacker.damaged_command_action
            self.attacker.momentum = 0
            self.attacker.forced_target = Vector2(
                self.attacker.base_pos[0] - (5 * sin(radians(self.attacker.angle))),
                self.attacker.base_pos[1] - (5 * cos(radians(self.attacker.angle))))

            self.attacker.battle.add_sound_effect_queue(self.attacker.sound_effect_pool["Damaged"][0],
                                                        self.attacker.base_pos,
                                                        self.attacker.dmg_sound_distance,
                                                        self.attacker.dmg_sound_shake,
                                                        volume_mod=self.attacker.hit_volume_mod)

    else:  # ignore charge defence if have trait
        troop_dmg += troop_dmg * self.charge_power / 100

    return troop_dmg, element_effect, impact
