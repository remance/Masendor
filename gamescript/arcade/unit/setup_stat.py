
def setup_stat(self, battle_start=False):
    """Grab stat from all subunit in the unit"""
    self.troop_number = 0
    self.stamina = 0
    self.morale = 0
    all_speed = []  # list of subunit speed, use to get the slowest one
    self.ammo = 0
    how_many = 0
    all_shoot_range = []  # list of shoot range, use to get the shortest and longest one

    # for checking row order and adjusting layer to show subunit closest to bottom of the screen first
    pos_dict = {sprite: sprite.base_pos for sprite in self.subunit_list}
    pos_dict = dict(sorted(pos_dict.items(), key=lambda x: x[1][1]))

    # Grab subunit stat
    for index, subunit in enumerate(pos_dict.keys()):
        if subunit.state != 100:  # only get stat from alive subunit
            if self.zoom == 1:
                if subunit.unit_leader is False:
                    self.battle_camera.change_layer(subunit, index + 4)
                else:
                    self.battle_camera.change_layer(subunit, 15)  # use higher layer for leader
            self.troop_number += subunit.troop_number
            self.stamina += subunit.stamina
            self.morale += subunit.morale
            all_speed.append(subunit.speed)
            for key in (0, 1):
                for magazine in subunit.magazine_count[key]:
                    self.ammo += magazine
                for shoot_range in subunit.shoot_range[key].values():
                    if shoot_range > 0:
                        all_shoot_range.append(shoot_range)
            subunit.skill_cond = self.skill_cond
            how_many += 1

    self.troop_number = int(self.troop_number)  # convert to int to prevent float decimal

    self.cal_unit_stat(how_many, all_speed, all_shoot_range, battle_start)  # calculate stat for unit related calculation
