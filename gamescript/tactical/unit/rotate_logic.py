import math


def rotate_logic(self, dt):
    if self.angle != self.new_angle and self.state != 10 and self.stamina > 0 and self.collide is False:
        self.rotate_cal = abs(self.new_angle - self.angle)  # amount of angle left to rotate
        self.rotate_check = 360 - self.rotate_cal  # rotate distance used for preventing angle calculation bug (pygame rotate related)
        self.move_rotate = True
        self.radians_angle = math.radians(360 - self.angle)  # for subunit rotate
        if self.angle < 0:  # negative angle (rotate to left side)
            self.radians_angle = math.radians(-self.angle)

        # Rotate logic to continuously rotate based on angle and shortest length
        rotate_tiny = self.rotate_speed * dt  # rotate little by little according to time
        if self.new_angle > self.angle:  # rotate to angle more than the current one
            if self.rotate_cal > 180:  # rotate with the smallest angle direction
                self.angle -= rotate_tiny
                self.rotate_check -= rotate_tiny
                if self.rotate_check <= 0:
                    self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
            else:
                self.angle += rotate_tiny
                if self.angle > self.new_angle:
                    self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
        elif self.new_angle < self.angle:  # rotate to angle less than the current one
            if self.rotate_cal > 180:  # rotate with the smallest angle direction
                self.angle += rotate_tiny
                self.rotate_check -= rotate_tiny
                if self.rotate_check <= 0:
                    self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
            else:
                self.angle -= rotate_tiny
                if self.angle < self.new_angle:
                    self.angle = self.new_angle  # if rotate pass base_target angle, rotate to base_target angle
        # ^^ End rotate tiny
        self.set_subunit_target()  # generate new pos related to side

    elif self.move_rotate and abs(self.angle - self.new_angle) < 1:  # Finish
        self.move_rotate = False
        if self.rotate_only is False:  # continue moving to base_target after finish rotate
            self.set_subunit_target(target=self.base_target)
        else:
            self.state = 0  # idle state
            self.issue_order(self.base_target, other_command="Stop")
            self.rotate_only = False  # reset rotate only condition
