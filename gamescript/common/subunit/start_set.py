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
    self.animation_pool = animation_pool[self.troop_id]

    self.pick_animation()
