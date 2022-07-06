import math

infinity = float("inf")


def status_update(self, weather=None):
    """Calculate stat from stamina, morale state, skill, status, terrain"""

    if self.red_border and self.unit.selected:  # have red border (taking melee_dmg) on inspect ui, reset image
        self.block.blit(self.block_original, self.corner_image_rect)
        self.red_border = False

    for effect in self.special_effect:  # reset temporary special effect
        self.special_effect[effect][0][1] = False

    self.fatigue()

    self.morale = self.base_morale
    self.authority = self.unit.authority  # unit total authority
    self.discipline = self.base_discipline
    self.melee_attack = self.base_melee_attack
    self.melee_def = self.base_melee_def
    self.range_def = self.base_range_def
    self.accuracy = self.base_accuracy
    self.reload = self.base_reload
    self.charge_def = self.base_charge_def
    self.speed = self.base_speed
    self.charge = self.base_charge
    self.shoot_range = self.original_range[self.equipped_weapon].copy()
    self.weapon_speed = self.original_weapon_speed[self.equipped_weapon].copy()
    self.weapon_dmg = self.original_weapon_dmg[self.equipped_weapon].copy()

    self.crit_effect = 1  # Default critical effect

    self.corner_atk = False  # Cannot melee_attack corner enemy by default

    self.auth_penalty = self.base_auth_penalty
    self.hp_regen = self.base_hp_regen
    self.stamina_regen = self.base_stamina_regen
    self.inflict_status = self.base_inflict_status

    # Apply status effect from trait

    trait_list = list(self.trait["Original"].values()) + list(self.trait["Weapon"][self.equipped_weapon][0].values()) + list(self.trait["Weapon"][self.equipped_weapon][1].values())
    if len(trait_list) > 1:
        for trait in trait_list:
            if 0 not in trait["Status"]:
                for effect in trait["Status"]:  # apply status effect from trait
                    self.status_effect[effect] = self.status_list[effect].copy()
                    if trait["Buff Range"] > 1:  # status buff range to nearby friend
                        self.apply_status_to_friend(trait[1], effect, self.status_list[effect].copy())

    # Apply effect from weather
    weather_temperature = 0
    if weather is not None:
        self.melee_attack += weather.melee_atk_buff
        self.melee_def += weather.melee_def_buff
        self.range_def += weather.range_def_buff
        self.speed += weather.speed_buff
        self.accuracy += weather.accuracy_buff
        for shoot_range in self.shoot_range:
            shoot_range += weather.range_buff
        self.reload += weather.reload_buff
        self.charge += weather.charge_buff
        self.charge_def += weather.charge_def_buff
        self.hp_regen += weather.hp_regen_buff
        self.stamina_regen += weather.stamina_regen_buff
        self.morale += (weather.morale_buff * self.mental)
        self.discipline += weather.discipline_buff
        for element in weather.element:  # Weather can cause elemental effect such as wet
            self.element_status_check[element[0]] += (element[1] * (100 - self.element_resistance[element[0]]) / 100)
        weather_temperature = weather.temperature

    # v Map feature modifier to stat
    map_feature_mod = self.feature_map.feature_mod[self.feature]
    if map_feature_mod[self.feature_mod + " Speed/Charge Effect"] != 1:  # speed/charge
        speed_mod = map_feature_mod[self.feature_mod + " Speed/Charge Effect"]  # get the speed mod appropriate to subunit type
        self.speed *= speed_mod
        self.charge *= speed_mod

    if map_feature_mod[self.feature_mod + " Combat Effect"] != 1:  # melee melee_attack
        # combat_mod = self.unit.feature_map.feature_mod[self.unit.feature][self.feature_mod + 1]
        self.melee_attack *= map_feature_mod[self.feature_mod + " Combat Effect"]  # get the melee_attack mod appropriate to subunit type

    if map_feature_mod[self.feature_mod + " Defense Effect"] != 1:  # melee/charge defence
        combat_mod = map_feature_mod[self.feature_mod + " Defense Effect"]  # get the defence mod appropriate to subunit type
        self.melee_def *= combat_mod
        self.charge_def *= combat_mod

    self.range_def += map_feature_mod["Range Defense Bonus"]  # range defence bonus from terrain bonus
    self.accuracy -= (map_feature_mod["Range Defense Bonus"] / 2)  # range def bonus block subunit sight as well so less accuracy
    self.discipline += map_feature_mod["Discipline Bonus"]  # discipline defence bonus from terrain bonus

    self.apply_map_status(map_feature_mod)
    # self.hidden += self.unit.feature_map[self.unit.feature][6]
    temp_reach = map_feature_mod["Temperature"] + weather_temperature  # temperature the subunit will change to based on current terrain feature and weather

    # Apply effect from skill
    if len(self.skill_effect) > 0:
        for effect in self.skill_effect:  # apply elemental effect to melee_dmg if skill has element
            cal_effect = self.skill_effect[effect]
            self.melee_attack *= cal_effect["Melee Attack Effect"]
            self.melee_def *= cal_effect["Melee Defence Effect"]
            self.range_def *= cal_effect["Ranged Defence Effect"]
            self.speed *= cal_effect["Speed Effect"]
            self.accuracy *= cal_effect["Accuracy Effect"]
            for shoot_range in self.shoot_range:
                shoot_range *= cal_effect["Range Effect"]
            self.reload /= cal_effect[
                "Reload Effect"]  # different from other modifier the higher mod reduce reload time (decrease stat)
            self.charge *= cal_effect["Charge Effect"]
            self.charge_def += cal_effect["Charge Defence Bonus"]
            self.hp_regen += cal_effect["HP Regeneration Bonus"]
            self.stamina_regen += cal_effect["Stamina Regeneration Bonus"]
            self.morale += (cal_effect["Morale Bonus"] * self.mental)
            self.discipline += cal_effect["Discipline Bonus"]

            for weapon in self.weapon_dmg:
                for element in self.weapon_dmg[weapon]:
                    if element != "Physical":
                        extra_dmg = cal_effect[element + " Damage Extra"]
                        if extra_dmg != 0:
                            self.weapon_dmg[weapon][element][0] += extra_dmg * self.weapon_dmg[weapon]["Physical"]
                            self.weapon_dmg[weapon][element][1] += extra_dmg * self.weapon_dmg[weapon]["Physical"]
                    else:
                        self.weapon_dmg[weapon][element][0] *= cal_effect["Physical Damage Effect"]
                        self.weapon_dmg[weapon][element][1] *= cal_effect["Physical Damage Effect"]

            # self.sight += cal_status["Sight Bonus"]
            # self.hidden += cal_status["Hidden Bonus"]
            self.crit_effect *= cal_effect["Critical Effect"]
            if cal_effect["Area of Effect"] in (2, 3):  # TODO maybe change skill system to have attack type
                self.special_effect[0]["All Side Full Attack"][1] = True
                if cal_effect["Area of Effect"] == 3:
                    self.corner_atk = True  # if aoe 3 mean it can melee_attack enemy on all side

            if 0 not in cal_effect["Status"]:  # apply status to friendly if there is one in skill effect
                for effect in cal_effect["Status"]:
                    self.status_effect[effect] = self.status_list[effect].copy()
                    if self.status_effect[effect][2] > 1:
                        self.apply_status_to_friend(self.status_effect[effect][2], effect, self.status_list)

            self.bonus_morale_dmg += cal_effect["Morale Damage Bonus"]
            self.bonus_stamina_dmg += cal_effect["Stamina Damage Bonus"]
            if 0 not in cal_effect["Enemy Status"]:  # apply status effect to enemy from skill to inflict list
                for effect in cal_effect["Enemy Status"]:
                    if effect != 0:
                        self.inflict_status[effect] = cal_effect["Area of Effect"]
        if 0 in self.skill_effect:
            self.auth_penalty += 0.5  # higher authority penalty when attacking (retreat while attacking)

    # Apply effect and modifier from status effect
    if len(self.status_effect) > 0:
        for effect in self.status_effect:
            cal_effect = self.status_list[effect]
            self.melee_attack = self.melee_attack * cal_effect["Melee Attack Effect"]
            self.melee_def = self.melee_def * cal_effect["Melee Defence Effect"]
            self.range_def = self.range_def * cal_effect["Ranged Defence Effect"]
            self.speed = self.speed * cal_effect["Speed Effect"]
            self.accuracy = self.accuracy * cal_effect["Accuracy Effect"]
            self.reload = self.reload / cal_effect["Reload Effect"]
            self.charge = self.charge * cal_effect["Charge Effect"]
            self.charge_def += cal_effect["Charge Defence Bonus"]
            self.hp_regen += cal_effect["HP Regeneration Bonus"]
            self.stamina_regen += cal_effect["Stamina Regeneration Bonus"]
            self.morale = self.morale + (cal_effect["Morale Bonus"] * self.mental)
            self.discipline += cal_effect["Discipline Bonus"]
            # self.sight += cal_status["Sight Bonus"]
            # self.hidden += cal_status["Hidden Bonus"]
            temp_reach += cal_effect["Temperature Change"]
            for element in self.element_resistance:  # Weather can cause elemental effect such as wet
                self.element_resistance[element] += cal_effect[element + " Resistance Bonus"]
            for effect in cal_effect["Special Effect"]:
                self.special_effect[effect][0][1] = True

    self.temperature_cal(temp_reach)  # calculate temperature and its effect

    self.element_effect_count()  # elemental effect

    self.morale_state = self.morale / self.max_morale  # for using as modifier to stat
    if self.morale_state > 3 or math.isnan(self.morale_state):  # morale state more than 3 give no more benefit
        self.morale_state = 3

    self.stamina_state = (self.stamina * 100) / self.max_stamina
    self.stamina_state_cal = 1
    if self.stamina != infinity:
        self.stamina_state_cal = self.stamina_state / 100  # for using as modifier to stat

    self.discipline = (self.discipline * self.morale_state * self.stamina_state_cal) + self.unit.leader_social[
        self.grade_name] + (self.authority / 10)  # use morale, stamina, leader social vs grade (+1 to skip class name) and authority
    self.melee_attack = (self.melee_attack * (self.morale_state + 0.1)) * self.stamina_state_cal + self.command_buff  # use morale, stamina and command buff
    self.melee_def = (self.melee_def * (
            self.morale_state + 0.1)) * self.stamina_state_cal + self.command_buff  # use morale, stamina and command buff
    self.range_def = (self.range_def * (self.morale_state + 0.1)) * self.stamina_state_cal + (
            self.command_buff / 2)  # use morale, stamina and half command buff
    self.accuracy = self.accuracy * self.stamina_state_cal + self.command_buff  # use stamina and command buff
    self.reload = self.reload * (2 - self.stamina_state_cal)  # the less stamina, the higher reload time
    self.charge_def = (self.charge_def * (
            self.morale_state + 0.1)) * self.stamina_state_cal + self.command_buff  # use morale, stamina and command buff
    height_diff = (self.height / self.front_height) ** 2  # walking down hill increase speed while walking up hill reduce speed
    self.speed = self.speed * self.stamina_state_cal * height_diff  # use stamina
    self.charge = (self.charge + self.speed) * (
            self.morale_state + 0.1) * self.stamina_state_cal + self.command_buff  # use morale, stamina and command buff

    full_merge_len = len(self.full_merge) + 1
    if full_merge_len > 1:  # reduce discipline if there are overlap subunit
        self.discipline = self.discipline / full_merge_len

    # Rounding up, add discipline to stat and forbid negative int stat
    discipline_cal = self.discipline / 200
    self.melee_attack = self.melee_attack + (self.melee_attack * discipline_cal)
    self.melee_def = self.melee_def + (self.melee_def * discipline_cal)
    self.range_def = self.range_def + (self.range_def * discipline_cal)
    self.speed = self.speed + (self.speed * discipline_cal / 2)
    # self.accuracy = self.accuracy
    # self.reload = self.reload
    self.charge_def = self.charge_def + (self.charge_def * discipline_cal)
    self.charge = self.charge + (self.charge * discipline_cal)

    if self.melee_attack < 0:  # seem like using if 0 is faster than max(0,)
        self.melee_attack = 0
    if self.melee_def < 0:
        self.melee_def = 0
    if self.range_def < 0:
        self.range_def = 0
    if self.speed < 1:
        self.speed = 1
        if 105 in self.status_effect:  # collapse state enforce 0 speed
            self.speed = 0
    if self.accuracy < 0:
        self.accuracy = 0
    if self.reload < 0:
        self.reload = 0
    if self.charge < 0:
        self.charge = 0
    if self.charge_def < 0:
        self.charge_def = 0
    if self.discipline < 0:
        self.discipline = 0

    self.weapon_speed[1] += ((50 - self.base_reload) * self.weapon_speed[1] / 100)  # final reload speed

    self.rotate_speed = self.unit.rotate_speed * 2  # rotate speed for subunit only use for self rotate not subunit rotate related
    if self.state in (0, 99):
        self.rotate_speed = self.speed

    # Cooldown, active and effect timer function
    self.skill_cooldown = {key: val - self.timer for key, val in self.skill_cooldown.items()}  # cooldown decrease overtime
    self.skill_cooldown = {key: val for key, val in self.skill_cooldown.items() if val > 0}  # remove cooldown if time reach 0
    self.idle_action = ()
    for key, value in self.skill_effect.items():  # Can't use dict comprehension here since value include all other skill stat
        value["Duration"] -= self.timer
        if key != 0 and ("hold" in value["Action"] or "repeat" in value["Action"]):
            self.idle_action = self.command_action

    self.skill_effect = {key: val for key, val in self.skill_effect.items() if
                         val["Duration"] > 0 and len(val["Restriction"]) > 0 and self.state in val["Restriction"]}  # remove effect if time reach 0 or restriction state is not met
    for a, b in self.status_effect.items():
        b["Duration"] -= self.timer

    # Remove status that reach 0 duration or status with conflict to the other status
    self.status_effect = {key: val for key, val in self.status_effect.items() if val["Duration"] > 0 or
                          any(ext in self.status_effect for ext in val["Status Conflict"]) is False}
