def process_trait_skill(self):
    """
    Process subunit traits and skills into dict with their stat, occur in swap_weapon
    :param self: Subunit object
    """
    for equip in self.trait["Weapon"]:  # covert trait index to data
        for key in self.trait["Weapon"][equip]:  # covert trait index to data
            self.trait["Weapon"][equip][key] = {x: self.troop_data.trait_list[x] for x in
                                                self.trait["Weapon"][equip][key] if x in self.troop_data.trait_list}
    self.add_weapon_trait()
    self.skill = skill_convert(self, self.skill, add_charge_skill=True)
    self.input_skill = self.skill.copy()
    self.input_skill.pop(self.charge_skill)


def skill_convert(self, skill_list, add_charge_skill=False):
    """
    Convert skill id list to dict with its stat
    :param self: Subunit object
    :param skill_list: List of skill id
    :param add_charge_skill: Add charge skill to dict or not
    :return: Dict of skill with id as key and stat as value
    """
    skill_dict = tuple(set(skill_list))

    # Grab skill stat into dict
    troop_skill_dict = {x: self.troop_data.skill_list[x] for x in skill_dict if x in self.troop_data.skill_list}

    troop_skill_dict = {skill: troop_skill_dict[skill] for skill in troop_skill_dict if
                        ((self.troop_data.skill_list[skill]["Troop Type"] == 0 or
                          self.troop_data.skill_list[skill]["Troop Type"] == self.subunit_type))}  # keep skill if class match

    skill_dict = troop_skill_dict | self.leader_skill

    if add_charge_skill:
        skill_dict[self.charge_skill] = self.troop_data.skill_list[
            self.charge_skill]  # add charge skill

    return skill_dict
