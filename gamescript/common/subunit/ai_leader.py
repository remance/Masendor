def ai_leader(self):
    # if self.unit_follow_order != "Free":
    #
    #     self.tactic = "Wait"
    if self.tactic == "Attack" and self.nearest_enemy:
        self.follow_target = self.nearest_enemy[0].base_pos
        # if not self.move_path and self.nearest_enemy[1] > 20:
        #     self.battle.pathfinding_thread.input_list.append(self)
