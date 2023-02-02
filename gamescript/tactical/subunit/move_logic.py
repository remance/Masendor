import random

import pygame
from gamescript.common import utility

rotation_xy = utility.rotation_xy
infinity = float("inf")


def move_logic(self, dt, unit_state):
    self.base_target = self.command_target  # always attempt to catch up to command target
    revert_move = True  # revert move check for in case subunit still need to rotate before moving
    if unit_state == 0 or self.unit.revert or (self.angle != self.unit.angle and self.unit.move_rotate is False):
        revert_move = False
    if self.base_pos != self.base_target and \
            (revert_move or self.angle == self.new_angle):  # cannot move if unit still need to rotate
        no_collide = True  # can move if front of subunit not collided or with some exception

        if self.front_collide and self.momentum < 1:
            diff_list = []
            for subunit in self.front_collide:
                diff_list.append(abs(self.troop_mass - subunit.troop_mass))
            avg = (sum(diff_list) / len(diff_list)) + 1
            # Chance to move pass based on mass difference (smaller or bigger mean easier)
            # More collision make it more difficult to move pass too
            if random.randint(0, avg) < avg / len(diff_list):
                no_collide = False

        if no_collide:
            move = self.base_target - self.base_pos
            move_length = move.length()  # convert length

            if move_length > 0:  # movement length longer than 0.1, not reach base_target yet
                move.normalize_ip()
                if unit_state in (1, 3, 5, 7):  # walking
                    self.move_speed = self.unit.walk_speed  # use walk speed
                    self.walk = True
                elif unit_state in (10, 99):  # run with its own speed instead of uniformed run
                    self.move_speed = self.speed * self.momentum  # use its own speed when broken
                    self.run = True
                else:  # self.state in (2, 4, 6, 10, 96, 98, 99), running
                    self.move_speed = self.unit.run_speed * self.momentum  # use run speed
                    self.run = True
                if self.collide_penalty:  # reduce speed during moving through another unit
                    self.move_speed /= 2
                self.move = True
                self.move_speed /= 10
                move *= self.move_speed * dt
                new_move_length = move.length()
                new_pos = self.base_pos + move

                if self.move_speed > 0 and (self.state in (98, 99) or (0 < new_pos[0] < self.map_corner[0] and
                                                                       0 < new_pos[1] < self.map_corner[1])):
                    # cannot go pass map unless in retreat state
                    if new_move_length <= move_length:  # move normally according to move speed
                        self.base_pos += move
                        self.pos = self.base_pos * self.camera_zoom
                        self.rect.center = tuple(
                            int(v) for v in self.pos)  # list rect so the sprite gradually move to position on screen
                        self.hitbox_rect.center = self.base_pos
                        if self.stamina != infinity:
                            if self.walk:
                                self.stamina = self.stamina - (dt * 2)
                            elif self.run:
                                self.stamina = self.stamina - (dt * 5)

                    else:  # move length pass the base_target destination, set movement to stop exactly at base_target
                        move = self.base_target - self.base_pos  # simply change move to whatever remaining distance
                        self.base_pos += move  # adjust base position according to movement
                    if len(self.combat_move_queue) > 0 and self.base_pos.distance_to(
                            pygame.Vector2(
                                self.combat_move_queue[0])) < 0.1:  # reach the current queue point, remove from queue
                        self.combat_move_queue = self.combat_move_queue[1:]

                    self.change_pos_scale()
                    self.make_pos_range()

                    self.terrain, self.feature = self.get_feature(self.base_pos,
                                                                  self.base_map)  # get new terrain and feature at each subunit position
                    self.height = self.height_map.get_height(self.base_pos)  # get new height

                    self.make_front_pos()
                    self.last_pos = self.base_pos

                    if self.unit_leader and new_move_length > 0:
                        if self.unit.move_rotate is False:
                            self.unit.base_pos += move
                        front_pos = (self.unit.base_pos[0],
                                     (self.unit.base_pos[1] - self.unit.unit_box_height))  # find front position
                        self.unit.front_pos = rotation_xy(self.unit.base_pos, front_pos, self.unit.radians_angle)

                        number_pos = (self.unit.base_pos[0] - self.unit.unit_box_width,
                                      (self.unit.base_pos[1] + self.unit.unit_box_height))
                        self.unit.base_number_pos = self.unit.base_pos
                        self.unit.change_pos_scale()

                    if self.run:  # charge skill only when running to melee
                        if self.momentum < 1:
                            self.momentum += dt * self.acceleration / 100
                        elif self.momentum >= 1 and self.state == 4 and self.attacking and self.unit.move_rotate is False:
                            self.use_skill(self.charge_skill)  # Use charge skill
                            self.unit.charging = True
                            self.momentum = 1

                    elif self.momentum > 0.1:  # reset charge momentum if charge skill not active
                        self.momentum -= dt
                        if self.momentum <= 0.5:
                            self.unit.charging = False
                            if self.momentum <= 0.1:
                                self.momentum = 0.1
