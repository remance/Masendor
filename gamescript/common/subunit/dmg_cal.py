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

    if defence < 0 or self.ignore_def:  # Ignore def trait
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
            dmg = random.uniform(self.melee_dmg[0], self.melee_dmg[1])
            if 0 in self.skill_effect:  # Include charge in dmg if attacking
                if self.ignore_charge_def is False:  # Ignore charge defence if have ignore trait
                    side_cal = battle_side_cal[def_side]
                    if target.full_def or target.temp_full_def:  # defence all side
                        side_cal = 1
                    dmg = dmg + ((self.charge - (target.charge_def * side_cal)) * 2)
                    if (target.charge_def * side_cal) >= self.charge / 2:
                        self.charge_momentum = 1  # charge get stopped by charge def
                    else:
                        self.charge_momentum -= (target.charge_def * side_cal) / self.charge
                else:
                    dmg = dmg + (self.charge * 2)
                    self.charge_momentum -= 1 / self.charge

            if 0 in target.skill_effect:  # Also include charge_def in melee_dmg if enemy charging
                if target.ignore_charge_def is False:
                    charge_def_cal = self.charge_def - target.charge
                    if charge_def_cal < 0:
                        charge_def_cal = 0
                    dmg = dmg + (charge_def_cal * 2)  # if charge def is higher than enemy charge then deal back additional melee_dmg
            elif 0 not in self.skill_effect:  # not charging or defend from charge, use attack speed roll
                dmg += sum([random.uniform(self.melee_dmg[0], self.melee_dmg[1]) for x in range(self.weapon_speed)])

            penetrate = self.melee_penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmg * penetrate * combat_score

        else:  # Range or other type of damage
            penetrate = dmg_type.penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmg_type.dmg * penetrate * combat_score

        leader_dmg = dmg
        troop_dmg = (dmg * self.troop_number) + leader_dmg_bonus  # dmg on subunit is dmg multiply by troop number with addition from leader combat
        if (self.anti_inf and target.subunit_type in (1, 2)) or (self.anti_cav and target.subunit_type in (4, 5, 6, 7)):  # Anti trait dmg bonus
            troop_dmg = troop_dmg * 1.25

        morale_dmg = dmg / 50

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

    return troop_dmg, morale_dmg, leader_dmg