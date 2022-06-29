import random

import pygame

from gamescript.common.subunit import make_sprite

make_sprite = make_sprite.make_sprite


def create_sprite_pool(self, direction_list, genre_sprite_size, screen_scale, who_todo, preview=False):
    # TODO maybe add body pos and size for check collide?
    animation_sprite_pool = {}  # TODO need to add for subunit creator
    weapon_common_type_list = list(set(["_" + value["Common"] + "_" for value in self.generic_action_data.values()]))  # list of all common type animation set
    weapon_attack_type_list = list(set(["_" + value["Attack"] + "_" for value in self.generic_action_data.values()]))  # list of all attack set
    for subunit_id, this_subunit in who_todo.items():
        try:
            if subunit_id not in animation_sprite_pool and subunit_id not in (0, "h1"):  # skip None troop
                animation_sprite_pool[subunit_id] = {}

                race = self.troop_data.race_list[this_subunit["Race"]]["Name"]
                mount_race = self.troop_data.mount_list[this_subunit["Mount"][0]]["Race"]

                this_subunit["Size"] = self.troop_data.race_list[this_subunit["Race"]]["Size"] / 10  # TODO add mount

                primary_main_weapon = this_subunit["Primary Main Weapon"][0]
                primary_sub_weapon = this_subunit["Primary Sub Weapon"][0]
                secondary_main_weapon = this_subunit["Secondary Main Weapon"][0]
                secondary_sub_weapon = this_subunit["Secondary Sub Weapon"][0]
                armour = (self.armour_data.armour_list[this_subunit["Armour"][0]]["Name"],
                          self.troop_data.mount_armour_list[this_subunit["Mount"][2]]["Name"])
                subunit_weapon_list = [(self.weapon_data.weapon_list[primary_main_weapon]["Name"],
                                        self.weapon_data.weapon_list[primary_sub_weapon]["Name"])]

                weapon_common_action = [(self.generic_action_data[subunit_weapon_list[0][0]]["Common"],
                                         self.generic_action_data[subunit_weapon_list[0][1]]["Common"])]
                weapon_attack_action = [(self.generic_action_data[subunit_weapon_list[0][0]]["Attack"],
                                         self.generic_action_data[subunit_weapon_list[0][1]]["Attack"])]
                if (primary_main_weapon, primary_sub_weapon) != (secondary_main_weapon, secondary_sub_weapon):
                    subunit_weapon_list = [subunit_weapon_list[0],
                                           (self.weapon_data.weapon_list[secondary_main_weapon]["Name"],
                                            self.weapon_data.weapon_list[secondary_sub_weapon]["Name"])]
                    weapon_common_action = [weapon_common_action[0], (self.generic_action_data[subunit_weapon_list[1][0]]["Common"],
                                                                      self.generic_action_data[subunit_weapon_list[1][1]]["Common"])]
                    weapon_attack_action = [weapon_attack_action[0], (self.generic_action_data[subunit_weapon_list[1][0]]["Attack"],
                                                                       self.generic_action_data[subunit_weapon_list[1][1]]["Attack"])]
                if preview:  # only create random right side sprite
                    animation = [this_animation for this_animation in self.generic_animation_pool[0] if race in this_animation and "&" not in this_animation]  # TODO remove last condition when has mount
                    animation = [this_animation for this_animation in animation
                                 if (any(ext in this_animation for ext in weapon_common_type_list) is False or
                                     weapon_common_action[0][0] in this_animation) and
                                 (any(ext in this_animation for ext in weapon_attack_type_list) is False or
                                  (weapon_attack_action[0][0] in this_animation and ("Main", "Sub")[0] in this_animation))
                                 and "Default" not in this_animation]  # get animation with weapon
                    if len(animation) > 0:
                        animation = random.choice(animation)  # random animation
                    else:
                        animation = race+"_Default"

                    frame_data = random.choice(self.generic_animation_pool[1][animation])  # random frame
                    animation_property = self.generic_animation_pool[0][animation][0]["animation_property"].copy()
                    if type(subunit_id) == int:
                        sprite_data = self.troop_data.troop_sprite_list[str(subunit_id)]
                    else:
                        leader_id = int(subunit_id.replace("h", ""))
                        if leader_id < 10000:
                            sprite_data = self.leader_data.leader_sprite_list[str(leader_id)]
                        else:  # common leader
                            sprite_data = self.leader_data.common_leader_sprite_list[str(leader_id)]
                    sprite_dict = make_sprite(animation, this_subunit["Size"], frame_data,
                                              sprite_data, self.gen_body_sprite_pool,
                                              self.gen_weapon_sprite_pool,
                                              self.gen_armour_sprite_pool,
                                              self.effect_sprite_pool, animation_property,
                                              self.weapon_joint_list,
                                              (0, subunit_weapon_list[0]), armour,
                                              self.hair_colour_list, self.skin_colour_list,
                                              genre_sprite_size, screen_scale)

                    animation_sprite_pool[subunit_id] = {"sprite": sprite_dict["sprite"],
                         "animation_property": sprite_dict["animation_property"],
                         "frame_property": sprite_dict["frame_property"]}
                else:
                    for animation in self.generic_animation_pool[0]:  # use one side in the list for finding animation name
                        # only get animation with same race and mount after "&"
                        # if race in animation and ((mount_race == "Any" and "&" not in animation) or
                        #                           ("&" in animation and mount_race in animation.split("&")[1])):
                        if race in animation and "&" not in animation and "Preview" not in animation:
                            animation_property = self.generic_animation_pool[0][animation][0]["animation_property"].copy()
                            for weapon_set_index, weapon_set in enumerate(
                                    subunit_weapon_list):  # create animation for each weapon set
                                for weapon_index, weapon in enumerate(weapon_set):
                                    # first check if animation is common weapon type specific and match with weapon, then check if it is attack specific
                                    make_animation = True
                                    animation_type = "normal"
                                    name_input = animation
                                    if any(ext in animation for ext in weapon_common_type_list):
                                        animation_type = "weapon"
                                        name_input = animation + "/" + str(weapon_set_index)
                                    if animation_type == "normal":
                                        if name_input not in animation_sprite_pool[subunit_id]:
                                            animation_sprite_pool[subunit_id][name_input] = {}
                                        else:
                                            make_animation = False
                                    elif animation_type == "weapon":
                                        if (any(ext in animation for ext in weapon_common_type_list) is False or
                                            weapon_common_action[weapon_set_index][weapon_index] in animation) and \
                                                (any(ext in animation for ext in weapon_attack_type_list) is False or (
                                                        weapon_attack_action[weapon_set_index][weapon_index] in animation and
                                                        ("Main", "Sub")[weapon_index] in animation)):
                                            if name_input not in animation_sprite_pool[subunit_id]:
                                                animation_sprite_pool[subunit_id][name_input] = {}
                                        else:
                                            make_animation = False
                                    if make_animation:
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
                                            animation_sprite_pool[subunit_id][name_input][
                                                new_direction] = {}
                                            if opposite_direction is not None:
                                                animation_sprite_pool[subunit_id][name_input][
                                                    opposite_direction] = {}
                                            for frame_num, frame_data in enumerate(
                                                    self.generic_animation_pool[index][animation]):
                                                if type(subunit_id) == int:
                                                    sprite_data = self.troop_data.troop_sprite_list[str(subunit_id)]
                                                else:
                                                    leader_id = int(subunit_id.replace("h", ""))
                                                    if leader_id < 10000:
                                                        sprite_data = self.leader_data.leader_sprite_list[str(leader_id)]
                                                    else:  # common leader
                                                        sprite_data = self.leader_data.common_leader_sprite_list[str(leader_id)]
                                                sprite_dict = make_sprite(animation, this_subunit["Size"], frame_data,
                                                                          sprite_data, self.gen_body_sprite_pool,
                                                                          self.gen_weapon_sprite_pool,
                                                                          self.gen_armour_sprite_pool,
                                                                          self.effect_sprite_pool, animation_property,
                                                                          self.weapon_joint_list,
                                                                          (weapon_set_index, weapon_set), armour,
                                                                          self.hair_colour_list, self.skin_colour_list,
                                                                          genre_sprite_size, screen_scale)

                                                animation_sprite_pool[subunit_id][name_input][new_direction][frame_num] = \
                                                    {"sprite": sprite_dict["sprite"],
                                                     "animation_property": sprite_dict["animation_property"],
                                                     "frame_property": sprite_dict["frame_property"]}
                                                if opposite_direction is not None:  # flip sprite for opposite direction
                                                    animation_sprite_pool[subunit_id][ name_input][ opposite_direction][ frame_num] = {
                                                        "sprite": pygame.transform.flip(sprite_dict["sprite"].copy(), True,
                                                                                        False),
                                                        "animation_property": sprite_dict["animation_property"],
                                                        "frame_property": sprite_dict["frame_property"]}
        except KeyError:  # any key error will return nothing
            pass
    return animation_sprite_pool
