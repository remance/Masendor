def wheel_ui_process(self, choice):
    if choice in self.unit_behaviour_wheel:  # click choice that has children choice
        renew_wheel(self, choice)
    elif choice is not None:  # click choice with game effect
        if choice in self.unit_behaviour_wheel["Setting"]:
            if choice == "Height Map":
                self.battle_map.mode += 1  # change height map mode
                if self.battle_map.mode > 2:
                    self.battle_map.mode = 0
                self.battle_map.change_mode()

        elif choice in self.unit_behaviour_wheel["Formation"]:
            if choice == "Formation List":  # get formation from leader
                self.unit_behaviour_wheel[choice] = {value: value for value in
                                                     self.player_char.formation_list}  # TODO change when has icon
                renew_wheel(self, choice)
        elif choice in self.unit_behaviour_wheel["Unit"]:
            if choice == "Unit Formation List":  # get formation from leader
                self.unit_behaviour_wheel[choice] = {value: value for value in
                                                     self.player_char.formation_list}
                renew_wheel(self, choice)

        elif choice in self.unit_behaviour_wheel["Formation Style"]:
            self.player_char.setup_formation("troop", style=choice)
        elif choice in self.unit_behaviour_wheel["Formation Phase"]:
            self.player_char.setup_formation("troop", phase=choice)
        elif choice in self.unit_behaviour_wheel["Formation Density"]:
            self.player_char.setup_formation("troop", density=choice)
        elif choice in self.unit_behaviour_wheel["Formation Position"]:
            self.player_char.setup_formation("troop", position=choice)
        elif choice in self.unit_behaviour_wheel["Formation Order"]:
            self.player_char.change_follow_order(choice, "troop")
        elif "Formation List" in self.unit_behaviour_wheel and choice in self.unit_behaviour_wheel["Formation List"]:
            self.player_char.change_formation("troop", formation=choice)

        elif choice in self.unit_behaviour_wheel["Unit Style"]:
            self.player_char.setup_formation("unit", style=choice)
        elif choice in self.unit_behaviour_wheel["Unit Phase"]:
            self.player_char.setup_formation("unit", phase=choice)
        elif choice in self.unit_behaviour_wheel["Unit Density"]:
            self.player_char.setup_formation("unit", density=choice)
        elif choice in self.unit_behaviour_wheel["Unit Position"]:
            self.player_char.setup_formation("unit", position=choice)
        elif choice in self.unit_behaviour_wheel["Unit Order"]:
            self.player_char.change_follow_order(choice, "unit")
        elif "Unit Formation List" in self.unit_behaviour_wheel and choice in self.unit_behaviour_wheel["Unit Formation List"]:
            self.player_char.change_formation("unit", formation=choice)


def renew_wheel(self, choice):
    self.wheel_ui.generate(self.unit_behaviour_wheel[choice])
