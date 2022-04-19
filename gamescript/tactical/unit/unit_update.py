def selection(self):
    if self.just_selected:  # add highlight to subunit in selected unit
        for subunit in self.subunits:
            subunit.zoom_scale()
        self.just_selected = False

    elif self.selected and self.battle.current_selected != self:  # no longer selected
        self.selected = False
        for subunit in self.subunits:  # remove highlight
            subunit.image_inspect_original = subunit.inspect_image_original2.copy()
            subunit.rotate()
            subunit.selected = False


def auth_recal(self):
    """recalculate authority from all alive leaders"""
    self.authority = (self.leader[0].authority / 2) + (self.leader[1].authority / 4) + \
                     (self.leader[2].authority / 4) + (self.leader[3].authority / 10)
    self.leader_social = self.leader[0].social
    if self.authority > 0:
        big_army_size = self.subunit_list > 0
        big_army_size = big_army_size.sum()
        if big_army_size > 20:  # army size larger than 20 will reduce start_set leader authority
            self.authority = (self.team_commander.authority / 2) + (self.leader[0].authority / 2 * (100 - big_army_size) / 100) + \
                             (self.leader[1].authority / 2) + (self.leader[2].authority / 2) + (self.leader[3].authority / 4)
        else:
            self.authority += (self.team_commander.authority / 2)


def morale_check_logic(self):
    if self.morale <= 10:  # Retreat state when morale lower than 10
        if self.state not in (98, 99):
            self.state = 98
        if self.retreat_start is False:
            self.retreat_start = True

    elif self.state == 98 and self.morale >= 50:  # quit retreat when morale reach increasing limit
        self.state = 0  # become idle, not resume previous command
        self.retreat_start = False
        self.retreat_way = None
        self.process_command(self.base_pos, False, False, other_command=1)

    if self.retreat_start and self.state != 96:
        self.retreat()


def setup_unit(self, battle_start=True):
    """Grab stat from all subunit in the unit"""
    self.troop_number = 0
    self.stamina = 0
    self.morale = 0
    all_speed = []  # list of subunit speed, use to get the slowest one
    self.ammo = 0
    how_many = 0
    all_shoot_range = []  # list of shoot range, use to get the shortest and longest one

    # v Grab subunit stat
    not_broken = False
    # if self.zoom == 1:  # closest zoom
    pos_dict = {sprite: sprite.base_pos for sprite in self.subunits}
    pos_dict = dict(sorted(pos_dict.items(), key=lambda x: x[1][1]))

    for index, subunit in enumerate(pos_dict.keys()):
        if subunit.state != 100:  # only get stat from alive subunit
            if self.zoom == 1:
                self.battle_camera.change_layer(subunit, index + 4)
            self.troop_number += subunit.troop_number
            self.stamina += subunit.stamina
            self.morale += subunit.morale
            all_speed.append(subunit.speed)
            self.ammo += subunit.magazine_left
            if subunit.shoot_range > 0:
                all_shoot_range.append(subunit.shoot_range)
            subunit.skill_cond = self.skill_cond
            how_many += 1
            if subunit.state != 99:  # check if unit completely broken
                not_broken = True
    self.troop_number = int(self.troop_number)  # convert to int to prevent float decimal

    if not_broken is False:
        self.state = 99  # completely broken
        self.can_split_row = False  # can not split unit
        self.can_split_col = False
    # ^ End grab subunit stat

    # v calculate stat for unit related calculation
    if self.troop_number > 0:
        self.stamina = self.stamina / how_many  # Average stamina of all subunit
        self.morale = self.morale / how_many  # Average morale of all subunit
        self.speed = min(all_speed)  # use the slowest subunit
        self.walk_speed, self.run_speed = self.speed / 20, self.speed / 15
        if self.state in (1, 3, 5):
            self.rotate_speed = self.walk_speed * 50 / (len(self.subunit_list[0]) * len(
                self.subunit_list))  # rotate speed is based on move speed and unit block size (not subunit total number)
        else:
            self.rotate_speed = self.run_speed * 50 / (len(self.subunit_list[0]) * len(self.subunit_list))

        if self.rotate_speed > 20:
            self.rotate_speed = 20  # state 10 melee combat rotate is auto placement
        if self.rotate_speed < 1:  # no less than speed 1, it will be too slow or can't rotate with speed 0
            self.rotate_speed = 1

        if len(all_shoot_range) > 0:
            self.max_range = max(all_shoot_range)  # Max shoot range of all subunit
            self.min_range = min(all_shoot_range)  # Min shoot range of all subunit
        if battle_start is False:  # Only do once when self start
            self.max_stamina = self.stamina
            self.max_morale = self.morale
            self.max_health = self.troop_number
        self.morale_state = 100
        self.stamina_state = 100
        if self.max_morale != float("inf"):
            self.morale_state = round((self.morale * 100) / self.max_morale)
        if self.max_stamina != float("inf"):
            self.stamina_state = round((self.stamina * 100) / self.max_stamina)
    # ^ End cal stat
