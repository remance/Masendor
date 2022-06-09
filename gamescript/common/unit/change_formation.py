def change_formation(self, name):
    if name == "original":
        self.subunit_id_array = self.original_subunit_id_array.copy()
    self.subunit_formation_change()
