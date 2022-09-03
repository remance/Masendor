import csv
import os

import pygame
from gamescript.common import utility

stat_convert = utility.stat_convert

letter_board = (
"a", "b", "c", "d", "e", "f", "g", "h")  # letter according to subunit position in inspect ui similar to chess board
number_board = ("8", "7", "6", "5", "4", "3", "2", "1")  # same as above
board_pos = []
for dd in number_board:
    for ll in letter_board:
        board_pos.append(ll + dd)


def setup_battle_unit(self, team_unit_list, troop_list, specific_team=None):
    """
    Read unit battle data from unit_pos file
    :param self: Battle or Game object
    :param team_unit_list: List of team unit group, can be list for preview or dict for battle
    :param troop_list: Troop_list from troop data
    :param specific_team: Assign the unit to which specific team
    """
    from gamescript import unit
    team_colour = unit.team_colour

    main_dir = self.main_dir

    with open(os.path.join(main_dir, "data", "ruleset", self.ruleset_folder, "map",
                           self.map_selected, str(self.map_source),
                           self.genre, "unit_pos.csv"), encoding="utf-8", mode="r") as unit_file:
        rd = csv.reader(unit_file, quoting=csv.QUOTE_ALL)
        rd = [row for row in rd]
        header = rd[0]
        int_column = ["ID", "Faction", "Team"]  # value int only
        list_column = [item for item in header if "Row " in item] + ["POS", "Leader",
                                                                     "Leader Position"]  # value in list only
        float_column = ["Angle", "Start Health", "Start Stamina"]  # value in float
        int_column = [index for index, item in enumerate(header) if item in int_column]
        list_column = [index for index, item in enumerate(header) if item in list_column]
        float_column = [index for index, item in enumerate(header) if item in float_column]
        subunit_game_id = 1
        for this_unit in rd[1:]:  # skip header
            for n, i in enumerate(this_unit):
                this_unit = stat_convert(this_unit, n, i, list_column=list_column, int_column=int_column,
                                         float_column=float_column)
            this_unit = {header[index]: stuff for index, stuff in enumerate(this_unit)}
            for key, value in this_unit.items():  # convert int troop id to str for compatibility
                if "Row " in key:
                    this_unit[key] = [str(item) for item in value]
            if specific_team is None or specific_team == this_unit["Team"]:  # check player control
                control = False
                if self.team_selected == this_unit["Team"] or self.enactment:
                    control = True

                colour = team_colour[this_unit["Team"]]
                if type(team_unit_list) == dict:
                    if this_unit["Team"] not in team_unit_list:
                        team_unit_list[this_unit["Team"]] = pygame.sprite.Group()
                    which_team = team_unit_list[this_unit["Team"]]
                else:  # for character selection
                    which_team = team_unit_list

                command = False  # Not commander unit by default
                if len(which_team) == 0:  # First unit is commander
                    command = True
                coa = pygame.transform.scale(self.faction_data.coa_list[this_unit["Faction"]],
                                             (60, 60))  # get coa_list image and scale smaller to fit ui
                subunit_game_id = self.generate_unit(which_team, this_unit, control, command, colour, coa,
                                                     subunit_game_id, troop_list)
                # ^ End subunit setup

    unit_file.close()
