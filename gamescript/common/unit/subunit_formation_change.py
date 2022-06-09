def subunit_formation_change(self):
    self.base_width_box, self.base_height_box = len(self.subunit_id_array[0]) * (self.image_size[0] + 10) / 20, \
                                                len(self.subunit_id_array) * (self.image_size[1] + 2) / 20
    self.set_subunit_target()
    self.setup_frontline()
    if self.control:
        self.battle.change_inspect_subunit()
    self.input_delay = 0.5
