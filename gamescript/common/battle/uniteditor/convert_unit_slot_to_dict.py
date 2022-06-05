def convert_unit_slot_to_dict(self, name, pos=None, add_id=None):
    current_preset = {"Row 1": [], "Row 2": [], "Row 3": [], "Row 4": [],
                      "Row 5": [], "Row 6": [], "Row 7": [], "Row 8": [], }
    start_item = 8
    subunit_count = 0
    for slot in self.subunit_build:  # add subunit troop id
        current_preset["Row " + str(int(start_item / 8))].append(str(slot.troop_id))
        start_item += 1
        if slot.troop_id != 0:
            subunit_count += 1
    if pos is not None:
        current_preset["POS"] = pos

    if subunit_count > 0:
        leader_list = []
        leader_pos_list = []
        for this_leader in self.preview_leader:  # add leader id
            count_zero = 0
            if this_leader.leader_id != 1:
                subunit_count += 1
                for slot_index, slot in enumerate(self.subunit_build):  # add subunit troop id
                    if slot.troop_id == 0:
                        count_zero += 1
                    if slot_index == this_leader.subunit_pos:
                        break

            leader_list.append(str(this_leader.leader_id))
            leader_pos_list.append(str(this_leader.subunit_pos - count_zero))
        current_preset["Leader"] = leader_list
        current_preset["Leader Position"] = leader_pos_list

        faction = []  # generate faction list that can use this unit
        faction_list = self.faction_data.faction_list.copy()
        del faction_list["ID"]
        del faction_list[0]
        faction_count = dict.fromkeys(faction_list.keys(), 0)  # dict of faction occurrence count

        for key, value in current_preset.items():
            for this_item in value:
                if "Row " in key:  # subunit
                    for faction_item in faction_list.items():
                        if int(this_item) in faction_item[1]["Troop"]:
                            faction_count[faction_item[0]] += 1
                elif key == "Leader":  # leader
                    for faction_item in faction_list.items():
                        if int(this_item) < 10000 and int(this_item) in faction_item[1]["Leader"]:
                            faction_count[faction_item[0]] += 1
                        elif int(this_item) >= 10000:
                            if faction_item[0] == self.leader_data.leader_list[int(this_item)]["Faction"] or \
                                    self.leader_data.leader_list[int(this_item)]["Faction"] == 0:
                                faction_count[faction_item[0]] += 1

        for item in faction_count.items():  # find faction of this unit
            if item[1] == faction_count[max(faction_count, key=faction_count.get)]:
                if faction_count[max(faction_count, key=faction_count.get)] == subunit_count:
                    faction.append(item[0])
                else:  # units from various factions, counted as multi-faction unit
                    faction = [0]
                    break
        current_preset["Faction"] = faction

        for key, value in enumerate(current_preset.items()):  # convert list to string
            if type(value) == list:
                if len(value) > 1:
                    current_preset[key] = ",".join(value)
                else:  # still type list because only one item in list
                    current_preset[key] = str(value[0])
        if add_id is not None:
            current_preset["ID"] = add_id
        current_preset = {name: current_preset}
    else:
        current_preset = None

    return current_preset

