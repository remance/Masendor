import numpy as np


def die(self):
    self.inspect_image_original3.blit(self.health_image_list[4], self.health_image_rect)  # blit white hp bar
    self.block_original.blit(self.health_image_list[4], self.health_block_rect)
    self.zoom_scale()
    self.last_health_state = 0
    self.skill_cooldown = {}  # remove all cooldown
    self.skill_effect = {}  # remove all skill effects

    self.block.blit(self.block_original, self.corner_image_rect)
    self.red_border = True  # to prevent red border appear when dead

    self.unit.dead_change = True

    if self in self.battle.battle_camera:
        self.battle.battle_camera.change_layer(sprite=self, new_layer=1)
    self.battle.alive_subunit_list.remove(self)
    self.unit.subunits.remove(self)

    self.command_action = ("Die", "uninterruptible")
    self.reset_animation()
    self.current_action = self.command_action  # replace any current action
    self.pick_animation()

    for subunit in self.unit.subunits_array.flat:  # remove from index array
        if subunit == self.game_id:
            self.unit.subunit_list = np.where(self.unit.subunit_list == self.game_id, 0, self.unit.subunit_list)
            break

    self.gone_leader_process("Destroyed")

    self.battle.event_log.add_log([0, str(self.board_pos) + " " + str(self.name)
                                   + " in " + self.unit.leader[0].name
                                   + "'s unit is destroyed"], [3])  # add log to say this subunit is destroyed in subunit tab
