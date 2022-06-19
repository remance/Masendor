def change_inspect_subunit(self):
    self.battle_ui_updater.remove(*self.inspect_subunit)
    for index, this_subunit in enumerate(self.current_selected.subunit_object_array.flat):
        if this_subunit is not None:
            self.inspect_subunit[index].add_subunit(this_subunit)
            self.battle_ui_updater.add(self.inspect_subunit[index])
            if self.subunit_selected is None:
                self.subunit_selected = self.inspect_subunit[index]
        else:
            self.inspect_subunit[index].add_subunit(None)
