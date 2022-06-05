def preview_authority(self, leader_list):
    """Calculate authority of editing unit"""
    authority = int(
        leader_list[0].authority + (leader_list[0].authority / 2) +
        (leader_list[1].authority / 4) + (leader_list[2].authority / 4) +
        (leader_list[3].authority / 10))
    big_unit_size = len([slot for slot in self.subunit_build if slot.name != "None"])
    if big_unit_size > 20:  # army size larger than 20 will reduce start_set leader authority
        authority = int(leader_list[0].authority +
                        (leader_list[0].authority / 2 * (100 - big_unit_size) / 100) +
                        leader_list[1].authority / 2 + leader_list[2].authority / 2 +
                        leader_list[3].authority / 4)

    for slot in self.subunit_build:
        slot.authority = authority

    if self.subunit_in_card is not None:
        self.command_ui.value_input(who=self.unit_build_slot)

