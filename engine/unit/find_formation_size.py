from math import sqrt


def find_formation_size(self, troop=False, leader=False):
    if troop:
        self.troop_follower_size = sqrt(len(self.alive_troop_follower))
        if self.troop_follower_size > 0:
            if self.troop_follower_size.is_integer():
                self.troop_follower_size = int(self.troop_follower_size)
            else:
                self.troop_follower_size = int(self.troop_follower_size) + 1

            # if self.troop_follower_size % 2 == 0:
            self.troop_follower_size += 2
        unit_type_count = {"melee inf": 0, "range inf": 0, "melee cav": 0, "range cav": 0, "artillery": 0}
        type_key = tuple(unit_type_count.keys())
        for troop in self.alive_troop_follower:
            unit_type_count[type_key[troop.unit_type]] += 1
        self.group_type = sorted(unit_type_count.items(),
                                 key=lambda item: item[1])[-1][0]  # sort the highest troop type

    if leader:
        self.leader_follower_size = sqrt(len(self.alive_leader_follower))
        if self.leader_follower_size > 0:
            if self.leader_follower_size.is_integer():
                self.leader_follower_size = int(self.leader_follower_size)
            else:
                self.leader_follower_size = int(self.leader_follower_size) + 1
