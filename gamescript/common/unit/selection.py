def selection(self):
    if self.just_selected:  # add highlight to subunit in selected unit
        for subunit in self.subunit_list:
            subunit.zoom_scale()
        self.just_selected = False

    elif self.selected and self.battle.current_selected != self:  # no longer selected
        self.selected = False
        for subunit in self.subunit_list:  # remove highlight
            subunit.image_inspect_original = subunit.inspect_base_image2.copy()
            subunit.rotate()
            subunit.selected = False
