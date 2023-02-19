import math

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

    self.idle_action = {}
    for key, value in self.skill_effect.copy().items():
        if value["Type"] != "Perform":  # perform skill type duration mean per action instead of time
            self.skill_duration[key] -= self.timer
            if self.skill_duration[key] <= 0:  # skill end
                self.skill_duration.pop(key)
                self.skill_effect.pop(key)
            elif "hold" in value["Action"] or "repeat" in value["Action"]:
                self.idle_action = self.command_action

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
    self.sight = self.base_sight
    self.hidden = self.base_hidden
    self.crit_effect = self.base_crit_effect
    self.shoot_range = self.original_shoot_range[self.equipped_weapon].copy()
    self.weapon_speed = self.original_weapon_speed[self.equipped_weapon].copy()
    self.weapon_dmg = self.original_weapon_dmg[self.equipped_weapon].copy()

    self.hp_regen = self.base_hp_regen
    self.stamina_regen = self.base_stamina_regen

    self.morale_dmg_bonus = 0
    self.stamina_dmg_bonus = 0

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
    hidden_bonus = 0
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
    if map_feature_mod[self.feature_mod + " Speed/Charge Effect"] != 1:  # speed/charge
        speed_modifier += map_feature_mod[
            self.feature_mod + " Speed/Charge Effect"]  # get the speed mod appropriate to subunit type
        charge_modifier += map_feature_mod[self.feature_mod + " Speed/Charge Effect"]

    if map_feature_mod[self.feature_mod + " Combat Effect"] != 1:  # melee melee_attack
        # combat_mod = self.unit.feature_map.feature_mod[self.unit.feature][self.feature_mod + 1]
        melee_attack_modifier += map_feature_mod[
            self.feature_mod + " Combat Effect"]  # get the melee_attack mod appropriate to subunit type

    if map_feature_mod[self.feature_mod + " Defense Effect"] != 1:  # melee/charge defence
        melee_def_modifier += map_feature_mod[
            self.feature_mod + " Defense Effect"]  # get the defence mod appropriate to subunit type
        charge_def_modifier += map_feature_mod[self.feature_mod + " Defense Effect"]

    range_def_bonus += map_feature_mod["Range Defense Bonus"]  # range defence bonus from terrain bonus
    accuracy_bonus -= (map_feature_mod[
                           "Range Defense Bonus"] / 2)  # range def bonus block subunit sight as well so less accuracy
    discipline_bonus += map_feature_mod["Discipline Bonus"]  # discipline defence bonus from terrain bonus

    self.apply_map_status(map_feature_mod)
    # self.hidden += self.unit.feature_map[self.unit.feature][6]

    # Temperature of the subunit change to based on current terrain feature (at time of the day) and weather
    temp_reach = map_feature_mod[self.battle.day_time + " Temperature"] + weather_temperature

    # Apply effect from skill
    if self.skill_effect:
        for cal_effect in self.skill_effect.values():  # apply elemental effect to melee_dmg if skill has element
            melee_attack_modifier += cal_effect["Melee Attack Effect"]
            melee_def_modifier += cal_effect["Melee Defence Effect"]
            range_def_modifier += cal_effect["Ranged Defence Effect"]
            speed_modifier += cal_effect["Speed Effect"]
            accuracy_modifier += cal_effect["Accuracy Effect"]
            shoot_range_modifier += cal_effect["Range Effect"]
            reload_modifier += cal_effect[
                "Reload Effect"]
            self.charge *= cal_effect["Charge Effect"]
            charge_def_bonus += cal_effect["Charge Defence Bonus"]
            hp_regen_bonus += cal_effect["HP Regeneration Bonus"]
            stamina_regen_bonus += cal_effect["Stamina Regeneration Bonus"]
            morale_bonus += (cal_effect["Morale Bonus"] * self.mental)
            discipline_bonus += cal_effect["Discipline Bonus"]

            for weapon in self.weapon_dmg:
                for key, value in self.weapon_dmg[weapon].items():
                    if key != "Physical" and key + " Damage Extra" in cal_effect:
                        extra_dmg = cal_effect[key + " Damage Extra"]
                        if extra_dmg != 0:
                            value[0] += extra_dmg * self.weapon_dmg[weapon]["Physical"]
                            value[1] += extra_dmg * self.weapon_dmg[weapon]["Physical"]
                    else:
                        value[0] *= cal_effect["Physical Damage Effect"]
                        value[1] *= cal_effect["Physical Damage Effect"]

            sight_bonus += cal_effect["Sight Bonus"]
            hidden_bonus += cal_effect["Hidden Bonus"]
            crit_effect_modifier += cal_effect["Critical Effect"]
            self.morale_dmg_bonus += cal_effect["Morale Damage Bonus"]
            self.stamina_dmg_bonus += cal_effect["Stamina Damage Bonus"]

    # Apply effect and modifier from status effect
    if self.status_effect:
        for cal_effect in self.status_effect.values():
            melee_attack_modifier += cal_effect["Melee Attack Effect"]
            melee_def_modifier += cal_effect["Melee Defence Effect"]
            range_def_modifier += cal_effect["Ranged Defence Effect"]
            speed_modifier += cal_effect["Speed Effect"]
            accuracy_modifier += cal_effect["Accuracy Effect"]
            reload_modifier += cal_effect["Reload Effect"]
            charge_modifier += cal_effect["Charge Effect"]
            charge_def_bonus += cal_effect["Charge Defence Bonus"]
            hp_regen_bonus += cal_effect["HP Regeneration Bonus"]
            stamina_regen_bonus += cal_effect["Stamina Regeneration Bonus"]
            morale_bonus += (cal_effect["Morale Bonus"] * self.mental)
            discipline_bonus += cal_effect["Discipline Bonus"]
            sight_bonus += cal_effect["Sight Bonus"]
            hidden_bonus += cal_effect["Hidden Bonus"]
            temp_reach += cal_effect["Temperature Change"]
            for element in self.element_resistance:  # Weather can cause elemental effect such as wet
                self.element_resistance[element] += cal_effect[element + " Resistance Bonus"]
            for effect in cal_effect["Special Effect"]:
                self.special_effect[tuple(self.special_effect.keys())[effect]][0][1] = True

    # Day time effect sight and hidden stat
    if self.battle.day_time == "Twilight":
        if not self.night_vision:
            sight_bonus -= 10
            accuracy_bonus -= 5
        hidden_bonus += 10
    elif self.battle.day_time == "Night":
        if not self.night_vision:
            sight_bonus -= 30
            accuracy_bonus -= 20
        hidden_bonus += 30
    else:  # day
        if self.day_blindness:
            sight_bonus -= 30
            accuracy_bonus -= 20

    self.cal_temperature(temp_reach)  # calculate temperature and its effect

    self.check_element_effect()  # elemental effect

    self.morale_state = self.morale / self.max_morale  # for using as modifier to stat
    if self.morale_state > 3 or math.isnan(self.morale_state):  # morale state more than 3 give no more benefit
        self.morale_state = 3
    elif self.morale_state < 0:
        self.morale_state = 0

    # Apply morale, and leader buff to stat
    self.discipline = (self.discipline * self.morale_state) + self.leader_social_buff + \
                      (self.authority / 10)  # use morale, stamina, leader social vs grade and authority
    self.melee_attack = (self.melee_attack * (self.morale_state + 0.1)) * self.command_buff
    self.melee_def = (self.melee_def * (self.morale_state + 0.1)) * self.command_buff
    self.range_def = (self.range_def * (self.morale_state + 0.1)) * self.command_buff
    self.accuracy = self.accuracy * self.command_buff
    self.charge_def = (self.charge_def * (
            self.morale_state + 0.1)) * self.command_buff  # use morale, stamina and command buff
    height_diff = (self.height / self.front_height) ** 2  # walk down hill increase speed, walk up hill reduce speed
    self.speed = self.speed * height_diff
    self.charge = (self.charge + self.speed) * (self.morale_state + 0.1) * self.command_buff

    # Add discipline to stat
    discipline_cal = self.discipline / 200
    self.melee_attack += (self.melee_attack * discipline_cal)
    self.melee_def += (self.melee_def * discipline_cal)
    self.range_def += (self.range_def * discipline_cal)
    self.speed += (self.speed * discipline_cal / 2)
    self.charge_def += (self.charge_def * discipline_cal)
    self.charge += (self.charge * discipline_cal)

    # Apply bonus and modifier to stat
    self.morale = (self.morale * morale_modifier) + morale_bonus
    self.discipline = self.discipline + discipline_bonus
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
    self.sight = self.sight + sight_bonus
    self.hidden = self.hidden + hidden_bonus
    self.crit_effect = self.crit_effect * crit_effect_modifier

    troop_mass = self.troop_mass
    if "less mass" in self.current_action:  # knockdown reduce mass
        troop_mass = int(self.troop_mass / self.current_action["less mass"])
    self.charge_power = ((self.charge * self.momentum) / 2) * troop_mass

    self.charge_def_power = self.charge_def * troop_mass
    if self.move_speed:  # reduce charge def by half when moving
        self.charge_def_power /= 2

    if self.hold_timer == 1:  # holding weapon animation for at least 1 sec, apply buff
        if "power" in self.action_list[self.current_action["weapon"]]["Properties"]:
            for value in self.weapon_dmg[self.current_action["weapon"]].values():
                value[0] *= 0.5
                value[1] *= 0.5

        if "block" in self.action_list[self.current_action["weapon"]]["Properties"]:  # double def but reduce dodge
            self.melee_def *= 2
            self.range_def *= 2
            self.melee_dodge /= 2
            self.range_dodge /= 2

        if "chargeblock" in self.action_list[self.current_action["weapon"]]["Properties"]:  # double charge def but reduce dodge
            self.charge_def_power *= 2
            self.melee_dodge /= 2
            self.range_dodge /= 2

    if weapon_dmg_modifier != 1:
        for weapon in self.weapon_dmg:
            for element in self.weapon_dmg[weapon]:
                self.weapon_dmg[weapon][element][0] *= weapon_dmg_modifier
                self.weapon_dmg[weapon][element][1] *= weapon_dmg_modifier

    # include all penalties to morale like remaining health, battle situation scale
    self.morale -= ((20 - (20 * self.battle.battle_scale[self.team] / 100)) * self.mental)

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
    if self.charge_power < 0:
        self.charge_power = 0
    if self.charge_def_power < 0:
        self.charge_def_power = 0
    if self.discipline < 0:
        self.discipline = 0
    if self.equipped_weapon in self.magazine_count:  # add reload speed skill to reduce ranged weapon cooldown
        for weapon in self.magazine_count[self.equipped_weapon]:
            self.weapon_speed[weapon] += ((100 - self.reload) * self.weapon_speed[weapon] / 100)
            if self.weapon_speed[weapon] < 1:  # weapon speed can not be less than 0.1 second per hit
                self.weapon_speed[weapon] = 1

    self.run_speed = self.speed
    self.walk_speed = self.speed / 2
