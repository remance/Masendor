from gamescript.common import utility

rotation_xy = utility.rotation_xy


def make_front_pos(self):
    """create new pos for front side of sprite"""
    front_pos = (self.base_pos[0], (self.base_pos[1] - self.image_height))  # generate front side position
    front_pos = rotation_xy(self.base_pos, front_pos,
                            self.radians_angle)  # rotate the new front side according to sprite rotation

    return front_pos


def make_pos_range(self):
    """create range of sprite pos for pathfinding"""
    self.pos_range = (range(int(max(0, self.base_pos[0] - (self.image_height - 1))), int(min(1000, self.base_pos[0] + self.image_height))),
                      range(int(max(0, self.base_pos[1] - (self.image_height - 1))), int(min(1000, self.base_pos[1] + self.image_height))))


def threshold_count(self, elem, t1status, t2status):
    """apply elemental status effect when reach elemental threshold"""
    if elem > 50:
        self.status_effect[t1status] = self.status_list[t1status].copy()  # apply tier 1 status
        if elem > 100:
            self.status_effect[t2status] = self.status_list[t2status].copy()  # apply tier 2 status
            del self.status_effect[t1status]  # remove tier 1 status
            elem = 0  # reset elemental count
    return elem


def temperature_cal(self, temp_reach):
    """Temperature mod function from terrain and weather"""
    if temp_reach < 0:  # cold # temperature
        temp_reach = temp_reach * (100 - self.cold_res) / 100  # lowest temperature the subunit will change based on cold resist
    else:  # hot temperature
        temp_reach = temp_reach * (100 - self.heat_res) / 100  # highest temperature the subunit will change based on heat resist

    if self.temp_count != temp_reach:  # move temp_count toward temp_reach
        if temp_reach > 0:
            if self.temp_count < temp_reach:
                self.temp_count += (100 - self.heat_res) / 100 * self.timer  # increase temperature, rate depends on heat resistance (- is faster)
        elif temp_reach < 0:
            if self.temp_count > temp_reach:
                self.temp_count -= (100 - self.cold_res) / 100 * self.timer  # decrease temperature, rate depends on cold resistance
        else:  # temp_reach is 0, subunit temp revert to 0
            if self.temp_count > 0:
                self.temp_count -= (1 + self.heat_res) / 100 * self.timer  # revert faster with higher resist
            else:
                self.temp_count += (1 + self.cold_res) / 100 * self.timer

    # Temperature effect
    if self.temp_count > 50:  # Hot
        self.status_effect[96] = self.status_list[96].copy()
        if self.temp_count > 100:  # Extremely hot
            self.status_effect[97] = self.status_list[97].copy()
            del self.status_effect[96]
    if self.temp_count < -50:  # Cold
        self.status_effect[95] = self.status_list[95].copy()
        if self.temp_count < -100:  # Extremely cold
            self.status_effect[29] = self.status_list[29].copy()
            del self.status_effect[95]


def find_nearby_subunit(self):
    """Find nearby friendly squads in the same unit for applying buff"""
    self.nearby_subunit_list = []
    corner_subunit = []
    for row_index, row_list in enumerate(self.unit.subunit_list.tolist()):
        if self.game_id in row_list:
            if row_list.index(self.game_id) - 1 != -1:  # get subunit from left if not at first column
                self.nearby_subunit_list.append(self.unit.subunit_list[row_index][row_list.index(self.game_id) - 1])  # index 0
            else:  # not exist
                self.nearby_subunit_list.append(0)  # add number 0 instead

            if row_list.index(self.game_id) + 1 != len(row_list):  # get subunit from right if not at last column
                self.nearby_subunit_list.append(self.unit.subunit_list[row_index][row_list.index(self.game_id) + 1])  # index 1
            else:  # not exist
                self.nearby_subunit_list.append(0)  # add number 0 instead

            if row_index != 0:  # get top subunit
                self.nearby_subunit_list.append(self.unit.subunit_list[row_index - 1][row_list.index(self.game_id)])  # index 2
                if row_list.index(self.game_id) - 1 != -1:  # get top left subunit
                    corner_subunit.append(self.unit.subunit_list[row_index - 1][row_list.index(self.game_id) - 1])  # index 3
                else:  # not exist
                    corner_subunit.append(0)  # add number 0 instead
                if row_list.index(self.game_id) + 1 != len(row_list):  # get top right
                    corner_subunit.append(self.unit.subunit_list[row_index - 1][row_list.index(self.game_id) + 1])  # index 4
                else:  # not exist
                    corner_subunit.append(0)  # add number 0 instead
            else:  # not exist
                self.nearby_subunit_list.append(0)  # add number 0 instead

            if row_index != len(self.unit.subunit_list) - 1:  # get bottom subunit
                self.nearby_subunit_list.append(self.unit.subunit_list[row_index + 1][row_list.index(self.game_id)])  # index 5
                if row_list.index(self.game_id) - 1 != -1:  # get bottom left subunit
                    corner_subunit.append(self.unit.subunit_list[row_index + 1][row_list.index(self.game_id) - 1])  # index 6
                else:  # not exist
                    corner_subunit.append(0)  # add number 0 instead
                if row_list.index(self.game_id) + 1 != len(row_list):  # get bottom  right subunit
                    corner_subunit.append(self.unit.subunit_list[row_index + 1][row_list.index(self.game_id) + 1])  # index 7
                else:  # not exist
                    corner_subunit.append(0)  # add number 0 instead
            else:  # not exist
                self.nearby_subunit_list.append(0)  # add number 0 instead
    self.nearby_subunit_list = self.nearby_subunit_list + corner_subunit


def status_to_friend(self, aoe, status_id, status_list):
    """apply status effect to nearby subunit depending on aoe stat"""
    if aoe in (2, 3):
        if aoe > 1:  # only direct nearby friendly subunit
            for subunit in self.nearby_subunit_list[0:4]:
                if subunit != 0 and subunit.state != 100:  # only apply to exist and alive squads
                    subunit.status_effect[status_id] = status_list  # apply status effect
        if aoe > 2:  # all nearby including corner friendly subunit
            for subunit in self.nearby_subunit_list[4:]:
                if subunit != 0 and subunit.state != 100:  # only apply to exist and alive squads
                    subunit.status_effect[status_id] = status_list  # apply status effect
    elif aoe == 4:  # apply to whole unit
        for subunit in self.unit.subunit_list.flat:
            if subunit.state != 100:  # only apply to alive squads
                subunit.status_effect[status_id] = status_list  # apply status effect
