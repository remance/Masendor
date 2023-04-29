import pygame

from gamescript.battleui import SpriteIndicator


def change_battle_state(self):
    self.previous_game_state = self.game_state
    if self.game_state == "battle":  # change to battle state
        self.camera_mode = self.start_camera_mode
        if not self.unit_selected:
            self.camera_mode = "Free"
        self.mini_map.draw_image(self.battle_map_base, self.battle_map.mini_map_image, self.camera)

        # self.command_ui.rect = self.command_ui.image.get_rect(
        #     center=(self.command_ui.image.get_width() / 2, self.command_ui.image.get_height() / 2))  # change leader ui position back

        self.battle_ui_updater.add(self.event_log, self.event_log.scroll)

        self.game_speed = 1

        # Run enter_battle method
        for this_subunit in self.unit_updater:
            this_subunit.hitbox = SpriteIndicator(this_subunit.hitbox_image, this_subunit, self)
            this_subunit.effectbox = SpriteIndicator(pygame.Surface((0, 0)), this_subunit, self, layer=10000001)
            this_subunit.enter_battle(self.unit_animation_pool, self.status_animation_pool)

        # Setup formation for leader
        for this_subunit in self.unit_updater:
            this_subunit.ai_unit()
            if this_subunit.is_leader:
                if this_subunit.alive_troop_follower:
                    this_subunit.change_formation("troop")
                if this_subunit.alive_leader_follower:
                    this_subunit.change_formation("group")

            if self.unit_selected:  # select player unit by default if control only one
                if this_subunit.map_id == self.unit_selected:  # get player unit
                    self.player_unit = this_subunit
                    self.player_unit.player_control = True
                    self.battle_camera.change_layer(self.player_unit, 999999)
                    self.command_ui.add_leader_image(this_subunit.portrait)
                    if self.camera_mode == "Follow":
                        self.true_camera_pos = self.player_unit.base_pos
                        self.camera_fix()
