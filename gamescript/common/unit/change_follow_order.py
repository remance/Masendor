from pygame import Vector2


def change_follow_order(self, new_order, which):
    if which == "troop":
        self.troop_follow_order = new_order
        follower_list = self.alive_troop_follower
        follower_pos_list = self.troop_pos_list
    elif which == "unit":
        self.group_follow_order = new_order
        follower_list = self.alive_leader_follower
        follower_pos_list = self.group_pos_list

    if new_order == "Stay Here":  # assign current pos to current spot
        for who in follower_list:
            who.follow_target = Vector2(who.base_pos)
        if which == "troop":  # leader follower also change troop formation order
            for who in self.alive_leader_follower:
                who.change_follow_order(new_order, "troop")

    else:  # find new pos from formation
        for who in follower_list:
            who.follow_target = follower_pos_list[who]
        if which == "troop":
            for who in self.alive_leader_follower:
                who.change_follow_order(new_order, "troop")
