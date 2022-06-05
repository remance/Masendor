def find_nearby_subunit(self):
    """Find nearby friendly squads in the same unit for applying buff"""
    self.nearby_subunit_list = []
    corner_subunit = []
    for row_index, row_list in enumerate(self.unit.subunit_list.tolist()):
        if self.game_id in row_list:
            if row_list.index(self.game_id) - 1 != -1:  # get subunit from left if not at first column
                self.nearby_subunit_list.append(self.unit.subunit_list[row_index][row_list.index(self.game_id) - 1])  # index 0
            else:  # not exist
                self.nearby_subunit_list.append(0)  # add number 0 instead

            if row_list.index(self.game_id) + 1 != len(row_list):  # get subunit from right if not at last column
                self.nearby_subunit_list.append(self.unit.subunit_list[row_index][row_list.index(self.game_id) + 1])  # index 1
            else:  # not exist
                self.nearby_subunit_list.append(0)  # add number 0 instead

            if row_index != 0:  # get top subunit
                self.nearby_subunit_list.append(self.unit.subunit_list[row_index - 1][row_list.index(self.game_id)])  # index 2
                if row_list.index(self.game_id) - 1 != -1:  # get top left subunit
                    corner_subunit.append(self.unit.subunit_list[row_index - 1][row_list.index(self.game_id) - 1])  # index 3
                else:  # not exist
                    corner_subunit.append(0)  # add number 0 instead
                if row_list.index(self.game_id) + 1 != len(row_list):  # get top right
                    corner_subunit.append(self.unit.subunit_list[row_index - 1][row_list.index(self.game_id) + 1])  # index 4
                else:  # not exist
                    corner_subunit.append(0)  # add number 0 instead
            else:  # not exist
                self.nearby_subunit_list.append(0)  # add number 0 instead

            if row_index != len(self.unit.subunit_list) - 1:  # get bottom subunit
                self.nearby_subunit_list.append(self.unit.subunit_list[row_index + 1][row_list.index(self.game_id)])  # index 5
                if row_list.index(self.game_id) - 1 != -1:  # get bottom left subunit
                    corner_subunit.append(self.unit.subunit_list[row_index + 1][row_list.index(self.game_id) - 1])  # index 6
                else:  # not exist
                    corner_subunit.append(0)  # add number 0 instead
                if row_list.index(self.game_id) + 1 != len(row_list):  # get bottom  right subunit
                    corner_subunit.append(self.unit.subunit_list[row_index + 1][row_list.index(self.game_id) + 1])  # index 7
                else:  # not exist
                    corner_subunit.append(0)  # add number 0 instead
            else:  # not exist
                self.nearby_subunit_list.append(0)  # add number 0 instead
    self.nearby_subunit_list = self.nearby_subunit_list + corner_subunit