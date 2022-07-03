import random

battle_side_cal = (1, 0.4, 0.1, 0.4)  # battle_side_cal is for melee combat side modifier
infinity = float("inf")


def dmg_cal(self, target, hit, defence, dmg_type, def_side=None):
    """Calculate dmg, melee attack will use attacker subunit stat,
    other types will use the type object stat instead (mostly used for range attack)"""
    height_advantage = self.height - target.height
    if dmg_type != "melee":
        height_advantage = int(height_advantage / 2)  # Range attack use less height advantage
    hit += height_advantage

    if defence < 0 or True in self.special_status["Ignore Defence"]:  # Ignore def trait
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
    if combat_score == 0 and random.randint(0, 10) > 9:  # Final chance to not miss
        combat_score = 0.1

    if combat_score > 0:
        leader_dmg_bonus = 0
        if self.dmg_include_leader and self.leader is not None:
            leader_dmg_bonus = self.leader.combat  # Get extra dmg from leader combat stat

        if dmg_type == "melee":  # Melee dmg
            dmg = {key: random.uniform(value[0], value[1]) * self.weapon_penetrate[self.equipped_weapon][key] / target.element_resistance[key] if self.weapon_penetrate[self.equipped_weapon][key] / target.element_resistance[key] <= 1 else random.uniform(value[0], value[1]) for key, value in self.weapon_dmg.items()}
            dmg_sum = sum(dmg.values())
            status_effect = {key: value / dmg_sum for key, value in dmg.items()}
            if 0 in self.skill_effect:  # Include charge in dmg if charging
                if True in self.special_status["Ignore Charge Defence"] is False:  # Ignore charge defence if have ignore trait
                    side_cal = battle_side_cal[def_side]
                    if True in target.special_status["All Side Full Defence"]:  # defence all side
                        side_cal = 1
                    dmg_sum = dmg_sum + ((self.charge - (target.charge_def * side_cal)) * 2)
                    if (target.charge_def * side_cal) >= self.charge / 2:
                        self.charge_momentum = 1  # charge get stopped by charge def
                    else:
                        self.charge_momentum -= (target.charge_def * side_cal) / self.charge
                else:
                    dmg_sum = dmg_sum + (self.charge * 2)
                    self.charge_momentum -= 1 / self.charge

            if 0 in target.skill_effect:  # Also include charge_def in melee_dmg if enemy also charging
                if True in target.special_status["Ignore Charge Defence"] is False:
                    charge_def_cal = self.charge_def - target.charge
                    if charge_def_cal < 0:
                        charge_def_cal = 0
                    dmg_sum = dmg_sum + (charge_def_cal * 2)  # if charge def is higher than enemy charge then deal back additional melee_dmg
            elif 0 not in self.skill_effect:  # not charging or defend from charge, use attack speed roll
                dmg_sum += sum([random.uniform(self.weapon_dmg[0], self.weapon_dmg[1]) for x in range(self.original_weapon_speed)])

            dmg_sum = dmg_sum * combat_score

        else:  # Range or other type of damage
            dmg = {key: value * (dmg_type.penetrate - target.element_resistance[key])
                   if dmg_type.penetrate - target.element_resistance[key] <= 1 else value for key, value in dmg_type.dmg.items()}
            dmg_sum = sum(dmg_type.values())
            status_effect = {key: value / dmg_sum for key, value in dmg.items()}
            dmg_sum = dmg_sum * combat_score

        leader_dmg = dmg_sum
        troop_dmg = (dmg_sum * self.troop_number) + leader_dmg_bonus  # dmg on subunit is dmg multiply by troop number with addition from leader combat
        if (True in self.shooter.special_status["Anti Infantry"] and target.subunit_type in (1, 2)) or \
                (True in self.shooter.special_status["Anti Cavalry"] and target.subunit_type in (4, 5, 6, 7)):
            troop_dmg = troop_dmg * 1.25  # Anti trait dmg bonus

        morale_dmg = dmg_sum / 50

        # Damage cannot be negative (it would heal instead), same for morale and leader dmg
        if troop_dmg < 0:
            troop_dmg = 0
        if leader_dmg < 0:
            leader_dmg = 0
        if morale_dmg < 0:
            morale_dmg = 0
    else:  # complete miss
        troop_dmg = 0
        leader_dmg = 0
        morale_dmg = 0

    return troop_dmg, morale_dmg, leader_dmg, status_effect