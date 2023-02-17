import random

from gamescript.common.damagesprite import cal_melee_hit

combat_side_cal = cal_melee_hit.combat_side_cal
infinity = float("inf")


def cal_dmg(self, attacker, target, hit, defence, dodge, weapon, hit_side=None):
    """
    Calculate dmg, melee attack will use attacker subunit stat,
    other types will use the type object stat instead (mostly used for range attack)
    :param self: DamageSprite object
    :param attacker: Subunit object
    :param target: Target subunit object
    :param hit: Hit chance value
    :param defence: Defence chance value
    :param dodge: Dodge chance value
    :param weapon: Weapon index (0 for main, 1 for sub)
    :param hit_side: Side that the target got hit, use only for melee attack to calculate charge
    :return: Damage on health, morale, leader and element effect
    """
    troop_dmg = 0
    morale_dmg = 0
    element_effect = {}

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

    combat_score = round(hit_chance / 100, 1)
    if combat_score == 0 and random.randint(0, 10) > 5:  # chance to scrape instead of miss
        combat_score = 0.1

    impact = self.impact * combat_score

    if combat_score > 0:
        if self.attack_type == "melee":  # Melee dmg
            troop_dmg, element_effect = cal_dmg_penetrate(self, target)

            if self.charge_skill in attacker.skill_effect:  # Include charge in dmg if charging
                if attacker.check_special_effect("Ignore Charge Defence",
                                                 weapon=weapon) is False:  # ignore charge defence if have trait
                    side_cal = combat_side_cal[hit_side]
                    if target.check_special_effect("All Side Full Defence"):  # defence all side
                        side_cal = 1
                    troop_dmg += ((attacker.charge_power - (target.charge_def_power * side_cal)) * 2)
                    if (target.charge_def * side_cal) >= attacker.charge_power / 2:
                        attacker.momentum = 0  # charge get stopped by charge def
                    else:
                        attacker.momentum -= (target.charge_def_power * side_cal) / attacker.charge_power
                        if attacker.momentum < 0:
                            attacker.momentum = 0
                else:
                    troop_dmg += attacker.charge_power * 2

            if target.charge_skill in target.skill_effect:  # also include its own charge defence in dmg if enemy also charging
                if attacker.check_special_effect("Ignore Charge Defence") is False:
                    charge_def_cal = attacker.charge_def_power - target.charge_power
                    if charge_def_cal < 0:
                        charge_def_cal = 0
                    troop_dmg += (charge_def_cal * 2)  # if charge def is higher than enemy charge then deal back additional melee_dmg

            troop_dmg *= combat_score

        else:  # Range or other type of damage
            troop_dmg, element_effect = cal_dmg_penetrate(self, target)

        self.penetrate -= (target.troop_mass * 5)

        # troop_dmg on subunit is dmg multiply by troop number with addition from leader combat
        if (attacker.check_special_effect("Anti Infantry", weapon=weapon) and target.subunit_type < 2 or
                (attacker.check_special_effect("Anti Cavalry", weapon=weapon) and target.subunit_type == 2)):
            troop_dmg = troop_dmg * 1.25  # Anti trait dmg bonus

        morale_dmg = troop_dmg / 10

        # Damage cannot be negative (it would heal instead), same for morale dmg
        if troop_dmg < 0:
            troop_dmg = 0
        if morale_dmg < 0:
            morale_dmg = 0

    return troop_dmg, morale_dmg, element_effect, impact


def cal_dmg_penetrate(self, target):
    troop_dmg = 0
    element_effect = {}
    for key, value in self.dmg.items():
        if target.element_resistance[key] > 0:
            if self.penetrate < target.element_resistance[key]:
                troop_dmg += value - (value * (target.element_resistance[key] - self.penetrate) / 100)
                element_effect[key] = (value / 10 * (target.element_resistance[key] - self.penetrate) / 100)
            else:
                troop_dmg += value
                element_effect[key] = value / 10
            self.penetrate -= target.element_resistance[key]
        else:
            troop_dmg += value
            element_effect[key] = value / 10
    return troop_dmg, element_effect