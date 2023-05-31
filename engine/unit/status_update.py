infinity = float("inf")

dodge_formation_bonus = {"Very Tight": -30, "Tight": -15,
                         "Very Loose": 0, "Loose": -5}


def status_update(self):
    """Calculate stat from stamina, morale state, skill, status, terrain"""
    for effect in self.special_effect:  # reset temporary special effect
        self.special_effect[effect][0][1] = False

    # Cooldown, active and effect timer function
    for key in self.skill_cooldown.copy():  # loop is faster than comprehension here
        self.skill_cooldown[key] -= self.timer
        if self.skill_cooldown[key] <= 0:  # remove cooldown if time reach 0
            self.skill_cooldown.pop(key)

    # skill is considered available if not in cooldown, has enough discipline and stamina, not already in used
    self.available_skill = [skill for skill in self.input_skill if skill not in self.skill_cooldown
                            and self.discipline >= self.input_skill[skill]["Discipline Requirement"]
                            and self.stamina > self.input_skill[skill]["Stamina Cost"] and
                            ("skill" not in self.current_action or self.current_action["skill"] != skill)]

    ai_skill_condition_list = {"move": [], "melee": [], "range": [], "enemy_near": [], "damaged": [], "retreat": [],
                               "idle": [], "unit_melee": [], "unit_range": [], "troop_melee": [], "troop_range": [],
                               "move_far": []}

    for key, value in self.input_skill.items():
        if key in self.available_skill:
            for condition in value["AI Use Condition"]:
                ai_skill_condition_list[condition].append(key)

    self.available_move_skill = ai_skill_condition_list["move"]
    self.available_melee_skill = ai_skill_condition_list["melee"]
    self.available_range_skill = ai_skill_condition_list["range"]
    self.available_enemy_near_skill = ai_skill_condition_list["enemy_near"]
    self.available_damaged_skill = ai_skill_condition_list["damaged"]
    self.available_retreat_skill = ai_skill_condition_list["retreat"]
    self.available_idle_skill = ai_skill_condition_list["idle"]

    if self.is_leader:
        self.available_unit_melee_skill = ai_skill_condition_list["unit_melee"]
        self.available_troop_melee_skill = ai_skill_condition_list["troop_melee"]
        self.available_unit_range_skill = ai_skill_condition_list["unit_range"]
        self.available_troop_range_skill = ai_skill_condition_list["troop_range"]
        self.available_move_far_skill = ai_skill_condition_list["move_far"]

    for key in self.status_duration.copy():  # loop is faster than comprehension here
        self.status_duration[key] -= self.timer
        if self.status_duration[key] <= 0:
            self.status_duration.pop(key)

    # Remove status that reach 0 duration or status with conflict to the other status
    self.status_effect = {key: val for key, val in self.status_effect.items() if key in self.status_duration and
                          not any(ext in self.status_effect for ext in val["Status Conflict"])}

    # Reset to base stat
    self.morale = self.base_morale
    self.discipline = self.base_discipline
    self.melee_attack = self.base_melee_attack
    self.melee_def = self.base_melee_def
    self.range_def = self.base_range_def
    self.melee_dodge = self.base_melee_dodge
    self.range_dodge = self.base_range_dodge
    self.accuracy = self.base_accuracy
    self.reload = self.base_reload
    self.charge_def = self.base_charge_def
    self.speed = self.base_speed
    self.charge = self.base_charge
    # self.sight = self.base_sight
    # self.hidden = self.base_hidden
    self.crit_effect = self.base_crit_effect
    self.shoot_range = self.original_shoot_range[self.equipped_weapon].copy()
    self.weapon_speed = self.original_weapon_speed[self.equipped_weapon].copy()
    self.weapon_dmg = {key: {key2: value2.copy() for key2, value2 in value.items()} for
                       key, value in self.original_weapon_dmg[self.equipped_weapon].items()}

    self.element_resistance = self.base_element_resistance.copy()

    self.hp_regen = self.base_hp_regen
    self.stamina_regen = self.base_stamina_regen

    self.morale_dmg_bonus = 0
    self.stamina_dmg_bonus = 0
    self.weapon_impact_effect = 1

    morale_bonus = 0
    discipline_bonus = 0
    melee_attack_bonus = 0
    melee_def_bonus = 0
    range_def_bonus = 0
    accuracy_bonus = 0
    reload_bonus = 0
    charge_def_bonus = 0
    speed_bonus = 0
    charge_bonus = 0
    sight_bonus = 0
    # hidden_bonus = 0
    shoot_range_bonus = 0
    hp_regen_bonus = 0
    stamina_regen_bonus = 0

    morale_modifier = 1
    melee_attack_modifier = 1
    melee_def_modifier = 1
    range_def_modifier = 1
    accuracy_modifier = 1
    reload_modifier = 1
    charge_def_modifier = 1
    speed_modifier = 1
    charge_modifier = 1
    shoot_range_modifier = 1
    weapon_dmg_modifier = 1
    crit_effect_modifier = 1
    melee_weapon_speed_modifier = 1

    # Apply status effect from trait
    for status, aoe in self.trait_ally_status["Final"].items():
        self.apply_effect(status, self.status_list[status], self.status_effect, self.status_duration)
        if aoe > 1:  # status buff range to nearby friend
            self.apply_status_to_nearby(self.near_ally, aoe, status)

    for status, aoe in self.trait_enemy_status["Final"].items():
        self.apply_effect(status, self.status_list[status], self.status_effect, self.status_duration)
        if aoe > 1:  # status buff range to nearby friend
            self.apply_status_to_nearby(self.near_enemy, aoe, status)
    # Apply effect from weather
    weather = self.battle.current_weather
    weather_temperature = 0
    if weather.has_stat_effect:
        melee_attack_bonus += weather.melee_atk_buff
        melee_def_bonus += weather.melee_def_buff
        range_def_bonus += weather.range_def_buff
        speed_bonus += weather.speed_buff
        accuracy_bonus += weather.accuracy_buff
        shoot_range_bonus += weather.range_buff
        reload_bonus += weather.reload_buff
        charge_bonus += weather.charge_buff
        charge_def_bonus += weather.charge_def_buff
        hp_regen_bonus += weather.hp_regen_buff
        stamina_regen_bonus += weather.stamina_regen_buff
        morale_bonus += (weather.morale_buff * self.mental)
        discipline_bonus += weather.discipline_buff
        for element in weather.element:  # Weather can cause elemental effect such as wet
            self.element_status_check[element[0]] += (element[1] * (100 - self.element_resistance[element[0]]) / 100)
        weather_temperature = weather.temperature

    # Map feature modifier to stat
    map_feature_mod = self.feature_map.feature_mod[self.feature]

    if map_feature_mod[self.feature_mod + " Speed Modifier"] != 1:  # speed/charge
        speed_modifier += map_feature_mod[
            self.feature_mod + " Speed Modifier"]  # get the speed mod appropriate to unit type

        if self.double_terrain_penalty and map_feature_mod[self.feature_mod + " Speed Modifier"] < 1:
            speed_modifier += map_feature_mod[
                self.feature_mod + " Speed Modifier"]  # double negative effect

    if map_feature_mod[self.feature_mod + " Melee Modifier"] != 1:  # melee melee_attack
        # combat_mod = self.unit.feature_map.feature_mod[self.unit.feature][self.feature_mod + 1]
        melee_attack_modifier += map_feature_mod[
            self.feature_mod + " Melee Modifier"]  # get the melee_attack mod appropriate to unit type

    if map_feature_mod[self.feature_mod + " Melee Modifier"] != 1:  # melee/charge defence
        melee_def_modifier += map_feature_mod[
            self.feature_mod + " Melee Modifier"]  # get the defence mod appropriate to unit type
        charge_def_modifier += map_feature_mod[self.feature_mod + " Melee Modifier"]

    range_def_bonus += map_feature_mod["Range Defence Bonus"]  # range defence bonus from terrain
    accuracy_bonus -= (map_feature_mod[
                           "Range Defence Bonus"] / 2)  # range def bonus block unit sight as well so less accuracy
    discipline_bonus += map_feature_mod["Discipline Bonus"]  # discipline bonus from terrain

    self.apply_map_status(map_feature_mod)
    # self.hidden += self.unit.feature_map[self.unit.feature][6]

    # Temperature of the unit change to based on current terrain feature (at time of the day) and weather
    temp_reach = map_feature_mod[self.battle.day_time + " Temperature"] + weather_temperature

    # Apply effect from skill
    if self.skill_effect:
        for key, value in self.skill_effect.copy().items():
            if "Action" not in value[
                "Action Type"]:  # action skill type duration mean per attack action instead of time
                self.skill_duration[key] -= self.timer
                if self.skill_duration[key] <= 0:  # skill end
                    self.skill_duration.pop(key)
                    self.skill_effect.pop(key)
                # elif "hold" in value["Action"] or "repeat" in value["Action"]:
                #     self.idle_action = self.command_action

        for cal_effect in self.skill_effect.values():  # apply elemental effect to melee_dmg if skill has element
            melee_attack_modifier += cal_effect["Melee Attack Modifier"]
            melee_def_modifier += cal_effect["Melee Defence Modifier"]
            range_def_modifier += cal_effect["Ranged Defence Modifier"]
            speed_modifier += cal_effect["Speed Modifier"]
            accuracy_modifier += cal_effect["Accuracy Modifier"]
            melee_weapon_speed_modifier += cal_effect["Melee Speed Modifier"]
            shoot_range_modifier += cal_effect["Range Modifier"]
            reload_modifier += cal_effect[
                "Reload Modifier"]
            self.charge *= cal_effect["Charge Modifier"]
            charge_def_bonus += cal_effect["Charge Defence Bonus"]
            hp_regen_bonus += cal_effect["HP Regeneration Bonus"]
            stamina_regen_bonus += cal_effect["Stamina Regeneration Bonus"]
            morale_bonus += (cal_effect["Morale Bonus"] * self.mental)
            discipline_bonus += cal_effect["Discipline Bonus"]

            for weapon in self.weapon_dmg:
                for key, value in self.weapon_dmg[weapon].items():
                    if key + " Damage Extra" in cal_effect:
                        extra_dmg = cal_effect[key + " Damage Extra"]
                        if extra_dmg:
                            value[0] += int(extra_dmg / 2)
                            value[1] += extra_dmg

            weapon_dmg_modifier += cal_effect["Damage Modifier"]

            # sight_bonus += cal_effect["Sight Bonus"]
            # hidden_bonus += cal_effect["Hidden Bonus"]
            crit_effect_modifier += cal_effect["Critical Modifier"]
            self.morale_dmg_bonus += cal_effect["Morale Damage Bonus"]
            self.stamina_dmg_bonus += cal_effect["Stamina Damage Bonus"]
            self.weapon_impact_effect += cal_effect["Weapon Impact Modifier"]

    # Apply effect and modifier from status effect
    if self.status_effect:
        for cal_effect in self.status_effect.values():
            melee_attack_modifier += cal_effect["Melee Attack Modifier"]
            melee_def_modifier += cal_effect["Melee Defence Modifier"]
            range_def_modifier += cal_effect["Ranged Defence Modifier"]
            speed_modifier += cal_effect["Speed Modifier"]
            accuracy_modifier += cal_effect["Accuracy Modifier"]
            reload_modifier += cal_effect["Reload Modifier"]
            charge_modifier += cal_effect["Charge Modifier"]
            melee_weapon_speed_modifier += cal_effect["Melee Speed Modifier"]
            charge_def_bonus += cal_effect["Charge Defence Bonus"]
            hp_regen_bonus += cal_effect["HP Regeneration Bonus"]
            stamina_regen_bonus += cal_effect["Stamina Regeneration Bonus"]
            morale_bonus += (cal_effect["Morale Bonus"] * self.mental)
            discipline_bonus += cal_effect["Discipline Bonus"]
            # sight_bonus += cal_effect["Sight Bonus"]
            # hidden_bonus += cal_effect["Hidden Bonus"]
            temp_reach += cal_effect["Temperature Change"]
            for element in self.element_resistance:  # Weather can cause elemental effect such as wet
                self.element_resistance[element] += cal_effect[element + " Resistance Bonus"]
            for effect in cal_effect["Special Effect"]:
                self.special_effect[tuple(self.special_effect.keys())[effect]][0][1] = True

    # Day time effect sight and hidden stat
    if self.battle.day_time == "Twilight":
        if not self.night_vision:
            # sight_bonus -= 10
            accuracy_bonus -= 5
        # hidden_bonus += 10
    elif self.battle.day_time == "Night":
        if not self.night_vision:
            # sight_bonus -= 30
            accuracy_bonus -= 20
        # hidden_bonus += 30
    else:  # day
        if self.day_blindness:
            # sight_bonus -= 30
            accuracy_bonus -= 20

    self.cal_temperature(temp_reach)  # calculate temperature and its effect

    self.check_element_effect()  # elemental effect

    self.morale = (self.morale * morale_modifier) + morale_bonus

    self.morale_state = self.morale / 1000  # for using as modifier to stat
    if self.morale_state > 1:  # morale state can give no more than double bonus
        self.morale_state = 1
    elif self.morale_state < 0:
        self.morale_state = 0

    self.stamina_state = self.stamina / self.max_stamina
    if self.stamina_state < 0.5:
        self.stamina_state = 0.5

    # Apply morale, and leader buff to stat
    self.discipline = (self.discipline + (self.discipline * self.morale_state * self.stamina_state)) + \
                      self.leader_social_buff + (self.authority / 10)  # use morale, leader social and authority
    self.melee_attack = (self.melee_attack + (self.melee_attack * self.morale_state)) * self.command_buff
    self.melee_def = (self.melee_def + (self.melee_def * self.morale_state)) * self.command_buff
    self.range_def = (self.range_def + (self.range_def * self.morale_state)) * self.command_buff
    self.accuracy = self.accuracy * self.command_buff
    self.charge_def = (self.charge_def + (self.charge_def * self.morale_state)) * self.command_buff
    self.speed = (self.speed * self.stamina_state)
    self.charge = (self.charge + (self.charge * self.morale_state)) * self.command_buff

    # Add discipline to stat
    self.discipline += discipline_bonus
    if self.discipline < 0:
        self.discipline = 0

    discipline_cal = self.discipline / 1000
    self.melee_attack += (self.melee_attack * discipline_cal)
    self.melee_def += (self.melee_def * discipline_cal)
    self.range_def += (self.range_def * discipline_cal)
    self.charge_def += (self.charge_def * discipline_cal)
    self.charge += (self.charge * discipline_cal)

    # Apply bonus and modifier to stat
    self.melee_attack = (self.melee_attack * melee_attack_modifier) + melee_attack_bonus
    self.shoot_range = {key: (shoot_range * shoot_range_modifier) + shoot_range_bonus for key, shoot_range in
                        self.shoot_range.items()}

    self.melee_def = (self.melee_def * melee_def_modifier) + melee_def_bonus
    self.range_def = (self.range_def * range_def_modifier) + range_def_bonus
    self.melee_dodge = (self.base_melee_dodge * speed_modifier) + speed_bonus  # dodge get buff based on speed instead
    self.range_dodge = (self.base_range_dodge * speed_modifier) + speed_bonus
    if self.leader is not None:  # get buff from formation density
        self.melee_dodge += dodge_formation_bonus[self.leader.troop_formation_density]
        self.range_dodge += dodge_formation_bonus[self.leader.troop_formation_density]
    self.accuracy = (self.accuracy * accuracy_modifier) + accuracy_bonus
    self.reload = (self.reload * reload_modifier) + reload_bonus
    self.charge_def = (self.charge_def * charge_def_modifier) + charge_def_bonus
    self.speed = (self.speed * speed_modifier) + speed_bonus
    self.charge = (self.charge * charge_modifier) + charge_bonus
    # self.sight += sight_bonus
    # self.hidden += hidden_bonus
    self.crit_effect *= crit_effect_modifier

    for key, value in self.melee_range.items():
        if value > 0:
            self.weapon_speed[key] /= melee_weapon_speed_modifier

    troop_mass = self.troop_mass
    if "less mass" in self.current_action:  # knockdown reduce mass
        troop_mass = int(self.troop_mass / self.current_action["less mass"])

    self.charge += troop_mass
    self.charge_def += troop_mass

    if self.hold_timer and "weapon" in self.current_action:  # holding weapon
        self.melee_dodge /= 2  # reduce dodge during any holding
        self.range_dodge /= 2
        if self.current_action["weapon"] in self.equipped_block_weapon:  # double def for blocking
            self.melee_def *= 2
            self.range_def *= 2

        if self.current_action["weapon"] in self.equipped_charge_block_weapon:  # double charge def but reduce dodge
            self.charge_def *= 2

    if weapon_dmg_modifier != 1:
        for weapon in self.weapon_dmg:
            for element in self.weapon_dmg[weapon]:
                self.weapon_dmg[weapon][element][0] *= weapon_dmg_modifier
                self.weapon_dmg[weapon][element][1] *= weapon_dmg_modifier

    if self.move_speed:  # stat that got affected when moving
        # self.hidden *= 0.9
        # if self.momentum:
        #     self.hidden *= 0.5
        self.charge_def /= 2  # reduce charge def by half when moving

    if self.melee_attack < 0:  # seem like using if 0 is faster than max(0,)
        self.melee_attack = 0
    if self.melee_def < 0:
        self.melee_def = 0
    if self.range_def < 0:
        self.range_def = 0
    if self.melee_dodge < 0:
        self.melee_dodge = 0
    if self.range_dodge < 0:
        self.range_dodge = 0
    if self.speed < 1:  # prevent speed to be lower than 1
        self.speed = 1
    if self.accuracy < 0:
        self.accuracy = 0
    if self.reload < 0:
        self.reload = 0
    if self.charge < 0:
        self.charge = 0
    if self.charge_def < 0:
        self.charge_def = 0

    if self.equipped_weapon in self.ammo_now:  # add reload speed skill to reduce ranged weapon cooldown
        for weapon in self.ammo_now[self.equipped_weapon]:
            self.weapon_speed[weapon] /= (self.reload / 50)

    self.run_speed = self.speed / 2
    self.walk_speed = self.speed / 4

    if self.player_control:  # cal status for command ui value
        self.melee_attack_mod = int(melee_attack_modifier + (melee_attack_bonus / 10))
        if self.melee_attack_mod > 3:
            self.melee_attack_mod = 3
        elif self.melee_attack_mod < -1:
            self.melee_attack_mod = -1
        self.melee_def_mod = int(melee_def_modifier + (melee_def_bonus / 10))
        if self.melee_def_mod > 3:
            self.melee_def_mod = 3
        elif self.melee_def_mod < -1:
            self.melee_def_mod = -1
        self.range_attack_mod = int(accuracy_modifier + (accuracy_bonus / 10))
        if self.range_attack_mod > 3:
            self.range_attack_mod = 3
        elif self.range_attack_mod < -1:
            self.range_attack_mod = -1
        self.range_def_mod = int(range_def_modifier + (range_def_bonus / 10))
        if self.range_def_mod > 3:
            self.range_def_mod = 3
        elif self.range_def_mod < -1:
            self.range_def_mod = -1
        self.speed_mod = int(speed_modifier + (speed_bonus / 10))
        if self.speed_mod > 3:
            self.speed_mod = 3
        elif self.speed_mod < -1:
            self.speed_mod = -1
        self.morale_mod = int(morale_modifier + (morale_bonus / 10))
        if self.morale_mod > 3:
            self.morale_mod = 3
        elif self.morale_mod < -1:
            self.morale_mod = -1
        self.discipline_mod = int(discipline_bonus / 20) + 1
        if self.discipline_mod > 3:
            self.discipline_mod = 3
        elif self.discipline_mod < -1:
            self.discipline_mod = -1
        # self.hidden_mod = int(hidden_bonus / 40) + 1
        # if self.hidden_mod > 3:
        #     self.hidden_mod = 3
        # elif self.hidden_mod < -1:
        #     self.hidden_mod = -1
        self.temperature_mod = int(self.temperature / 50) + 1
        if self.temperature_mod > 3:
            self.temperature_mod = 3
        elif self.temperature_mod < -1:
            self.temperature_mod = -1
