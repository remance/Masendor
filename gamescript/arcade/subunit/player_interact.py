def player_interact(self, mouse_pos, mouse_left_up):
    """Mouse collision detection"""
    if self.rect.collidepoint(mouse_pos):
        self.battle.last_mouseover = self.unit  # last mouse over on this unit
        if self.battle.game_state == "editor" and self.battle.unit_build_slot not in self.battle.battle_ui_updater:
            if self.battle.game_state == "editor" and mouse_left_up and self.battle.click_any is False:
                self.battle.current_selected = self.unit  # become last selected unit
                if self.unit.selected is False:
                    self.unit.just_selected = True
                    self.unit.selected = True
                self.battle.click_any = True
