def swap_weapon(self):
    self.process_trait_skill()
    self.action_list = {key: value for key, value in self.generic_action_data.items() if
                        key in self.weapon_name[0] or key in self.weapon_name[1]}
