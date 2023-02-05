def filter_troop_list(self):
    """Filter troop list based on faction picked and type filter"""
    if self.faction_pick != 0:  # pick specific faction
        self.troop_list = ["None"] + \
                          [value["Name"] for key, value in self.troop_data.troop_list.items()
                           if key in self.faction_data.faction_list[self.faction_pick]["Troop"]]
        self.troop_index_list = [0] + self.faction_data.faction_list[self.faction_pick]["Troop"]
        self.leader_list = ["None"] + [value["Name"] for key, value in self.leader_data.leader_list.items()
                                       if key in self.faction_data.faction_list[self.faction_pick]["Leader"]]

    else:  # pick all faction
        self.troop_list = ["None"] + [item["Name"] for item in self.troop_data.troop_list.values()]
        self.troop_index_list = list(range(0, len(self.troop_list)))

        self.leader_list = ["None"] + [value["Name"] for value in
                                       self.leader_data.leader_list.values()]

    for this_unit in self.troop_index_list[::-1]:
        if this_unit != 0:
            if self.filter_troop[0] is False:  # filter out melee infantry
                if self.troop_data.troop_list[this_unit]["Troop Class"] in ("Heavy Infantry", "Light Infantry"):
                    self.troop_list.pop(self.troop_index_list.index(this_unit))
                    self.troop_index_list.remove(this_unit)

            if self.filter_troop[1] is False:  # filter out range infantry
                if self.troop_data.troop_list[this_unit]["Troop Class"] in ("Range Infantry", "Artillery"):
                    self.troop_list.pop(self.troop_index_list.index(this_unit))
                    self.troop_index_list.remove(this_unit)

            if self.filter_troop[2] is False:  # filter out melee cav
                if self.troop_data.troop_list[this_unit]["Troop Class"] in ("Heavy Cavalry", "Light Cavalry", "Chariot"):
                    self.troop_list.pop(self.troop_index_list.index(this_unit))
                    self.troop_index_list.remove(this_unit)

            if self.filter_troop[3] is False:  # filter out range cav
                if self.troop_data.troop_list[this_unit]["Troop Class"] in ("Range Cavalry",):
                    self.troop_list.pop(self.troop_index_list.index(this_unit))
                    self.troop_index_list.remove(this_unit)
