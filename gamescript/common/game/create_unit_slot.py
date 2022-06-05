def create_unit_slot(self, game_id, troop_id, range_to_run, start_pos):
    from gamescript import subunit
    width, height = 0, 0
    slot_number = 0  # Number of subunit based on the position in row and column
    for _ in range_to_run:  # generate player unit slot for filling troop into preview unit
        width += self.icon_sprite_width
        dummy_subunit = subunit.EditorSubunit(troop_id, game_id, self.unit_build_slot,
                                              (start_pos[0] + width, start_pos[1] + height), 100, 100, [1, 1])
        dummy_subunit.kill()  # not part of subunit in battle, remove from all groups
        self.subunit_build.add(dummy_subunit)
        slot_number += 1
        if slot_number % 8 == 0:  # Pass the last subunit in the row, go to the next one
            width = 0
            height += self.icon_sprite_height

        game_id += 1
    return game_id
