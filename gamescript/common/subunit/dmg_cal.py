import random

from gamescript.common.subunit import hit_register

combat_side_cal = hit_register.combat_side_cal
infinity = float("inf")


def dmg_cal(self, target, hit, defence, weapon, penetrate, dmg_object, hit_side=None):
    """
    Calculate dmg, melee attack will use attacker subunit stat,
    other types will use the type object stat instead (mostly used for range attack)
    :param self: Subunit object
    :param target: Target subunit object
    :param hit: Hit chance value
    :param defence: Defence chance value
    :param dmg_object: Int value for melee weapon or any object for other damage objects
    :param hit_side: Side that the target got hit
    :return: Damage on health, morale, leader and element effect
    """
    height_advantage = self.height - target.height
    if type(dmg_object) != int:
        height_advantage = int(height_advantage / 2)  # Range attack use less height advantage
    hit += height_advantage

    if defence < 0 or self.check_special_effect("Ignore Defence", weapon=weapon):  # Ignore def trait
        defence = 0

    hit_chance = hit - defence
    if hit_chance < 0:
        hit_chance = 0
    elif hit_chance > 80:  # Critical hit
        hit_chance *= self.crit_effect  # modify with crit effect further
        if hit_chance > 200:
            hit_chance = 200
    else:  # infinity number can cause nan value
        hit_chance = 200

    combat_score = round(hit_chance / 100, 1)
    if combat_score == 0 and random.randint(0, 10) > 5:  # chance to scrape instead of miss
        combat_score = 0.1

    troop_dmg = 0
    leader_dmg = 0
    morale_dmg = 0
    remain_penetrate = penetrate

    element_effect = {}

    if combat_score > 0:
        leader_dmg_bonus = 0
        if self.dmg_include_leader and self.leader is not None:
            leader_dmg_bonus = self.leader.combat  # Get extra dmg from leader combat stat

        if type(dmg_object) == int:  # Melee dmg
            dmg = {key: random.uniform(value[0], value[1]) * penetrate / target.element_resistance[key]
            if target.element_resistance[key] > 0 else random.uniform(value[0], value[1]) for key, value in
                   self.weapon_dmg[dmg_object].items()}  # dict comprehension here to save element key

            dmg_sum = sum(dmg.values())
            if 0 in self.skill_effect:  # Include charge in dmg if charging
                if self.check_special_effect("Ignore Charge Defence",
                                             weapon=weapon) is False:  # ignore charge defence if have trait
                    side_cal = combat_side_cal[hit_side]
                    if target.check_special_effect("All Side Full Defence"):  # defence all side
                        side_cal = 1
                    dmg_sum = dmg_sum + ((self.charge_power - (target.charge_def_power * side_cal)) * 2)
                    if (target.charge_def * side_cal) >= self.charge_power / 2:
                        self.charge_momentum = 1  # charge get stopped by charge def
                    else:
                        self.charge_momentum -= (target.charge_def_power * side_cal) / self.charge_power
                else:
                    dmg_sum = dmg_sum + (self.charge_power * 2)
                    self.charge_momentum -= 1 / self.charge_power

            if 0 in target.skill_effect:  # also include its own charge defence in dmg if enemy also charging
                if self.check_special_effect("Ignore Charge Defence") is False:
                    charge_def_cal = self.charge_def_power - target.charge_power
                    if charge_def_cal < 0:
                        charge_def_cal = 0
                    dmg_sum = dmg_sum + (
                            charge_def_cal * 2)  # if charge def is higher than enemy charge then deal back additional melee_dmg

            dmg_sum = dmg_sum * combat_score

        else:  # Range or other type of damage
            dmg = {key: value * penetrate / target.element_resistance[key] if target.element_resistance[key] > 0
            else value for key, value in dmg_object.dmg.items()}
            dmg_sum = sum(dmg.values())
            dmg_sum = dmg_sum * combat_score

        for value in target.element_resistance.values():
            remain_penetrate -= value

        leader_dmg = dmg_sum

        # troop_dmg on subunit is dmg multiply by troop number with addition from leader combat
        troop_dmg = (dmg_sum * self.troop_number) + leader_dmg_bonus
        if (self.check_special_effect("Anti Infantry", weapon=weapon) and target.subunit_type in (0, 1)) or \
                (self.check_special_effect("Anti Cavalry", weapon=weapon) and target.subunit_type in (3, 4, 5, 6)):
            troop_dmg = troop_dmg * 1.25  # Anti trait dmg bonus

        element_effect = {}
        if troop_dmg > 0:
            element_effect = {key: value / troop_dmg for key, value in dmg.items()}
        morale_dmg = dmg_sum / 1000

        # Damage cannot be negative (it would heal instead), same for morale and leader dmg
        if troop_dmg < 0:
            troop_dmg = 0
        if leader_dmg < 0:
            leader_dmg = 0
        if morale_dmg < 0:
            morale_dmg = 0

    return troop_dmg, morale_dmg, leader_dmg, element_effect, remain_penetrate
