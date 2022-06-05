def troop_card_button_click(self, who):
    for button in self.troop_card_button:  # Change subunit card option based on button clicking
        if button.rect.collidepoint(self.mouse_pos):
            self.click_any = True
            if self.troop_card_ui.option != button.event:
                self.troop_card_ui.option = button.event
                self.troop_card_ui.value_input(who=who, weapon_data=self.weapon_data,
                                               armour_data=self.armour_data,
                                               change_option=1, split=self.split_happen)

                if self.troop_card_ui.option == 2:
                    self.trait_skill_icon_blit()
                    self.effect_icon_blit()
                    self.countdown_skill_icon()
                else:
                    self.kill_effect_icon()
            break
