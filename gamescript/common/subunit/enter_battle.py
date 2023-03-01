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

    if self.leader:
        self.add_leader_buff()
        self.unit_leader = self.leader
        while self.unit_leader.leader:  # get the highest leader of the unit
            self.unit_leader = self.unit_leader.leader
    elif self.is_leader:  # is top unit leader
        self.unit_leader = None
        self.is_unit_leader = True

    if self.is_leader:
        self.find_formation_size(troop=True, leader=True)

    # Add troop number to counter how many troop join battle
    self.battle.active_subunit_list.append(self)
    self.battle.all_team_subunit[self.team].add(self)
    self.battle.team_troop_number[self.team] += 1
    self.battle.start_troop_number[self.team] += 1

    self.status_update()

    # Grab only animation sprite that the subunit can use
    self.animation_pool = animation_pool[self.sprite_id][self.race_name][self.mount_race_name][self.armour_id][
        self.mount_armour_id]
    self.animation_pool = self.animation_pool[
                              str(self.primary_main_weapon[0]) + "," + str(self.primary_sub_weapon[0])] | \
                          self.animation_pool[
                              str(self.secondary_main_weapon[0]) + "," + str(self.secondary_sub_weapon[0])]

    self.default_sprite_size = (self.animation_pool[self.animation_race_name + "_Default"]["r_side"][0]["sprite"].get_width() / 5,
                                self.animation_pool[self.animation_race_name + "_Default"]["r_side"][0]["sprite"].get_height() / 5)
    self.attack_effect_spawn_distance = self.default_sprite_size[0] * 1.5

    self.pick_animation()
