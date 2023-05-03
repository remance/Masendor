from engine.common.battle import setup_battle_ui

add_skill_icon = setup_battle_ui.add_skill_icon


def process_trait_skill(self):
    """
    Process unit traits and skills into dict with their stat, occur in swap_weapon
    :param self: Unit object
    """
    for equip in self.trait["Weapon"]:  # covert trait index to data
        for key in self.trait["Weapon"][equip]:  # covert trait index to data
            self.trait["Weapon"][equip][key] = {x: self.troop_data.trait_list[x] for x in
                                                self.trait["Weapon"][equip][key] if x in self.troop_data.trait_list}
    self.add_weapon_trait()

    for index, status_head in enumerate(("Status", "Enemy Status")):
        trait_status_dict = (self.trait_ally_status, self.trait_enemy_status)[index]

        for equip in self.trait["Weapon"]:
            for weapon in self.trait["Weapon"][equip]:
                for trait in self.trait["Weapon"][equip][weapon].values():
                    for status in trait[status_head]:
                        if status not in trait_status_dict["Weapon"]:
                            trait_status_dict["Weapon"][status] = trait["Area Of Effect"]
                        elif trait_status_dict["Weapon"][status] < trait["Area Of Effect"]:  # replace aoe that larger
                            trait_status_dict["Weapon"][status] = trait["Area Of Effect"]

        trait_status_dict["Final"] = trait_status_dict["Original"].copy()
        for status in trait_status_dict["Weapon"]:
            if status not in trait_status_dict["Final"] or \
                    trait_status_dict["Final"][status] < trait_status_dict["Weapon"][status]:
                trait_status_dict["Final"][status] = trait_status_dict["Weapon"][status]

    self.skill = skill_convert(self, self.skill, add_charge_skill=True)
    self.input_skill = self.skill.copy()
    self.input_skill.pop(self.charge_skill)

    self.available_skill = [skill for skill in self.input_skill if skill not in self.skill_cooldown
                            and self.discipline >= self.input_skill[skill]["Discipline Requirement"]
                            and self.stamina > self.input_skill[skill]["Stamina Cost"] and
                            ("skill" not in self.current_action or self.current_action["skill"] != skill)]

    self.target_skill = {key: value for key, value in self.input_skill.items() if value["Type"] == "Target"}
    self.weapon_skill = {key: value for key, value in self.weapon_skill.items() if value in self.skill}

    ai_skill_condition_list = {"move": [], "melee": [], "range": [], "enemy_near": [], "damaged": [], "retreat": [],
                               "idle": [], "unit_melee": [], "unit_range": [], "troop_melee": [], "troop_range": [],
                               "move_far": []}
    for key, value in self.input_skill.items():
        for condition in value["AI Use Condition"]:
            ai_skill_condition_list[condition].append(key)

    self.move_skill = ai_skill_condition_list["move"]
    self.melee_skill = ai_skill_condition_list["melee"]
    self.range_skill = ai_skill_condition_list["range"]
    self.enemy_near_skill = ai_skill_condition_list["enemy_near"]
    self.damaged_skill = ai_skill_condition_list["damaged"]
    self.retreat_skill = ai_skill_condition_list["retreat"]
    self.idle_skill = ai_skill_condition_list["idle"]

    if self.is_leader:
        self.unit_melee_skill = ai_skill_condition_list["unit_melee"]
        self.troop_melee_skill = ai_skill_condition_list["troop_melee"]
        self.unit_range_skill = ai_skill_condition_list["unit_range"]
        self.troop_range_skill = ai_skill_condition_list["troop_range"]
        self.move_far_skill = ai_skill_condition_list["move_far"]

    if self.player_control:  # change skill ui
        add_skill_icon(self.battle)


def skill_convert(self, skill_list, add_charge_skill=False):
    """
    Convert skill id list to dict with its stat
    :param self: Unit object
    :param skill_list: List of skill id
    :param add_charge_skill: Add charge skill to dict or not
    :return: Dict of skill with id as key and stat as value
    """
    skill_dict = tuple(set(skill_list))

    # Grab skill stat into dict
    troop_skill_dict = {x: self.troop_data.skill_list[x] for x in skill_dict if x in self.troop_data.skill_list}

    troop_skill_dict = {skill: troop_skill_dict[skill] for skill in troop_skill_dict if
                        ((self.troop_data.skill_list[skill]["Troop Type"] == 0 or
                          self.troop_data.skill_list[skill][
                              "Troop Type"] == self.unit_type))}  # keep skill if class match

    skill_dict = troop_skill_dict | self.leader_skill

    if add_charge_skill:
        skill_dict[self.charge_skill] = self.troop_data.skill_list[
            self.charge_skill]  # add charge skill

    return skill_dict
