import math

infinity = float("inf")


def status_update(self, weather=None):
    """calculate stat from stamina, morale state, skill, status, terrain"""

    if self.red_border and self.unit.selected:  # have red border (taking melee_dmg) on inspect ui, reset image
        self.block.blit(self.block_original, self.corner_image_rect)
        self.red_border = False

    # v reset stat to default and apply morale, stamina, command buff to stat
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
    self.shoot_range = self.base_range

    self.crit_effect = 1  # default critical effect
    self.front_dmg_effect = 1  # default frontal melee_dmg
    self.side_dmg_effect = 1  # default side melee_dmg

    self.corner_atk = False  # cannot melee_attack corner enemy by default
    self.temp_full_def = False

    self.auth_penalty = self.base_auth_penalty
    self.hp_regen = self.base_hp_regen
    self.stamina_regen = self.base_stamina_regen
    self.inflict_status = self.base_inflict_status
    self.elem_melee = self.base_elem_melee
    self.elem_range = self.base_elem_range
    # ^ End default stat

    # v Apply status effect from trait
    if len(self.trait) > 1:
        for trait in self.trait.values():
            if 0 not in trait["Status"]:  # 0 value means no trait or not use
                for effect in trait["Status"]:  # apply status effect from trait
                    self.status_effect[effect] = self.status_list[effect].copy()
                    if trait["Buff Range"] > 1:  # status buff range to nearby friend
                        self.apply_status_to_friend(trait[1], effect, self.status_list[effect].copy())
    # ^ End trait

    # v apply effect from weather"""
    weather_temperature = 0
    if weather is not None:
        self.melee_attack += weather.melee_atk_buff
        self.melee_def += weather.melee_def_buff
        self.range_def += weather.range_def_buff
        # self.armour += weather.armour_buff
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
        if weather.elem[0] != 0:  # Weather can cause elemental effect such as wet
            self.elem_count[weather.elem[0]] += (weather.elem[1] * (100 - self.elem_res[weather.elem[0]]) / 100)
        weather_temperature = weather.temperature
    # ^ End weather

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
    # ^ End map feature

    # v Apply effect from skill
    # For list of status and skill effect column index used in status_update see script_other.py load_game_data()
    if len(self.skill_effect) > 0:
        for status in self.skill_effect:  # apply elemental effect to melee_dmg if skill has element
            cal_status = self.skill_effect[status]
            if cal_status["Type"] == 0 and cal_status["Element"] != 0:  # melee elemental effect
                self.elem_melee = cal_status["Element"]
            elif cal_status["Type"] == 1 and cal_status["Element"] != 0:  # range elemental effect
                self.elem_range = cal_status["Element"]
            self.melee_attack = self.melee_attack * cal_status["Melee Attack Effect"]
            self.melee_def = self.melee_def * cal_status["Melee Defence Effect"]
            self.range_def = self.range_def * cal_status["Ranged Defence Effect"]
            self.speed = self.speed * cal_status["Speed Effect"]
            self.accuracy = self.accuracy * cal_status["Accuracy Effect"]
            for shoot_range in self.shoot_range:
                shoot_range *= cal_status["Range Effect"]
            self.reload = self.reload / cal_status[
                "Reload Effect"]  # different from other modifier the higher mod reduce reload time (decrease stat)
            self.charge = self.charge * cal_status["Charge Effect"]
            self.charge_def = self.charge_def + cal_status["Charge Defence Bonus"]
            self.hp_regen += cal_status["HP Regeneration Bonus"]
            self.stamina_regen += cal_status["Stamina Regeneration Bonus"]
            self.morale = self.morale + (cal_status["Morale Bonus"] * self.mental)
            self.discipline = self.discipline + cal_status["Discipline Bonus"]
            # self.sight += cal_status["Sight Bonus"]
            # self.hidden += cal_status["Hidden Bonus"]
            self.crit_effect = self.crit_effect * cal_status["Critical Effect"]
            self.front_dmg_effect = self.front_dmg_effect * cal_status["Damage Effect"]
            if cal_status["Area of Effect"] in (2, 3) and cal_status["Damage Effect"] != 100:
                self.side_dmg_effect = self.side_dmg_effect * cal_status["Damage Effect"]
                if cal_status["Area of Effect"] == 3:
                    self.corner_atk = True  # if aoe 3 mean it can melee_attack enemy on all side

            # v Apply status to friendly if there is one in skill effect
            if 0 not in cal_status["Status"]:
                for effect in cal_status["Status"]:
                    self.status_effect[effect] = self.status_list[effect].copy()
                    if self.status_effect[effect][2] > 1:
                        self.apply_status_to_friend(self.status_effect[effect][2], effect, self.status_list)
            # ^ End apply status to

            self.bonus_morale_dmg += cal_status["Morale Damage"]
            self.bonus_stamina_dmg += cal_status["Stamina Damage"]
            if 0 not in cal_status["Enemy Status"]:  # Apply status effect to enemy from skill to inflict list
                for effect in cal_status["Enemy Status"]:
                    if effect != 0:
                        self.inflict_status[effect] = cal_status["Area of Effect"]
        if 0 in self.skill_effect:
            self.auth_penalty += 0.5  # higher authority penalty when attacking (retreat while charging)
    # ^ End skill effect

    # v Apply effect and modifier from status effect
    # """special status: 0 no control, 1 hostile to all, 2 no retreat, 3 no terrain effect, 4 no melee_attack, 5 no skill, 6 no spell, 7 no exp gain,
    # 7 immune to bad mind, 8 immune to bad body, 9 immune to all effect, 10 immortal""" Not implemented yet
    if len(self.status_effect) > 0:
        for status in self.status_effect:
            cal_status = self.status_list[status]
            self.melee_attack = self.melee_attack * cal_status["Melee Attack Effect"]
            self.melee_def = self.melee_def * cal_status["Melee Defence Effect"]
            self.range_def = self.range_def * cal_status["Ranged Defence Effect"]
            self.armour = self.armour * cal_status["Armour Effect"]
            self.speed = self.speed * cal_status["Speed Effect"]
            self.accuracy = self.accuracy * cal_status["Accuracy Effect"]
            self.reload = self.reload / cal_status["Reload Effect"]
            self.charge = self.charge * cal_status["Charge Effect"]
            self.charge_def += cal_status["Charge Defence Bonus"]
            self.hp_regen += cal_status["HP Regeneration Bonus"]
            self.stamina_regen += cal_status["Stamina Regeneration Bonus"]
            self.morale = self.morale + (cal_status["Morale Bonus"] * self.mental)
            self.discipline += cal_status["Discipline Bonus"]
            # self.sight += cal_status["Sight Bonus"]
            # self.hidden += cal_status["Hidden Bonus"]
            temp_reach += cal_status["Temperature Change"]
            if status == 91:  # All round defence status
                self.temp_full_def = True
    # ^ End status effect

    self.temperature_cal(temp_reach)  # calculate temperature and its effect

    # v Elemental effect, Apply effect if elem threshold reach 50 or 100
    self.elem_count[0] = self.element_threshold_count(self.elem_count[0], 28, 92)
    self.elem_count[1] = self.element_threshold_count(self.elem_count[1], 31, 93)
    self.elem_count[2] = self.element_threshold_count(self.elem_count[2], 30, 94)
    self.elem_count[3] = self.element_threshold_count(self.elem_count[3], 23, 35)
    self.elem_count[4] = self.element_threshold_count(self.elem_count[4], 26, 27)
    self.elem_count = {key: value - self.timer if value > 0 else value for key, value in self.elem_count.items()}
    # ^ End elemental effect

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

    # v Rounding up, add discipline to stat and forbid negative int stat
    discipline_cal = self.discipline / 200
    self.melee_attack = self.melee_attack + (self.melee_attack * discipline_cal)
    self.melee_def = self.melee_def + (self.melee_def * discipline_cal)
    self.range_def = self.range_def + (self.range_def * discipline_cal)
    # self.armour = self.armour
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
    if self.armour < 1:  # Armour cannot be lower than 1
        self.armour = 1
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
    # ^ End rounding up

    self.rotate_speed = self.unit.rotate_speed * 2  # rotate speed for subunit only use for self rotate not subunit rotate related
    if self.state in (0, 99):
        self.rotate_speed = self.speed

    # v cooldown, active and effect timer function
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
    self.status_effect = {key: val for key, val in self.status_effect.items() if val["Duration"] > 0}
