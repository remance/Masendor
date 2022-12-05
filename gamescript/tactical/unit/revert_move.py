def revert_move(self):
    """Only subunit will rotate to move, not the entire unit"""
    self.new_angle = self.angle
    self.move_rotate = False  # will not rotate to move
    self.revert = True
    new_angle = self.set_rotate(self.base_target)
    for subunit in self.subunit_list:
        subunit.new_angle = new_angle
