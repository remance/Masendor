import pygame

from engine.battleui import SpriteIndicator


def change_battle_state(self):
    self.previous_game_state = self.game_state
    if self.game_state == "battle":  # change to battle state
        self.camera_mode = self.start_camera_mode
        if not self.player_unit:
            self.camera_mode = "Free"
        self.mini_map.draw_image(self.battle_map_base, self.battle_map.mini_map_image, self.camera)

        # self.command_ui.rect = self.command_ui.image.get_rect(
        #     center=(self.command_ui.image.get_width() / 2, self.command_ui.image.get_height() / 2))  # change leader ui position back

        self.battle_ui_updater.add(self.event_log, self.event_log.scroll)

        self.game_speed = 1

        # Run enter_battle method
        for this_unit in self.unit_updater:
            this_unit.hitbox = SpriteIndicator(this_unit.hitbox_image, this_unit, self)
            this_unit.effectbox = SpriteIndicator(pygame.Surface((0, 0)), this_unit, self, layer=10000001)
            this_unit.enter_battle(self.unit_animation_pool, self.status_animation_pool)

        # Setup formation for leader
        for this_unit in self.unit_updater:
            this_unit.ai_unit()
            if this_unit.is_leader:
                if this_unit.alive_troop_follower:
                    this_unit.change_formation("troop")
                if this_unit.alive_leader_follower:
                    this_unit.change_formation("group")

            if self.player_unit:  # select player unit by default if control only one
                if this_unit.map_id == self.player_unit:  # get player unit
                    self.player_unit = this_unit
                    self.player_unit.player_control = True
                    self.battle_camera.change_layer(self.player_unit, 999999)
                    self.command_ui.add_leader_image(this_unit.portrait)
                    if self.camera_mode == "Follow":
                        self.true_camera_pos = self.player_unit.base_pos
                        self.camera_fix()
