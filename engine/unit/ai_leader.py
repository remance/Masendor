from math import sin, cos, radians

from pygame import Vector2


def ai_leader(self):
    """AI for army (top) leader"""
    # if self.unit_follow_order != "Free":
    #     self.tactic = "Wait"
    if self.tactic == "Attack" and self.nearest_enemy:
        if "range" in self.group_type or "artillery" in self.group_type:
            # group make up ranged troop, go to position that all troop followers can shoot
            if self.group_formation_position != "Behind":  # change formation so troop is behind leader for ranged group
                self.setup_formation("group", position="Behind")
            distance = 0
            for troop in self.alive_troop_follower:
                if troop.max_shoot_range > distance:
                    distance = troop.max_shoot_range
            distance *= 0.8
            enemy = self.nearest_enemy[0]
            angle = self.set_rotate(enemy.base_pos)
            enemy_distance = enemy.base_pos.distance_to(self.base_pos)
            if enemy_distance > distance:
                if self.group_formation_phase != "Skirmish Phase":  # start skirmish phase to maximise shooting
                    self.setup_formation("group", phase="Skirmish Phase")
                if self.army_formation_phase != "Skirmish Phase":
                    self.setup_formation("army", phase="Skirmish Phase")
                self.follow_target = Vector2(enemy.base_pos[0] + (distance * sin(radians(angle))),
                                             enemy.base_pos[1] + (distance * cos(radians(angle))))
            else:
                self.follow_target = Vector2(self.base_pos)
                if enemy_distance / 2 > distance:  # enemy half-way near, move melee troop up front if have any
                    if self.group_formation_phase != "Melee Phase":  # melee phase to counter nearby enemy
                        self.setup_formation("group", phase="Melee Phase")
                    if self.army_formation_phase != "Melee Phase":  # melee phase to counter nearby enemy
                        self.setup_formation("army", phase="Melee Phase")
        else:  # melee group rush to the nearest enemy
            self.follow_target = self.nearest_enemy[0].base_pos
        # if not self.move_path and self.nearest_enemy[1] > 20:
        #     self.battle.pathfinding_thread.input_list.append(self)
