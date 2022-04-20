def process_trait_skill(self):
    self.trait += self.armour_data.armour_list[self.armour_gear[0]]["Trait"]  # Apply armour trait to subunit
    self.trait = list(set([trait for trait in self.trait if trait != 0]))  # remove empty and duplicate traits
    if len(self.trait) > 0:
        self.trait = {x: self.troop_data.trait_list[x] for x in self.trait if
                      x in self.troop_data.trait_list}  # Any trait not available in ruleset will be ignored
        self.add_trait()

    self.skill = list(set(self.skill))
    self.skill = {x: self.troop_data.skill_list[x].copy() for x in self.skill if
                  x != 0 and x in self.troop_data.skill_list}  # grab skill stat into dict
    self.skill[0] = self.troop_data.skill_list[self.charge_skill].copy()  # add charge skill with key 0
    for skill in list(self.skill.keys()):  # remove skill if class mismatch
        skill_troop_cond = self.skill[skill]["Troop Type"]
        if skill_troop_cond != 0 and self.subunit_type != skill_troop_cond:
            self.skill.pop(skill)
