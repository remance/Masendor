import math


def find_formation_size(self):
    self.troop_follower_size = math.sqrt(len(self.alive_troop_subordinate))
    if self.troop_follower_size.is_integer():
        self.troop_follower_size = int(self.troop_follower_size)
    else:
        self.troop_follower_size = int(self.troop_follower_size) + 1

    # if self.troop_follower_size % 2 == 0:
    self.troop_follower_size += 2
