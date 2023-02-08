def add_mount_stat(self):
    """Combine mount stat"""
    mount_race_stat = self.troop_data.race_list[self.mount["Race"]]
    mount_size = mount_race_stat["Size"]
    # self.race_name += "&" + self.troop_data.race_list[race_id]["Name"]
    if mount_size > self.troop_size:  # replace size if mount is larger
        self.troop_size = mount_size

    if self.mount["Type"] == "Combat Equipment":  # Not exactly mount but weapon like artillery
        self.original_charge_def = 10
        self.subunit_type = 1  # count as range infantry for command buff
        self.feature_mod = "Infantry"  # Use cavalry type for terrain bonus
    else:
        self.original_charge_def = 25  # charge defence only 25 for cav
        self.original_speed = (mount_race_stat["Agility"] / 5) + (
                    self.mount["Speed Bonus"] + self.mount_grade["Speed Bonus"])  # use mount base speed instead
        self.subunit_type = 2  # count as cav for command buff
        self.feature_mod = "Cavalry"  # Use cavalry type for terrain bonus

    self.health += (self.mount["Health Bonus"] * self.mount_grade["Health Effect"]) + \
                   self.mount_armour["Health"]  # Add mount health to the troop health
    self.original_morale += self.mount_grade["Morale Bonus"]
    self.original_charge += (self.mount["Charge Bonus"] +
                             self.mount_grade["Charge Bonus"])  # Add charge power of mount to troop
    self.original_discipline += self.mount_grade["Discipline Bonus"]
    self.stamina += self.mount["Stamina Bonus"]
    self.trait["Original"] += self.mount["Trait"]  # Apply mount trait to subunit

