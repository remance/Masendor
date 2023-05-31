from pygame import Vector2

from engine.utility import rotation_xy

infinity = float("inf")


def move_logic(self, dt):
    if "forced move" not in self.current_action:
        self.base_target = self.command_target  # always attempt to catch up to command target
    else:
        self.base_target = self.forced_target

    if self.move_speed:
        if "movable" in self.current_action:  # animation allow movement
            if self.base_pos != self.base_target:
                move = self.base_target - self.base_pos
                require_move_length = move.length()  # convert length
                move.normalize_ip()
                height_diff = (
                                      self.height / self.front_height) ** 2  # walk down hill increase speed, walk up hill reduce speed
                move *= self.move_speed * height_diff * dt
                new_pos = self.base_pos + move

                if (self.retreat_start or (0 < new_pos[0] < self.map_corner[0] and
                                           0 < new_pos[1] < self.map_corner[1])):
                    # cannot go pass map unless in retreat state
                    if move.length() <= require_move_length:  # move normally according to move speed
                        self.base_pos += move
                        if "forced move" not in self.current_action:  # damaged or knockdown does not change direction
                            self.new_angle = self.set_rotate(self.base_target)
                    else:  # move length pass the base_target destination, set movement to stop exactly at base_target
                        move = self.base_target - self.base_pos  # simply change move to whatever remaining distance
                        self.base_pos += move  # adjust base position according to movement
                        if "forced move" not in self.current_action:  # damaged or knockdown does not change direction
                            self.new_angle = self.set_rotate(new_pos)

                    self.pos = Vector2((self.base_pos[0] * self.screen_scale[0],
                                        self.base_pos[1] * self.screen_scale[1])) * 5
                    self.offset_pos = self.pos - self.current_animation[self.sprite_direction][self.show_frame][
                        "center_offset"]
                    self.rect.center = self.offset_pos
                    self.hitbox.rect.center = self.pos
                    self.effectbox.rect.center = self.offset_pos

                    self.move = True

                    self.height = self.get_height(self.base_pos)  # Current terrain height
                    self.terrain, self.feature = self.get_feature(self.base_pos,
                                                                  self.base_map)  # get new terrain and feature

                    self.make_front_pos()
                    self.front_height = self.get_height(self.front_pos)

                    # momentum calculation
                    if "use momentum" in self.current_action:
                        if abs(self.run_direction - self.new_angle) > 90:
                            # reset momentum if going opposite direction midrun
                            self.run_direction = self.new_angle
                            self.momentum = 0

                        self.stamina -= 0.1  # use stamina when run or charge
                        if self.stamina < 0:
                            self.stamina = 0
                        if self.momentum < 1:
                            self.momentum += dt * self.acceleration / 100
                            if self.momentum > 1:
                                self.momentum = 1

                    elif self.momentum:  # reset charge momentum when not running
                        self.momentum = 0

                if self.move_path and self.base_pos.distance_to(self.move_path[0]) < 0.1:
                    # reach the current queue point, remove from queue
                    self.move_path = self.move_path[1:]

            else:  # reach target, interrupt moving animation
                self.interrupt_animation = True  # in moving animation, interrupt it
                self.move_speed = 0

        elif "movable" not in self.command_action:  # has move speed but not movable animation, reset speed
            self.move_speed = 0

    else:
        if "movable" in self.current_action:  # in moving animation, interrupt it
            self.interrupt_animation = True
        if self.momentum:  # reduce charge momentum when not moving
            self.momentum = 0
