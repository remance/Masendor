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