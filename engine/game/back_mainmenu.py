def back_mainmenu(self):
    self.menu_state = "main_menu"
    self.add_ui_updater(*self.start_menu_ui_only)
    self.remove_ui_updater(self.hide_background)
