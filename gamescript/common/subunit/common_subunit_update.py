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