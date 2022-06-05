def process_trait_skill(self):
    """
    Process subunit traits and skills into dict with their stat
    :param self: Subunit object
    """
    self.trait += self.armour_data.armour_list[self.armour_gear[0]]["Trait"]  # Apply armour trait to subunit
    self.trait = list(set([trait for trait in self.trait if trait != 0]))  # remove empty and duplicate traits
    if len(self.trait) > 0:
        self.trait = {x: self.troop_data.trait_list[x] for x in self.trait if
                      x in self.troop_data.trait_list}  # Any trait not available in ruleset will be ignored
        self.add_trait()

    for weapon_set in self.weapon_skill:
        for weapon in self.weapon_skill[weapon_set]:
            skill = self.weapon_skill[weapon_set][weapon]
            if skill != 0 and (self.troop_data.skill_list[skill]["Troop Type"] != 0 and
                               self.troop_data.skill_list[skill]["Troop Type"] != self.subunit_type + 1):
                self.weapon_skill[weapon_set][weapon] = 0  # remove unmatch class skill
            else:
                self.skill.append(skill)
    self.skill = skill_convert(self, self.skill, add_charge_skill=True)


def skill_convert(self, skill_list, add_charge_skill=False):
    """
    Convert skill id list to dict with its stat
    :param self: Subunit object
    :param skill_list: List of skill id
    :param add_charge_skill: Add charge skill to dict or not
    :return: Dict of skill with id as key and stat as value
    """
    skill_dict = list(set(skill_list))
    skill_dict = {x: self.troop_data.skill_list[x].copy() for x in skill_dict if
                  x != 0 and x in self.troop_data.skill_list}  # grab skill stat into dict
    if add_charge_skill:
        skill_dict[0] = self.troop_data.skill_list[self.charge_skill].copy()  # add charge skill with key 0
    skill_dict = {skill: skill_dict[skill] for skill in skill_dict if skill == 0 or   # keep skill if class match
                  (skill != 0 and (self.troop_data.skill_list[skill]["Troop Type"] == 0 or
                                   self.troop_data.skill_list[skill]["Troop Type"] == self.subunit_type + 1))}

    leader_skill_dict = {x: self.leader_data.skill_list[x].copy() for x in skill_dict if x != 0 and x in self.leader_data.skill_list}
    skill_dict = skill_dict | leader_skill_dict

    return skill_dict
