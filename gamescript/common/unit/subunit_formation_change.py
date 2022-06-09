def subunit_formation_change(self):
    found_count = 0
    position_count = 0
    for row in range(0, len(self.subunit_id_array)):
        for column in range(0, len(self.subunit_id_array[0])):
            self.subunit_object_array[row][column] = None
            if found_count < len(self.subunit_list):
                if self.subunit_id_array[row][column] != 0:
                    for subunit in self.subunit_list:
                        if self.subunit_id_array[row][column] == subunit.game_id:
                            self.subunit_object_array[row][column] = subunit
                            subunit.unit_position = (self.subunit_position_list[position_count][0] / 10,
                                                     self.subunit_position_list[position_count][1] / 10)  # position in unit sprite
                            break
                    found_count += 1
            position_count += 1

    self.base_width_box, self.base_height_box = len(self.subunit_id_array[0]) * (self.image_size[0] + 10) / 20, \
                                                len(self.subunit_id_array) * (self.image_size[1] + 2) / 20
    self.set_subunit_target()
    self.setup_frontline()
    if self.control:
        self.battle.change_inspect_subunit()
    self.input_delay = 0.5
