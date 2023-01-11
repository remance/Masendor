import numpy as np

import pygame

from gamescript.common import utility

rotation_xy = utility.rotation_xy


def enter_battle(self):
    """Setup various variables at the start of battle or when new unit spawn/split"""
    self.alive_subunit_list = [item for item in self.subunit_list]
    self.setup_stat(battle_start=True)
    self.setup_formation()
    self.old_troop_health, self.old_troop_stamina = self.troop_number, self.stamina
    self.leader_social = self.leader[0].social
    self.authority = self.leader[0].authority  # will be recalculated again later

    self.map_corner = self.battle.map_corner

    if self.commander:  # assign team leader commander to every unit in team if this is commander unit
        for this_unit in self.battle.all_team_unit[self.team]:
            this_unit.team_commander = self.leader[0]

    self.battle.all_team_unit["alive"].add(self)
    self.ally_pos_list = self.battle.team_pos_list[self.team]
    self.enemy_pos_list = {key: value for key, value in self.battle.team_pos_list.items() if
                           key != self.team and key != "alive"}

    self.authority_recalculation()
    self.command_buff = [(self.leader[0].melee_command - 5) * 0.1, (self.leader[0].range_command - 5) * 0.1,
                         (self.leader[0].cav_command - 5) * 0.1]  # unit leader command buff

    self.subunit_id_array = self.subunit_id_array.astype(int)

    unit_top_left = pygame.Vector2(self.base_pos[0] - self.base_width_box,
                                   self.base_pos[
                                       1] - self.base_height_box)  # get the top left corner of sprite to generate subunit position
    for subunit in self.subunit_list:  # generate start position of each subunit
        subunit.base_pos = unit_top_left + subunit.unit_position
        subunit.base_pos = pygame.Vector2(rotation_xy(self.base_pos, subunit.base_pos, self.radians_angle))
        subunit.zoom_scale()
        subunit.base_target = subunit.base_pos
        subunit.command_target = subunit.base_pos  # rotate according to sprite current rotation
        subunit.front_pos = subunit.make_front_pos()

    self.change_pos_scale()

    # create unit original formation positioning score
    new_formation = np.where(self.subunit_object_array == None, 99,  # Do not use is for where None, not work
                             self.subunit_object_array)  # change empty to the least important
    new_formation = np.where(self.subunit_object_array != None, 1,
                             new_formation)  # change all occupied to most important
    self.original_formation = {key: value * new_formation for key, value in
                               self.battle.troop_data.unit_formation_list["Original"].items()}

    self.original_subunit_id_array = self.subunit_id_array.copy()
