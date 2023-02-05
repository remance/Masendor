def add_weapon_stat(self):
    self.melee_weapon_set = {0: 0, 1: 0}
    self.range_weapon_set = {0: 0, 1: 0}
    self.weapon_type = {0: ["melee", "melee"], 1: ["melee", "melee"]}
    for set_index, weapon_set in enumerate(self.weapon_set):
        for weapon_index, weapon in enumerate(weapon_set):
            weapon_stat = self.troop_data.weapon_list[weapon[0]]
            dmg_sum = 0
            dmg_scaling = (weapon_stat["Strength Bonus Scale"], weapon_stat["Dexterity Bonus Scale"])
            dmg_scaling = [item / sum(dmg_scaling) if sum(dmg_scaling) > 0 else 0 for item in dmg_scaling]
            speed_scaling = ((((dmg_scaling[0] * self.strength / 100) + (dmg_scaling[1] * self.dexterity / 100)) * 10) +
                             (self.agility / 5) + (self.wisdom / 10))
            for damage in self.original_weapon_dmg[set_index][weapon_index]:
                damage_name = damage + " Damage"
                if damage_name in weapon_stat:
                    damage_with_attribute = weapon_stat[damage_name] + \
                                            (weapon_stat[damage_name] * (self.strength * dmg_scaling[0] / 100) +
                                             (weapon_stat[damage_name] * (self.dexterity * dmg_scaling[1] / 100)))
                self.original_weapon_dmg[set_index][weapon_index][damage] = [
                    damage_with_attribute * weapon_stat["Damage Balance"] *
                    self.troop_data.equipment_grade_list[weapon[1]]["Modifier"],
                    damage_with_attribute * self.troop_data.equipment_grade_list[weapon[1]]["Modifier"]]
                dmg_sum += self.original_weapon_dmg[set_index][weapon_index][damage][0]
            self.weapon_penetrate[set_index][weapon_index] = weapon_stat["Armour Penetration"] * \
                                                             self.troop_data.equipment_grade_list[weapon[1]]["Modifier"]
            if weapon_stat["Magazine"] == 0:  # weapon is melee weapon with no magazine to load ammo
                self.melee_weapon_set[set_index] += dmg_sum  # add weapon damage for sort
                self.magazine_count[set_index][weapon_index] = 0  # remove modifier
                self.original_melee_range[set_index][weapon_index] = weapon_stat["Range"]
                if weapon_stat["Range"] > self.max_melee_attack_range:
                    self.max_melee_attack_range = weapon_stat["Range"]
            else:
                self.weapon_type[set_index][weapon_index] = "ranged"
                self.magazine_count[set_index][weapon_index] *= weapon_stat["Ammunition"]
                self.magazine_size[set_index][weapon_index] = weapon_stat[
                    "Magazine"]  # can shoot how many times before have to reload
                self.shot_per_shoot[set_index][weapon_index] = weapon_stat["Shot Number"]
                self.original_range[set_index][weapon_index] = weapon_stat["Range"] * \
                                                               self.troop_data.equipment_grade_list[weapon[1]][
                                                                   "Modifier"]

                self.range_weapon_set[set_index] += dmg_sum  # add weapon damage for sort

            self.trait["Weapon"][set_index][weapon_index] += weapon_stat["Trait"]
            if weapon_index == 1 and weapon_stat["Hand"] == 2:  # 2 handed weapon as sub weapon get attack speed penalty
                self.original_weapon_speed[set_index][weapon_index] = (weapon_stat["Cooldown"] - (
                            weapon_stat["Cooldown"] * speed_scaling / 100)) * 1.5
            else:
                self.original_weapon_speed[set_index][weapon_index] = weapon_stat["Cooldown"] - (
                            weapon_stat["Cooldown"] * speed_scaling / 100)
            if self.original_weapon_speed[set_index][weapon_index] < 0:
                self.original_weapon_speed[set_index][weapon_index] = 0
            self.weapon_weight[set_index][weapon_index] = weapon_stat["Weight"]
            self.weight += weapon_stat["Weight"]
            if len(weapon_stat["Skill"]) > 0:
                self.weapon_skill[set_index][weapon_index] = weapon_stat["Skill"][0]  # take only first skill

    for key in self.trait["Weapon"]:
        for weapon in self.trait["Weapon"][key]:
            self.trait["Weapon"][key][weapon] = list(set([trait for trait in
                                                          self.trait["Weapon"][key][weapon] if
                                                          trait != 0]))  # remove empty and duplicate traits
            self.trait["Weapon"][key][weapon] = {x: self.troop_data.trait_list[x] for x in
                                                 self.trait["Weapon"][key][weapon] if
                                                 x in self.troop_data.trait_list}  # replace trait index with data

    # Remove weapon set with no magazine from ammo count
    self.ammo_now = {key: value for key, value in self.ammo_now.items() for
                     key2, value2 in self.magazine_count[key].items() if value2 > 0}
    for key in self.ammo_now.copy():  # remove weapon with no magazine
        for key2 in self.ammo_now[key].copy():
            if self.magazine_count[key][key2] == 0:
                self.ammo_now[key].pop(key2)

    # Sort higher damage priority
    self.melee_weapon_set = dict(sorted(self.melee_weapon_set.items(), key=lambda x: x[1], reverse=True))
    self.range_weapon_set = dict(sorted(self.range_weapon_set.items(), key=lambda x: x[1], reverse=True))

    # Keep only set with damage
    self.melee_weapon_set = {key: value for key, value in self.melee_weapon_set.items() if value > 0}
    self.range_weapon_set = {key: value for key, value in self.range_weapon_set.items() if value > 0}

    # Convert to list
    self.melee_weapon_set = [key for key in self.melee_weapon_set]
    self.range_weapon_set = [key for key in self.range_weapon_set]
