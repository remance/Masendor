def setup_stat(self, battle_start=False):
    """Grab stat from all subunit in the unit"""
    self.troop_number = 0
    self.stamina = 0
    self.morale = 0
    all_speed = []  # list of subunit speed, use to get the slowest one
    self.ammo = 0
    how_many = 0
    all_shoot_range = []  # list of shoot range, use to get the shortest and longest one

    # Grab subunit stat
    not_broken = False

    for subunit in self.alive_subunit_list:
        if self.camera_zoom == self.max_camera_zoom and subunit in self.battle.battle_camera:
            # Adjust layer to show subunit closest to bottom and furthest to the right of the screen first
            layer = round(subunit.base_pos[0] + (subunit.base_pos[1] * 10), 0)
            if layer < 0:
                layer = 1
            self.battle.battle_camera.change_layer(subunit, layer)
        self.troop_number += subunit.troop_number
        self.stamina += subunit.stamina
        self.morale += subunit.morale
        all_speed.append(subunit.speed)
        for magazine in subunit.magazine_count.values():
            for magazine_count in magazine.values():
                self.ammo += magazine_count
        for shoot_range in subunit.shoot_range.values():
            if shoot_range > 0:
                all_shoot_range.append(shoot_range)
        subunit.skill_cond = self.skill_cond
        how_many += 1
        if subunit.state != 99:  # check if unit completely broken
            not_broken = True
    self.troop_number = int(self.troop_number)  # convert to int to prevent float decimal

    if not_broken is False:
        self.state = 99  # completely broken
        self.can_split_row = False  # can not split unit
        self.can_split_col = False

    if how_many > 0:
        self.cal_unit_stat(how_many, all_speed, all_shoot_range,
                           battle_start)  # calculate stat for unit related calculation
