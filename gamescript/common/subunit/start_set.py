def start_set(self, zoom, animation_pool):
    """run once when battle start or subunit just get created"""
    self.zoom = zoom
    self.front_pos = self.make_front_pos()
    self.make_pos_range()
    self.zoom_scale()
    self.find_nearby_subunit()

    try:
        self.terrain, self.feature = self.get_feature(self.base_pos,
                                                      self.base_map)  # Get new terrain and feature at each subunit position
        self.height = self.height_map.get_height(self.base_pos)  # Current terrain height
        self.front_height = self.height_map.get_height(self.front_pos)  # Terrain height at front position
    except AttributeError:
        pass

    self.command_buff = self.unit.command_buff[
                            self.subunit_type] * 100  # Command buff from main leader according to this subunit type
    self.grade_social_effect = self.unit.leader_social[self.grade_name]
    self.status_update()

    self.battle.alive_subunit_list.append(self)

    # Add troop number to counter how many troop join battle
    self.battle.team_troop_number[self.team] += self.troop_number
    self.battle.start_troop_number[self.team] += self.troop_number

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
    #         if self.troop_data.skill_list[skill]["Action"][0] in animation:
    #             make_animation = True
    #             break

    self.pick_animation()
