import math

rotation_list=(-90, -120, -45, 0, 90, 45, 120, 180)


def rotate_logic(self, dt):
    if self.angle != self.new_angle and self.charging is False and self.state != 10 and self.stamina > 0 and self.collide is False:
        self.new_angle = min(rotation_list,
                             key=lambda x: abs(x - self.new_angle))  # find closest in list of rotation

        self.angle = self.new_angle  # arcade mode doesn't have gradual rotate, subunit can rotate at once
        # ^^ End rotate tiny
        self.set_subunit_target()  # generate new pos related to side


def revert_move(self):
    """Only subunit will rotate to move, not the entire unit"""
    self.new_angle = self.angle
    self.move_rotate = False  # will not rotate to move
    self.revert = True
    new_angle = self.set_rotate()
    for subunit in self.subunit_sprite:
        subunit.new_angle = new_angle
