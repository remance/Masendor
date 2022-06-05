def back_mainmenu(self):
    self.menu_state = "main_menu"

    self.main_ui_updater.remove(*self.menu_button)

    self.menu_button.remove(*self.menu_button)
    self.menu_button.add(*self.mainmenu_button)

    self.main_ui_updater.add(*self.start_menu_ui_only)
