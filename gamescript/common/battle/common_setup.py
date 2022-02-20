import pygame

from gamescript.common import animation

make_sprite = animation.make_sprite


def create_sprite_pool(self, direction_list):  # TODO maybe add body pos and size for check collide?
    animation_sprite_pool = {}
    weapon_common_type_list = list(set(["_" + value["Common"] + "_" for value in self.generic_action_data.values()]))  # list of all common type animation set
    weapon_attack_type_list = list(set(["_" + value["Attack"] + "_" for value in self.generic_action_data.values()]))  # list of all attack set
    for this_subunit in self.subunit_updater:
        if this_subunit.troop_id not in animation_sprite_pool:
            animation_sprite_pool[this_subunit.troop_id] = {}
            armour = (self.armour_data.armour_list[this_subunit.armour_gear[0]]["Name"], this_subunit.mount_armour["Name"])
            subunit_weapon_list = [(self.weapon_data.weapon_list[this_subunit.primary_main_weapon[0]]["Name"],
                                    self.weapon_data.weapon_list[this_subunit.primary_sub_weapon[0]]["Name"])]

            weapon_common_action = [(self.generic_action_data[subunit_weapon_list[0][0]]["Common"],
                                     self.generic_action_data[subunit_weapon_list[0][1]]["Common"])]
            weapon_attack_action = [(self.generic_action_data[subunit_weapon_list[0][0]]["Attack"],
                                     self.generic_action_data[subunit_weapon_list[0][1]]["Attack"])]
            if (this_subunit.primary_main_weapon, this_subunit.primary_sub_weapon) != \
                    (this_subunit.secondary_main_weapon, this_subunit.secondary_sub_weapon):
                subunit_weapon_list = [subunit_weapon_list[0],
                                       (self.weapon_data.weapon_list[this_subunit.secondary_main_weapon[0]]["Name"],
                                        self.weapon_data.weapon_list[this_subunit.secondary_sub_weapon[0]]["Name"])]
                weapon_common_action = [weapon_common_action[0], (self.generic_action_data[subunit_weapon_list[1][0]]["Common"],
                                                                  self.generic_action_data[subunit_weapon_list[1][1]]["Common"])]
                weapon_attack_action = [(weapon_attack_action[0], (self.generic_action_data[subunit_weapon_list[1][0]]["Attack"],
                                                                   self.generic_action_data[subunit_weapon_list[1][1]]["Attack"]))]

            for animation in self.generic_animation_pool[0]:  # just use whatever side in the list for finding animation name for now
                if self.troop_data.race_list[this_subunit.race]["Name"] in animation:  # grab race animation
                    animation_property = self.generic_animation_pool[0][animation][0]["animation_property"].copy()
                    for weapon_set_index, weapon_set in enumerate(subunit_weapon_list):  # create animation for each weapon set
                        for weapon_index, weapon in enumerate(weapon_set):
                            # first check if animation is common weapon type specific and match with weapon, then check if it is attack specific
                            if (any(ext in weapon_common_type_list for ext in animation) is False or weapon_common_action[weapon_set_index][weapon_index] in animation) and \
                                (any(ext in weapon_attack_type_list for ext in animation) is False or (weapon_common_action[weapon_set_index][weapon_index] in animation and ("main", "sub")[weapon_index] in animation)):
                                if animation + "/" + str(weapon_set_index) not in animation_sprite_pool[this_subunit.troop_id]:
                                    animation_sprite_pool[this_subunit.troop_id][animation + "/" + str(weapon_set_index)] = {}
                                for index, direction in enumerate(direction_list):
                                    new_direction = direction
                                    opposite_direction = None  # no opposite direction for front and back
                                    if direction == "side":
                                        new_direction = "r_side"
                                        opposite_direction = "l_side"
                                    elif direction == "sideup":
                                        new_direction = "r_sideup"
                                        opposite_direction = "l_sideup"
                                    elif direction == "sidedown":
                                        new_direction = "r_sidedown"
                                        opposite_direction = "l_sidedown"
                                    animation_sprite_pool[this_subunit.troop_id][animation + "/" + str(weapon_set_index)][new_direction] = {}
                                    if opposite_direction is not None:
                                        animation_sprite_pool[this_subunit.troop_id][animation + "/" + str(weapon_set_index)][opposite_direction] = {}
                                    for frame_num, frame_data in enumerate(self.generic_animation_pool[index][animation]):
                                        sprite_dict = make_sprite(this_subunit.size, frame_data,
                                                                  self.troop_data.troop_sprite_list[str(this_subunit.troop_id)],
                                                                  self.gen_body_sprite_pool, self.gen_weapon_sprite_pool, self.gen_armour_sprite_pool,
                                                                  self.effect_sprite_pool, animation_property, self.weapon_joint_list,
                                                                  (weapon_set_index, weapon_set), armour,
                                                                  self.hair_colour_list, self.skin_colour_list)

                                        animation_sprite_pool[this_subunit.troop_id][animation + "/" + str(weapon_set_index)][new_direction][
                                            frame_num] = \
                                            {"sprite": sprite_dict["sprite"], "animation_property": sprite_dict["animation_property"],
                                             "frame_property": sprite_dict["frame_property"]}
                                        if opposite_direction is not None:  # flip sprite for opposite direction
                                            animation_sprite_pool[this_subunit.troop_id][animation + "/" + str(weapon_set_index)][
                                                opposite_direction][
                                                frame_num] = {"sprite": pygame.transform.flip(sprite_dict["sprite"].copy(), True, False),
                                                              "animation_property": sprite_dict["animation_property"],
                                                              "frame_property": sprite_dict["frame_property"]}
    return animation_sprite_pool
