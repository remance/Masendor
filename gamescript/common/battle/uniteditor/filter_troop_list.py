def filter_troop_list(self):
    """Filter troop list based on faction picked and type filter"""
    if self.faction_pick != 0:
        self.troop_list = [value["Name"] for key, value in self.troop_data.troop_list.items()
                           if value["Name"] == "None" or
                           key in self.faction_data.faction_list[self.faction_pick]["Troop"]]
        self.troop_index_list = [0] + self.faction_data.faction_list[self.faction_pick]["Troop"]

    else:  # pick all faction
        self.troop_list = [item["Name"] for item in self.troop_data.troop_list.values()][1:]
        self.troop_index_list = list(range(0, len(self.troop_list)))

    for this_unit in self.troop_index_list[::-1]:
        if this_unit != 0:
            if self.filter_troop[0] is False:  # filter out melee infantry
                if self.troop_data.troop_list[this_unit]["Melee Attack"] > self.troop_data.troop_list[this_unit]["Accuracy"] and \
                        self.troop_data.troop_list[this_unit]["Mount"] == [1, 0, 1]:
                    self.troop_list.pop(self.troop_index_list.index(this_unit))
                    self.troop_index_list.remove(this_unit)

            if self.filter_troop[1] is False:  # filter out range infantry
                if self.troop_data.troop_list[this_unit]["Melee Attack"] < self.troop_data.troop_list[this_unit]["Accuracy"] and \
                        self.troop_data.troop_list[this_unit]["Mount"] == [1, 0, 1]:
                    self.troop_list.pop(self.troop_index_list.index(this_unit))
                    self.troop_index_list.remove(this_unit)

            if self.filter_troop[2] is False:  # filter out melee cav
                if self.troop_data.troop_list[this_unit]["Melee Attack"] > self.troop_data.troop_list[this_unit]["Accuracy"] and \
                        self.troop_data.troop_list[this_unit]["Mount"] != [1, 0, 1]:
                    self.troop_list.pop(self.troop_index_list.index(this_unit))
                    self.troop_index_list.remove(this_unit)

            if self.filter_troop[3] is False:  # filter out range cav
                if self.troop_data.troop_list[this_unit]["Melee Attack"] < self.troop_data.troop_list[this_unit]["Accuracy"] and \
                        self.troop_data.troop_list[this_unit]["Mount"] != [1, 0, 1]:
                    self.troop_list.pop(self.troop_index_list.index(this_unit))
                    self.troop_index_list.remove(this_unit)
