from pygame import Surface, transform

from engine.effect.effect import ChargeDamageEffect
from engine.uibattle.uibattle import SpriteIndicator


def change_battle_state(self):
    self.camera_mode = self.start_camera_mode
    if not self.player_unit:
        self.camera_mode = "Free"
    self.player1_mini_map.draw_image(self.battle_base_map, self.battle_map.mini_map_image, self.camera)

    # self.command_ui.rect = self.command_ui.image.get_rect(
    #     center=(self.command_ui.image.get_width() / 2, self.command_ui.image.get_height() / 2))  # change leader ui position back

    self.add_ui_updater(self.event_log, self.event_log.scroll)

    self.game_speed = 1

    # Run enter_battle method
    for this_unit in self.unit_updater:
        this_unit.hitbox = ChargeDamageEffect(this_unit)
        this_unit.effectbox = SpriteIndicator(Surface((0, 0)), this_unit, layer=10000001)
        this_unit.enter_battle(self.unit_animation_pool, self.status_animation_pool)

    # Setup formation for leader
    for this_unit in self.unit_updater:
        if this_unit.is_leader:
            if this_unit.alive_troop_follower:
                this_unit.change_formation("group")
            if this_unit.alive_leader_follower:
                this_unit.change_formation("army")
        if self.player_unit:  # select player unit by default if control only one
            if this_unit.map_id == self.player_unit:  # get player unit
                self.player_unit = this_unit
                self.player_unit.player_control = True
                self.battle_camera.change_layer(self.player_unit, 999999)
                portrait = transform.smoothscale(this_unit.portrait, (150 * self.screen_scale[0],
                                                                      150 * self.screen_scale[1]))
                self.portrait_rect = portrait.get_rect(center=(portrait.get_width() / 1.6,
                                                               portrait.get_height() * 0.95))
                self.background.blit(portrait, self.portrait_rect)  # add portrait to screen
                if self.camera_mode == "Follow":
                    self.true_camera_pos = self.player_unit.base_pos
                    self.camera_fix()
    if not self.player_unit:  # no player unit clean UI a bit
        portrait = self.empty_portrait
        self.portrait_rect = portrait.get_rect(center=(portrait.get_width() / 1.6,
                                                       portrait.get_height() * 0.95))
        self.background.blit(portrait, self.portrait_rect)  # add portrait to screen
        self.weapon_ui.equipped_weapon = None  # reset weapon ui
        self.weapon_ui.image = self.weapon_ui.base_image.copy()
