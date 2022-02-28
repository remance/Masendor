import csv
import os
import pygame


def editor_map_change(self, base_colour, feature_colour):
    map_images = (pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000), pygame.SRCALPHA), None)
    map_images[0].fill(base_colour)  # start with temperate terrain
    map_images[1].fill(feature_colour)  # start with plain feature
    map_images[2].fill((255, 100, 100, 125))  # start with height 100 plain

    self.battle_map_base.draw_image(map_images[0])
    self.battle_map_feature.draw_image(map_images[1])
    self.battle_map_height.draw_image(map_images[2])
    self.show_map.draw_image(self.battle_map_base, self.battle_map_feature, self.battle_map_height, None, self, True)
    self.mini_map.draw_image(self.show_map.true_image, self.camera)
    self.show_map.change_scale(self.camera_scale)

    for subunit in self.subunit_build:
        subunit.terrain, subunit.feature = subunit.get_feature((500, 500), self.battle_map_base)
        subunit.height = self.battle_map_height.get_height((500,500))


def save_preset(self):
    with open(os.path.join("profile", "unitpreset", str(self.ruleset), "custom_unitpreset.csv"), "w", encoding='utf-8', newline="") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        save_list = self.custom_unit_preset_list.copy()
        del save_list["New Preset"]
        final_save = [["presetname", "subunitline1", "subunitline2", "subunitline3", "subunitline4", "subunitline5", "subunitline6",
                       "subunitline7", "subunitline8", "leader", "leaderposition", "faction"]]
        for item in list(save_list.items()):
            sub_item = [small_item for small_item in item[1]]
            item = [item[0]] + sub_item
            final_save.append(item)
        for row in final_save:
            filewriter.writerow(row)
        csvfile.close()


def convert_slot_dict(self, name, pos=None, add_id=None):
    current_preset = [[], [], [], [], [], [], [], []]
    start_item = 0
    subunit_count = 0
    for slot in self.subunit_build:  # add subunit troop id
        current_preset[int(start_item / 8)].append(str(slot.troop_id))
        start_item += 1
        if slot.troop_id != 0:
            subunit_count += 1
    if pos is not None:
        current_preset.append(pos)

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
        current_preset.append(leader_list)
        current_preset.append(leader_pos_list)

        faction = []  # generate faction list that can use this unit
        faction_list = self.faction_data.faction_list.copy()
        del faction_list["ID"]
        del faction_list[0]
        faction_count = dict.fromkeys(faction_list.keys(), 0)  # dict of faction occurrence count

        for index, item in enumerate(current_preset):
            for this_item in item:
                if index in range(0, 8):  # subunit
                    for faction_item in faction_list.items():
                        if int(this_item) in faction_item[1]["Troop"]:
                            faction_count[faction_item[0]] += 1
                elif index == 8:  # leader
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
        current_preset.append(faction)

        for item_index, item in enumerate(current_preset):  # convert list to string
            if type(item) == list:
                if len(item) > 1:
                    current_preset[item_index] = ",".join(item)
                else:  # still type list because only one item in list
                    current_preset[item_index] = str(current_preset[item_index][0])
        if add_id is not None:
            current_preset = [add_id] + current_preset
        current_preset = {name: current_preset}
    else:
        current_preset = None

    return current_preset


def preview_authority(self, leader_list):
    """Calculate authority of editing unit"""
    authority = int(
        leader_list[0].authority + (leader_list[0].authority / 2) +
        (leader_list[1].authority / 4) + (leader_list[2].authority / 4) +
        (leader_list[3].authority / 10))
    big_unit_size = len([slot for slot in self.subunit_build if slot.name != "None"])
    if big_unit_size > 20:  # army size larger than 20 will reduce start_set leader authority
        authority = int(leader_list[0].authority +
                        (leader_list[0].authority / 2 * (100 - big_unit_size) / 100) +
                        leader_list[1].authority / 2 + leader_list[2].authority / 2 +
                        leader_list[3].authority / 4)

    for slot in self.subunit_build:
        slot.authority = authority

    if self.show_in_card is not None:
        self.command_ui.value_input(who=self.unit_build_slot)
    # ^ End cal authority


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
