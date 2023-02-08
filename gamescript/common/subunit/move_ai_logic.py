import random

follow_distance = 10
stay_formation_distance = 5


def move_ai_logic(self):
    if self.leader is not None:
        if not self.command_action:
            if self.is_leader is False:
                if self.leader.follow_order != "Free":  # move to assigned location
                    if self.leader.follow_order == "Stay Formation":
                        follow = stay_formation_distance
                    else:
                        follow = follow_distance
                    if self.leader.follow_order != "Stay Here":  # find new pos from formation
                        self.follow_target = self.leader.formation_pos_list[self]

                    distance_to_move = self.follow_target.distance_to(self.base_pos)
                    if distance_to_move > follow:  # too far from follow target pos, start moving toward it
                        self.command_target = self.follow_target
                        if distance_to_move > 0:  # only walk if not too far
                            self.command_action = self.walk_command_action.copy()
                            self.command_action["move speed"] = self.walk_speed
                            if distance_to_move > 20:  # run if too far
                                self.command_action = self.run_command_action.copy()
                                self.command_action["move speed"] = self.run_speed
                else:  # run to nearby enemy in free order
                    self.follow_target = self.nearest_enemy[0].base_pos
                    self.command_target = self.follow_target
                    self.command_action = self.run_command_action.copy()
                    self.command_action["move speed"] = self.run_speed
            # else:
            #     pass
        # impetus
