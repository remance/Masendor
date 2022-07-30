def add_mount_stat(self):
    """Combine mount stat"""
    mount_size = self.troop_data.race_list[self.mount["Race"]]["Size"]
    # self.race_name += "&" + self.troop_data.race_list[race_id]["Name"]
    if mount_size > self.size:  # replace size if mount is larger
        self.size = mount_size

    self.original_charge_def = 25  # charge defence only 25 for cav
    self.original_speed = (self.mount["Speed"] + self.mount_grade["Speed Bonus"])  # use mount base speed instead
    self.troop_health += (self.mount["Health Bonus"] * self.mount_grade["Health Effect"]) + \
                         self.mount_armour["Health"]  # Add mount health to the troop health
    self.original_charge += (self.mount["Charge Bonus"] +
                         self.mount_grade["Charge Bonus"])  # Add charge power of mount to troop
    self.original_morale += self.mount_grade["Morale Bonus"]
    self.original_discipline += self.mount_grade["Discipline Bonus"]
    self.stamina += self.mount["Stamina Bonus"]
    self.trait["Original"] += self.mount["Trait"]  # Apply mount trait to subunit
    self.subunit_type = 2  # If subunit has a mount, count as cav for command buff
    self.feature_mod = "Cavalry"  # Use cavalry type for terrain bonus

