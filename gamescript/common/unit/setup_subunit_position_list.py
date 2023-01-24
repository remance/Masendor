def setup_subunit_position_list(self):
    default_size = self.battle.subunit_hitbox_size
    self.subunit_position_list = []
    for row_index, row in enumerate(self.subunit_hitbox_size_array):
        self.subunit_position_list.append([])
        previous_large_x = 0
        for col_index, col in enumerate(row):
            x = 0
            y = 0
            if col_index != 0:  # get size from prior column in same row
                x = self.subunit_position_list[row_index][col_index - 1][0]
            if row_index != 0:  # get size from above row at same column index
                y = self.subunit_position_list[row_index - 1][col_index][1]
            x += col
            y += col
            if col > default_size:
                previous_large_x = col
            elif previous_large_x > default_size and previous_large_x % default_size == 0:  # previous larger subunit overtake the next row so use previous height
                x = previous_large_x
                y = previous_large_x
                previous_large_x -= default_size

            self.subunit_position_list[row_index].append((x, y))

            if self.subunit_object_array[row_index][col_index] is not None:
                self.subunit_object_array[row_index][col_index].pos_in_unit = (x, y)
