import csv
import os

from engine.unit import unit
from engine import utility

stat_convert = utility.stat_convert


def setup_battle_unit(self, team_unit_list, preview=None):
    """
    Read unit data in battle from unit_pos file
    :param self: Battle or Game object
    :param team_unit_list: List of team unit group, can be list for preview or dict for battle
    :param preview: Preview unit of a specific team
    :param custom_data: Use custom battle data instead of read from preset map data
    """
    leader_unit = {}
    self.last_troop_game_id = 0

    troop_data = self.map_data[self.map_source]["unit"]

    new_troop_data = []  # rearrange data list to ensure that leader units are made first
    for data in troop_data:  # unit leader first
        if data["Leader"] == 0:
            new_troop_data.append(data)

    for data in troop_data:  # leader with followers next
        if data["Leader"]:
            leader = [troop for troop in troop_data if troop["ID"] == data["Leader"]][0]
            if leader not in new_troop_data:
                new_troop_data.append(leader)

    for data in troop_data:  # move leader with no follower to last in list
        if data not in new_troop_data:
            new_troop_data.append(data)

    for data in new_troop_data:
        if not preview or preview == data["Team"]:  # check if create unit only for preview of a specific team
            troop_number_list = {key: [int(num) for num in value.split("/")] for key, value in
                                 data["Troop"].items()}

            if preview:  # make only leader for preview
                team_unit_list.add(unit.PreviewUnit(data["Leader ID"], self.last_troop_game_id, data["ID"],
                                                    data["Team"], data["POS"], data["Angle"], data["Start Health"],
                                                    data["Start Stamina"], None,
                                                    self.faction_data.coa_list[data["Faction"]]))
            else:
                leader = None
                if data["Leader"] != 0 and leader_unit[data["Leader"]].team == data["Team"]:
                    # avoid different team leader assign, in case of data mistake
                    leader = leader_unit[data["Leader"]]

                add_leader = unit.Leader(data["Leader ID"], self.last_troop_game_id, data["ID"], data["Team"],
                                         data["POS"], data["Angle"], data["Start Health"], data["Start Stamina"],
                                         leader, self.faction_data.coa_list[data["Faction"]])
                add_leader.troop_reserve_list = {key: value[1] for key, value in troop_number_list.items()}
                add_leader.troop_dead_list = {key: 0 for key, value in troop_number_list.items()}

                leader_unit[data["ID"]] = add_leader  # leader unit
                self.last_troop_game_id += 1
                for key, value in troop_number_list.items():
                    for _ in range(value[0]):
                        unit.Troop(key, self.last_troop_game_id, None, data["Team"],
                                   data["POS"], data["Angle"], data["Start Health"], data["Start Stamina"], add_leader,
                                   self.faction_data.coa_list[data["Faction"]])
                        self.last_troop_game_id += 1
