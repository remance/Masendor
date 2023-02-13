import pygame


def enter_battle(self, animation_pool):
    """run once when battle start or subunit just get created"""

    self.terrain, self.feature = self.get_feature(self.base_pos,
                                                  self.base_map)  # Get new terrain and feature at each subunit position
    self.height = self.get_height(self.base_pos)  # Current terrain height

    layer = round(self.base_pos[0] + (self.base_pos[1] * 10), 0)  # change layer
    if layer < 0:
        layer = 1
    if self._layer != layer:
        self.battle.battle_camera.change_layer(self, layer)

    self.swap_weapon(self.equipped_weapon)
    self.make_front_pos()

    self.map_corner = self.battle.map_corner

    if self.leader is not None:
        self.add_leader_buff()

    if self.is_leader:
        self.find_formation_size()

    self.status_update()

    # Add troop number to counter how many troop join battle
    self.battle.active_subunit_list.append(self)
    self.battle.all_team_subunit[self.team].add(self)
    self.battle.team_troop_number[self.team] += 1
    self.battle.start_troop_number[self.team] += 1

    # Grab only animation sprite that the subunit can use
    self.animation_pool = animation_pool[self.sprite_id][self.race_name][self.mount_race_name][self.armour_gear[0]][
        self.mount_gear[2]]
    self.animation_pool = self.animation_pool[
                              str(self.primary_main_weapon[0]) + "," + str(self.primary_sub_weapon[0])] | \
                          self.animation_pool[
                              str(self.secondary_main_weapon[0]) + "," + str(self.secondary_sub_weapon[0])]
    # skill_list = this_subunit["Skill"] + self.troop_data.weapon_list[primary_main_weapon]["Skill"] + \
    #              self.troop_data.weapon_list[primary_sub_weapon]["Skill"] + \
    #              self.troop_data.weapon_list[secondary_main_weapon]["Skill"] + \
    #              self.troop_data.weapon_list[secondary_sub_weapon]["Skill"]
    # if "_Skill_" in animation:  # skill animation
    #     make_animation = False  # not make animation for troop with no related skill animation
    #     for skill in skill_list:
    #         if self.troop_data.skill_list[skill]["Action"][0] in animation:  # TODO recheck if this is necessary
    #             make_animation = True
    #             break

    self.default_sprite_size = (self.animation_pool[self.animation_race_name + "_Default"]["r_side"][0]["sprite"].get_width() / 5,
                                self.animation_pool[self.animation_race_name + "_Default"]["r_side"][0]["sprite"].get_height() / 5)

    self.pick_animation()
