import numpy as np

die_command_action = {"name": "Die", "uninterruptible": True}


def die(self, how):
    """Subunit left battle, either dead or flee"""
    self.inspect_base_image3.blit(self.health_image_list[4], self.health_image_rect)  # blit white hp bar
    self.block_base_image.blit(self.health_image_list[4], self.health_block_rect)
    self.zoom_scale()
    self.last_health_state = 0
    self.skill_cooldown = {}  # remove all cooldown
    self.skill_effect = {}  # remove all skill effects

    self.block_image.blit(self.block_base_image, self.corner_image_rect)
    self.red_border = True  # to prevent red border from appearing when dead

    self.unit.dead_change = True
    if how == "dead":
        if self in self.battle.battle_camera:
            self.battle.battle_camera.change_layer(sprite=self, new_layer=0)

            self.command_action = die_command_action
            self.top_interrupt_animation = True
            self.current_action = self.command_action  # replace any current action
            self.pick_animation()

            self.gone_leader_process("Destroyed")

            self.battle.event_log.add_log((0, str(self.board_pos) + " " + str(self.name)
                                           + " in " + self.unit.leader[0].name
                                           + "'s unit is destroyed"),
                                          [3])  # add log to say this subunit is destroyed in subunit tab

    elif how == "flee":
        self.battle.flee_troop_number[
            self.team] += self.troop_number  # add number of troop retreat from battle
        self.troop_loss(self.troop_number)
        self.battle.battle_camera.remove(self)

    if self.shoot_line is not None:
        self.shoot_line.kill()
        self.shoot_line = None

    if self in self.battle.battle_subunit_list:
        self.battle.subunit_pos_list.pop(self.battle.battle_subunit_list.index(self))
        self.battle.battle_subunit_list.remove(self)
    if self in self.unit.alive_subunit_list:
        self.unit.alive_subunit_list.remove(self)

    self.unit.subunit_id_array = np.where(self.unit.subunit_id_array == self.game_id, 0, self.unit.subunit_id_array)

    if self.player_manual_control:
        self.battle.camera_mode = "Free"  # camera become free when player char die so can look over the battle
