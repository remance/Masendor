from math import log10

infinity = float("inf")

dodge_formation_bonus = {"Very Tight": -30, "Tight": -15,
                         "Very Loose": 0, "Loose": -5}


def status_update(self):
    """Calculate stat from stamina, morale state, skill, status, terrain"""
    for effect in self.special_effect:  # reset temporary special effect
        self.special_effect[effect][0][1] = False

    # Reset to base stat
    # self.sight = self.base_sight
    # self.hidden = self.base_hidden
    self.weapon_speed = self.original_weapon_speed[self.equipped_weapon].copy()
    self.weapon_dmg = {key: {key2: value2.copy() for key2, value2 in value.items()} for
                       key, value in self.original_weapon_dmg[self.equipped_weapon].items()}

    self.hp_regen = self.base_hp_regen
    self.stamina_regen = self.base_stamina_regen

    self.morale_dmg_bonus = 0
    self.stamina_dmg_bonus = 0
    self.weapon_impact_effect = 1
    self.weapon_dmg_modifier = 1

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
    # sight_bonus = 0
    # hidden_bonus = 0
    shoot_range_bonus = 0
    hp_regen_bonus = 0
    stamina_regen_bonus = 0
    crit_effect_bonus = 0
    melee_weapon_speed_bonus = 0
    temp_reach = 0

    for key in tuple(self.status_duration.keys()):  # loop seem to be faster than comprehension
        self.status_duration[key] -= self.timer
        if self.status_duration[key] <= 0:
            self.status_duration.pop(key)

    # Apply status effect from trait
    for status, aoe in self.trait_ally_status["Final"].items():
        self.apply_effect(status, self.status_list[status], self.status_effect, self.status_duration)
        if aoe > 1:  # status buff range to nearby friend
            self.apply_status_to_nearby(self.near_ally, aoe, status)

    for status, aoe in self.trait_enemy_status["Final"].items():
        self.apply_effect(status, self.status_list[status], self.status_effect, self.status_duration)
        if aoe > 1:  # status buff range to nearby friend
            self.apply_status_to_nearby(self.near_enemy, aoe, status)

    # Apply effect from skill
    if self.skill_effect:
        for key in tuple(self.skill_effect.keys()):
            if "Action" not in self.skill_effect[key]["Action Type"]:
                # action skill type duration mean per attack action instead of time
                self.skill_duration[key] -= self.timer
                if self.skill_duration[key] <= 0:  # skill end
                    self.skill_duration.pop(key)
                    self.skill_effect.pop(key)

        for cal_effect in self.skill_effect.values():  # apply elemental effect to melee_dmg if skill has element
            melee_attack_bonus += cal_effect["Melee Attack Bonus"]
            melee_def_bonus += cal_effect["Melee Defence Bonus"]
            range_def_bonus += cal_effect["Ranged Defence Bonus"]
            speed_bonus += cal_effect["Speed Bonus"]
            accuracy_bonus += cal_effect["Accuracy Bonus"]
            melee_weapon_speed_bonus += cal_effect["Melee Speed Bonus"]
            shoot_range_bonus += cal_effect["Range Bonus"]
            reload_bonus += cal_effect["Reload Bonus"]
            self.charge *= cal_effect["Charge Bonus"]
            charge_def_bonus += cal_effect["Charge Defence Bonus"]
            hp_regen_bonus += cal_effect["HP Regeneration Bonus"]
            stamina_regen_bonus += cal_effect["Stamina Regeneration Bonus"]
            morale_bonus += cal_effect["Morale Bonus"]
            discipline_bonus += cal_effect["Discipline Bonus"]

            for weapon in self.weapon_dmg:
                for key, value in self.weapon_dmg[weapon].items():
                    if key + " Damage Extra" in cal_effect:
                        extra_dmg = cal_effect[key + " Damage Extra"]
                        if extra_dmg:
                            value[0] += int(extra_dmg / 2)
                            value[1] += extra_dmg

            self.weapon_dmg_modifier += cal_effect["Damage Modifier"]

            # sight_bonus += cal_effect["Sight Bonus"]
            # hidden_bonus += cal_effect["Hidden Bonus"]
            crit_effect_bonus += cal_effect["Critical Bonus"]
            self.morale_dmg_bonus += cal_effect["Morale Damage Bonus"]
            self.stamina_dmg_bonus += cal_effect["Stamina Damage Bonus"]
            self.weapon_impact_effect += cal_effect["Weapon Impact Modifier"]

    # Remove status that reach 0 duration or status with conflict to the other status before apply effect
    self.status_effect = {key: val for key, val in self.status_effect.items() if key in self.status_duration and
                          not any(ext in self.status_effect for ext in val["Status Conflict"])}

    # Apply effect and modifier from status effect
    if self.status_effect:
        for cal_effect in self.status_effect.values():
            melee_attack_bonus += cal_effect["Melee Attack Bonus"]
            melee_def_bonus += cal_effect["Melee Defence Bonus"]
            range_def_bonus += cal_effect["Ranged Defence Bonus"]
            speed_bonus += cal_effect["Speed Bonus"]
            accuracy_bonus += cal_effect["Accuracy Bonus"]
            reload_bonus += cal_effect["Reload Bonus"]
            charge_bonus += cal_effect["Charge Bonus"]
            melee_weapon_speed_bonus += cal_effect["Melee Speed Bonus"]
            charge_def_bonus += cal_effect["Charge Defence Bonus"]
            hp_regen_bonus += cal_effect["HP Regeneration Bonus"]
            stamina_regen_bonus += cal_effect["Stamina Regeneration Bonus"]
            morale_bonus += cal_effect["Morale Bonus"]
            discipline_bonus += cal_effect["Discipline Bonus"]
            # sight_bonus += cal_effect["Sight Bonus"]
            # hidden_bonus += cal_effect["Hidden Bonus"]
            temp_reach += cal_effect["Temperature Change"]
            self.element_resistance = {element: value + cal_effect[element + " Resistance Bonus"] for
                                       element, value in self.base_element_resistance.items()}
            for effect in cal_effect["Special Effect"]:
                self.special_effect[tuple(self.special_effect.keys())[effect]][0][1] = True

    # Apply effect from weather
    weather = self.battle.current_weather
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
        morale_bonus += weather.morale_buff
        discipline_bonus += weather.discipline_buff
        for element in weather.element:  # Weather can cause elemental effect such as wet
            self.element_status_check[element[0]] += (element[1] * (100 - self.element_resistance[element[0]]) / 100)
        temp_reach += weather.temperature

    # Map feature modifier to stat
    map_feature_mod = self.feature_map.feature_mod[self.feature]
    if map_feature_mod[self.feature_mod + " Speed Bonus"]:  # speed/charge
        speed_bonus += map_feature_mod[
            self.feature_mod + " Speed Bonus"]  # get the speed mod appropriate to unit type
        if self.double_terrain_penalty and map_feature_mod[self.feature_mod + " Speed Bonus"] < 0:
            speed_bonus += map_feature_mod[
                self.feature_mod + " Speed Bonus"]  # double negative effect

    if map_feature_mod[self.feature_mod + " Melee Bonus"]:  # melee attack
        melee_attack_bonus += map_feature_mod[
            self.feature_mod + " Melee Bonus"]  # get the melee_attack mod appropriate to unit type

    if map_feature_mod[self.feature_mod + " Melee Bonus"]:  # melee/charge defence
        melee_def_bonus += map_feature_mod[
            self.feature_mod + " Melee Bonus"]  # get the defence mod appropriate to unit type
        charge_def_bonus += map_feature_mod[self.feature_mod + " Melee Bonus"]

    range_def_bonus += map_feature_mod["Range Defence Bonus"]  # range defence bonus from terrain
    accuracy_bonus -= (map_feature_mod[
                           "Range Defence Bonus"] / 2)  # range def bonus block unit sight as well so less accuracy
    discipline_bonus += map_feature_mod["Discipline Bonus"]  # discipline bonus from terrain

    self.apply_map_status(map_feature_mod)
    # self.hidden += self.unit.feature_map[self.unit.feature][6]

    # Temperature of the unit change to based on current terrain feature (at time of the day) and weather
    temp_reach += map_feature_mod[self.battle.day_time + " Temperature"]

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

    self.morale = self.base_morale + morale_bonus

    self.morale_state = self.morale / 50  # for using as modifier to stat
    if self.morale_state > 1:  # high morale state (higher than 50) give diminishing bonus to discipline
        self.morale_state = log10(self.morale) - 0.5
    elif self.morale_state < 0:
        self.morale_state = 0

    self.stamina_state = self.stamina / self.max_stamina

    # Discipline get from leader and effect bonus first
    self.discipline = self.base_discipline + self.leader_social_buff + (self.authority / 10) + discipline_bonus
    # Apply morale and stamina state to discipline, each affect half of discipline
    self.discipline = (self.discipline / 2 * self.stamina_state) + (self.discipline / 2 * self.morale_state)
    if self.discipline < 1:
        self.discipline = 1
    discipline_cal = self.command_buff + (log10(self.discipline) / 10)

    # Apply discipline, effect bonus and modifier to stat
    self.melee_attack = (self.base_melee_attack * discipline_cal) + melee_attack_bonus
    self.melee_def = (self.base_melee_def * discipline_cal) + melee_def_bonus
    self.range_def = (self.base_range_def * discipline_cal) + range_def_bonus
    self.accuracy = (self.base_accuracy * discipline_cal) + accuracy_bonus
    self.charge_def = (self.base_charge_def * discipline_cal) + charge_def_bonus
    self.speed = (self.base_speed * discipline_cal) + speed_bonus
    self.charge = (self.base_charge * discipline_cal) + charge_bonus
    self.shoot_range = {key: shoot_range + shoot_range_bonus for key, shoot_range in
                        self.original_shoot_range[self.equipped_weapon].items()}
    self.max_shoot_range = max(self.shoot_range.values())

    if self.leader is not None:  # get buff from formation density
        self.melee_dodge += dodge_formation_bonus[self.leader.group_formation_density]
        self.range_dodge += dodge_formation_bonus[self.leader.group_formation_density]
    # self.sight += sight_bonus
    # self.hidden += hidden_bonus
    self.crit_effect = self.base_crit_effect + crit_effect_bonus

    for key, value in self.melee_range.items():  # affect only melee weapon, so use key from melee range
        self.weapon_speed[key] -= melee_weapon_speed_bonus
        if self.weapon_speed[key] < 0:
            self.weapon_speed[key] = 0

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

    if self.melee_attack < 0:  # seem like using if is faster than max()
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
    self.walk_speed = self.speed / 3

    # Cooldown, active and effect timer function
    for key in tuple(self.skill_cooldown.keys()):  # loop is faster than comprehension here
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

    if self.player_control:  # cal status for command ui value
        self.melee_attack_mod = int(melee_attack_bonus / 10)
        if self.melee_attack_mod > 3:
            self.melee_attack_mod = 3
        elif self.melee_attack_mod < -1:
            self.melee_attack_mod = -1
        self.melee_def_mod = int(melee_def_bonus / 10)
        if self.melee_def_mod > 3:
            self.melee_def_mod = 3
        elif self.melee_def_mod < -1:
            self.melee_def_mod = -1
        self.range_attack_mod = int(accuracy_bonus / 10)
        if self.range_attack_mod > 3:
            self.range_attack_mod = 3
        elif self.range_attack_mod < -1:
            self.range_attack_mod = -1
        self.range_def_mod = int(range_def_bonus / 10)
        if self.range_def_mod > 3:
            self.range_def_mod = 3
        elif self.range_def_mod < -1:
            self.range_def_mod = -1
        self.speed_mod = int(speed_bonus / 10)
        if self.speed_mod > 3:
            self.speed_mod = 3
        elif self.speed_mod < -1:
            self.speed_mod = -1
        self.morale_mod = int(morale_bonus / 10)
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
