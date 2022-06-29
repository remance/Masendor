def setup_subunit_position_list(self):
    width, height = 0, 0
    subunit_number = 0  # Number of subunit based on the position in row and column
    for row_index, row in enumerate(self.subunit_object_array):
        self.subunit_position_list.append([])
        for _ in row:
            width += self.image_size[0]
            self.subunit_position_list[row_index].append((width, height))
            subunit_number += 1
        width = 0
        height += self.image_size[1]
        subunit_number = 0
