import csv
import os

import pygame

from gamescript import statdata
from gamescript.common import animation

make_sprite = animation.make_sprite
stat_convert = statdata.stat_convert


def create_sprite_pool(self, direction_list, genre_sprite_size, screen_scale):  # TODO maybe add body pos and size for check collide?
    animation_sprite_pool = {}
    weapon_common_type_list = list(set(["_" + value["Common"] + "_" for value in self.generic_action_data.values()]))  # list of all common type animation set
    weapon_attack_type_list = list(set(["_" + value["Attack"] + "_" for value in self.generic_action_data.values()]))  # list of all attack set
    for this_subunit in self.subunit_updater:
        if this_subunit.troop_id not in animation_sprite_pool:
            animation_sprite_pool[this_subunit.troop_id] = {}
            armour = (self.armour_data.armour_list[this_subunit.armour_gear[0]]["Name"], this_subunit.mount_armour["Name"])
            subunit_weapon_list = [(self.weapon_data.weapon_list[this_subunit.primary_main_weapon[0]]["Name"],
                                    self.weapon_data.weapon_list[this_subunit.primary_sub_weapon[0]]["Name"])]

            weapon_common_action = [(self.generic_action_data[subunit_weapon_list[0][0]]["Common"],
                                     self.generic_action_data[subunit_weapon_list[0][1]]["Common"])]
            weapon_attack_action = [(self.generic_action_data[subunit_weapon_list[0][0]]["Attack"],
                                     self.generic_action_data[subunit_weapon_list[0][1]]["Attack"])]
            if (this_subunit.primary_main_weapon, this_subunit.primary_sub_weapon) != \
                    (this_subunit.secondary_main_weapon, this_subunit.secondary_sub_weapon):
                subunit_weapon_list = [subunit_weapon_list[0],
                                       (self.weapon_data.weapon_list[this_subunit.secondary_main_weapon[0]]["Name"],
                                        self.weapon_data.weapon_list[this_subunit.secondary_sub_weapon[0]]["Name"])]
                weapon_common_action = [weapon_common_action[0], (self.generic_action_data[subunit_weapon_list[1][0]]["Common"],
                                                                  self.generic_action_data[subunit_weapon_list[1][1]]["Common"])]
                weapon_attack_action = [(weapon_attack_action[0], (self.generic_action_data[subunit_weapon_list[1][0]]["Attack"],
                                                                   self.generic_action_data[subunit_weapon_list[1][1]]["Attack"]))]

            for animation in self.generic_animation_pool[0]:  # just use whatever side in the list for finding animation name for now
                if this_subunit.race_name in animation:  # grab race animation
                    animation_property = self.generic_animation_pool[0][animation][0]["animation_property"].copy()
                    for weapon_set_index, weapon_set in enumerate(subunit_weapon_list):  # create animation for each weapon set
                        for weapon_index, weapon in enumerate(weapon_set):
                            # first check if animation is common weapon type specific and match with weapon, then check if it is attack specific
                            if (any(ext in animation for ext in weapon_common_type_list) is False or weapon_common_action[weapon_set_index][weapon_index] in animation) and \
                                (any(ext in animation for ext in weapon_attack_type_list) is False or (weapon_attack_action[weapon_set_index][weapon_index] in animation and ("main", "sub")[weapon_index] in animation)):
                                if animation + "/" + str(weapon_set_index) not in animation_sprite_pool[this_subunit.troop_id]:
                                    animation_sprite_pool[this_subunit.troop_id][animation + "/" + str(weapon_set_index)] = {}
                                for index, direction in enumerate(direction_list):
                                    new_direction = direction
                                    opposite_direction = None  # no opposite direction for front and back
                                    if direction == "side":
                                        new_direction = "r_side"
                                        opposite_direction = "l_side"
                                    elif direction == "sideup":
                                        new_direction = "r_sideup"
                                        opposite_direction = "l_sideup"
                                    elif direction == "sidedown":
                                        new_direction = "r_sidedown"
                                        opposite_direction = "l_sidedown"
                                    animation_sprite_pool[this_subunit.troop_id][animation + "/" + str(weapon_set_index)][new_direction] = {}
                                    if opposite_direction is not None:
                                        animation_sprite_pool[this_subunit.troop_id][animation + "/" + str(weapon_set_index)][opposite_direction] = {}
                                    for frame_num, frame_data in enumerate(self.generic_animation_pool[index][animation]):
                                        sprite_dict = make_sprite(this_subunit.size, frame_data,
                                                                  self.troop_data.troop_sprite_list[str(this_subunit.troop_id)],
                                                                  self.gen_body_sprite_pool, self.gen_weapon_sprite_pool, self.gen_armour_sprite_pool,
                                                                  self.effect_sprite_pool, animation_property, self.weapon_joint_list,
                                                                  (weapon_set_index, weapon_set), armour,
                                                                  self.hair_colour_list, self.skin_colour_list, genre_sprite_size, screen_scale)

                                        animation_sprite_pool[this_subunit.troop_id][animation + "/" + str(weapon_set_index)][new_direction][
                                            frame_num] = \
                                            {"sprite": sprite_dict["sprite"], "animation_property": sprite_dict["animation_property"],
                                             "frame_property": sprite_dict["frame_property"]}
                                        if opposite_direction is not None:  # flip sprite for opposite direction
                                            animation_sprite_pool[this_subunit.troop_id][animation + "/" + str(weapon_set_index)][
                                                opposite_direction][
                                                frame_num] = {"sprite": pygame.transform.flip(sprite_dict["sprite"].copy(), True, False),
                                                              "animation_property": sprite_dict["animation_property"],
                                                              "frame_property": sprite_dict["frame_property"]}
    return animation_sprite_pool


def unit_setup(self, team_army):
    """read unit from unit_pos(source) file and create object with addunit function"""
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
        list_column = ["Row 1", "Row 2", "Row 3", "Row 4", "Row 5", "Row 6", "Row 7", "Row 8", "Row 9", "Row 10",
                       "POS", "Leader", "Leader Position"]  # value in list only
        float_column = ["Angle", "Start Health", "Start Stamina"]  # value in float
        int_column = [index for index, item in enumerate(header) if item in int_column]
        list_column = [index for index, item in enumerate(header) if item in list_column]
        float_column = [index for index, item in enumerate(header) if item in float_column]
        subunit_game_id = 1
        for this_unit in rd[1:]:  # skip header
            for n, i in enumerate(this_unit):
                this_unit = stat_convert(this_unit, n, i, list_column=list_column, int_column=int_column, float_column=float_column)
            this_unit = {header[index]: stuff for index, stuff in enumerate(this_unit)}
            control = False
            if self.team_selected == this_unit["Team"] or self.enactment:  # player can control only his team or both in enactment mode
                control = True

            colour = team_colour[this_unit["Team"]]
            if type(team_army) == list or type(team_army) == tuple:
                which_army = team_army[this_unit["Team"]]
            else:  # for character selection
                which_army = team_army

            command = False  # Not commander unit by default
            if len(which_army) == 0:  # First unit is commander
                command = True
            coa = pygame.transform.scale(self.coa_list[this_unit["Faction"]], (60, 60))  # get coa_list image and scale smaller to fit ui
            self.generate_unit(which_army, this_unit, control, command, colour, coa, subunit_game_id)
            # ^ End subunit setup

    unit_file.close()
