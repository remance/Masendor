equip_header = ("Primary", "Secondary")


def swap_weapon_command(self, choice):
    if "Troop" in choice:
        for this_subunit in self.player_char.unit.subunit_list:
            if this_subunit.leader is None and this_subunit.state < 90:  # skip leader
                for index, value in equip_header:
                    if value in choice:
                        self.player_char.unit.equipped_weapon = index
                        break
    else:  # change only leader equipment
        for index, value in equip_header:
            if value in choice:
                self.player_char.unit.equipped_weapon = index
                break
