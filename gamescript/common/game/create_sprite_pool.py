import random

import pygame
from PIL import Image
from gamescript.common.subunit import create_troop_sprite

create_troop_sprite = create_troop_sprite.create_troop_sprite


def create_sprite_pool(self, direction_list, genre_sprite_size, screen_scale, who_todo, preview=False):
    weapon_list = self.troop_data.weapon_list
    animation_sprite_pool = {}  # TODO need to add for subunit creator
    weapon_common_type_list = list(set(["_" + value["Common"] for key, value in weapon_list.items() if
                                        key != ""]))  # list of all common type animation set
    weapon_attack_type_list = list(set(["_" + value["Attack"] for key, value in weapon_list.items() if
                                        key != ""]))  # list of all attack set
    for subunit_id, this_subunit in who_todo.items():
        # try:
        if subunit_id not in (0, "h1") and this_subunit["Sprite ID"] != "":  # skip None troop
            sprite_id = str(this_subunit["Sprite ID"])
            race = self.troop_data.race_list[this_subunit["Race"]]["Name"]
            mount_race = self.troop_data.mount_list[this_subunit["Mount"][0]]["Race"]  # get mount id
            mount_race = self.troop_data.race_list[mount_race]["Name"]  # replace id with name
            mount_race_name = mount_race
            if mount_race != "None":
                mount_race_name = mount_race_name + "_"

            primary_main_weapon = this_subunit["Primary Main Weapon"][0]
            primary_sub_weapon = this_subunit["Primary Sub Weapon"][0]
            secondary_main_weapon = this_subunit["Secondary Main Weapon"][0]
            secondary_sub_weapon = this_subunit["Secondary Sub Weapon"][0]
            hand_weapon_list = (
            (primary_main_weapon, primary_sub_weapon), (secondary_main_weapon, secondary_sub_weapon))
            armour = (self.troop_data.armour_list[this_subunit["Armour"][0]]["Name"],
                      self.troop_data.mount_armour_list[this_subunit["Mount"][2]]["Name"])

            weapon_key = (str(primary_main_weapon) + "," + str(primary_sub_weapon),
                          str(secondary_main_weapon) + "," + str(secondary_sub_weapon))
            skill_list = this_subunit["Skill"] + weapon_list[primary_main_weapon]["Skill"] + \
                         weapon_list[primary_sub_weapon]["Skill"] + \
                         weapon_list[secondary_main_weapon]["Skill"] + \
                         weapon_list[secondary_sub_weapon]["Skill"]
            skill_list = list(set([item for item in skill_list if item != 0]))

            subunit_weapon_list = [(weapon_list[primary_main_weapon]["Name"],
                                    weapon_list[primary_sub_weapon]["Name"])]

            weapon_common_action = [(weapon_list[primary_main_weapon]["Common"],
                                     weapon_list[primary_sub_weapon]["Common"])]
            weapon_attack_action = [(weapon_list[primary_main_weapon]["Attack"],
                                     weapon_list[primary_sub_weapon]["Attack"])]

            if (primary_main_weapon, primary_sub_weapon) != (secondary_main_weapon, secondary_sub_weapon):
                subunit_weapon_list = [subunit_weapon_list[0],
                                       (weapon_list[secondary_main_weapon]["Name"],
                                        weapon_list[secondary_sub_weapon]["Name"])]
                weapon_common_action = [weapon_common_action[0],
                                        (weapon_list[secondary_main_weapon]["Common"],
                                         weapon_list[secondary_sub_weapon]["Common"])]
                weapon_attack_action = [weapon_attack_action[0],
                                        (weapon_list[secondary_main_weapon]["Attack"],
                                         weapon_list[secondary_sub_weapon]["Attack"])]
            if preview:  # only create random right side sprite for preview in lorebook
                animation = [this_animation for this_animation in self.generic_animation_pool[0] if race in
                             this_animation and ((mount_race_name == "None" and "&" not in this_animation) or
                                                 mount_race_name in this_animation)]
                # get animation with weapon
                animation = [this_animation for this_animation in animation
                             if (any(ext in this_animation for ext in weapon_common_type_list) is False or
                                 weapon_common_action[0][0] in this_animation) and
                             (any(ext in this_animation for ext in weapon_attack_type_list) is False or
                              (weapon_attack_action[0][0] in this_animation and "_Main_" in this_animation))]
                # remove animation not suitable for preview
                animation = [this_animation for this_animation in animation if
                             any(ext in this_animation for ext in
                                 ("_Default", "_Die", "_Flee", "_Damaged")) is False and
                             "_Sub_" not in this_animation]
                if len(animation) > 0:
                    animation = random.choice(animation)  # random animation
                else:  # no animation found, use race default
                    animation = race + "_Default"

                frame_data = random.choice(self.generic_animation_pool[1][animation])  # random frame
                animation_property = self.generic_animation_pool[0][animation][0]["animation_property"].copy()

                sprite_data = self.troop_data.troop_sprite_list[sprite_id]
                sprite_dict = create_troop_sprite(animation, this_subunit["Size"], frame_data,
                                                  sprite_data, self.gen_body_sprite_pool,
                                                  self.gen_weapon_sprite_pool,
                                                  self.gen_armour_sprite_pool,
                                                  self.effect_sprite_pool, animation_property,
                                                  self.weapon_joint_list,
                                                  (0, subunit_weapon_list[0],
                                                   (self.troop_data.weapon_list[primary_main_weapon]["Hand"],
                                                    self.troop_data.weapon_list[primary_sub_weapon]["Hand"])),
                                                  armour, self.colour_list,
                                                  genre_sprite_size, screen_scale, self.troop_data.race_list)

                animation_sprite_pool[subunit_id] = {"sprite": sprite_dict["sprite"],
                                                     "animation_property": sprite_dict["animation_property"],
                                                     "frame_property": sprite_dict[
                                                         "frame_property"]}  # preview pool use subunit_id only
            else:
                low_x0 = float("inf")  # lowest x0
                low_y0 = float("inf")  # lowest y0
                high_x1 = 0  # highest x1
                high_y1 = 0  # highest y1

                if sprite_id not in animation_sprite_pool:  # troop can share sprite preset id but different gear
                    animation_sprite_pool[sprite_id] = {}

                next_level = animation_sprite_pool[sprite_id]
                if race not in next_level:
                    next_level[race] = {}

                next_level = next_level[race]
                if mount_race not in next_level:
                    next_level[mount_race] = {}

                next_level = next_level[mount_race]
                if this_subunit["Armour"][0] not in next_level:
                    next_level[this_subunit["Armour"][0]] = {}

                next_level = next_level[this_subunit["Armour"][0]]
                if this_subunit["Mount"][2] not in next_level:
                    next_level[this_subunit["Mount"][2]] = {}

                next_level = next_level[this_subunit["Mount"][2]]
                if weapon_key[0] not in next_level:
                    next_level[weapon_key[0]] = {}
                if weapon_key[1] not in next_level:
                    next_level[weapon_key[1]] = {}
                animation_list = list(self.generic_animation_pool[0].keys())
                animation_list = [item for item in animation_list if "Default" in item] + \
                                 [item for item in animation_list if "Default" not in item]
                for animation in animation_list:  # use one side in the list for finding animation name
                    if "Preview" not in animation and race in animation and \
                            ((mount_race_name == "None" and "&" not in animation) or mount_race_name in animation):
                        animation_property = self.generic_animation_pool[0][animation][0]["animation_property"].copy()
                        for weapon_set_index, weapon_set in enumerate(
                                subunit_weapon_list):  # create animation for each weapon set
                            current_in_pool = next_level[weapon_key[weapon_set_index]]
                            for weapon_index, weapon in enumerate(weapon_set):
                                # first check if animation is common weapon type specific and match with weapon, then check if it is attack specific
                                make_animation = True
                                name_input = animation + "/" + str(weapon_set_index)
                                if (any(ext in animation for ext in weapon_common_type_list) is False or
                                    weapon_common_action[weapon_set_index][weapon_index] in animation) and \
                                        (any(ext in animation for ext in weapon_attack_type_list) is False or (
                                                weapon_attack_action[weapon_set_index][weapon_index] in animation and
                                                ("Main", "Sub")[weapon_index] in animation)):
                                    if name_input not in current_in_pool:
                                        current_in_pool[name_input] = {}
                                else:
                                    make_animation = False

                                if "_Skill_" in animation:  # skill animation
                                    make_animation = False  # not make animation for troop with no related skill animation
                                    for skill in skill_list:
                                        if type(skill) == int:
                                            if skill in self.troop_data.skill_list:  # skip skill not in ruleset
                                                if self.troop_data.skill_list[skill]["Action"] and \
                                                        self.troop_data.skill_list[skill]["Action"][0] in animation:
                                                    make_animation = True
                                                    break
                                        else:  # leader skill
                                            if skill in self.leader_data.skill_list:  # skip skill not in ruleset
                                                if self.leader_data.skill_list[skill]["Action"] and \
                                                        self.leader_data.skill_list[skill]["Action"][0] in animation:
                                                    make_animation = True
                                                    break

                                if make_animation:
                                    for index, direction in enumerate(direction_list):
                                        new_direction = direction
                                        opposite_direction = None  # no opposite direction for front and back
                                        if "side" in direction:
                                            new_direction = "r_" + direction
                                            opposite_direction = "l_" + direction
                                        current_in_pool[name_input][new_direction] = {}
                                        if opposite_direction is not None:
                                            current_in_pool[name_input][opposite_direction] = {}
                                        for frame_num, frame_data in enumerate(
                                                self.generic_animation_pool[index][animation]):
                                            if type(subunit_id) == int:
                                                sprite_data = self.troop_data.troop_sprite_list[sprite_id]
                                            else:
                                                sprite_data = self.leader_data.leader_sprite_list[sprite_id]

                                            sprite_dict = create_troop_sprite(animation, this_subunit["Size"],
                                                                              frame_data,
                                                                              sprite_data, self.gen_body_sprite_pool,
                                                                              self.gen_weapon_sprite_pool,
                                                                              self.gen_armour_sprite_pool,
                                                                              self.effect_sprite_pool,
                                                                              animation_property,
                                                                              self.weapon_joint_list,
                                                                              (weapon_set_index, weapon_set,
                                                                               (self.troop_data.weapon_list[
                                                                                    hand_weapon_list[weapon_set_index][
                                                                                        0]]["Hand"],
                                                                                self.troop_data.weapon_list[
                                                                                    hand_weapon_list[weapon_set_index][
                                                                                        1]]["Hand"])),
                                                                              armour, self.colour_list,
                                                                              genre_sprite_size, screen_scale,
                                                                              self.troop_data.race_list)
                                            sprite_pic = sprite_dict["sprite"]
                                            if self.play_troop_animation == 0 and "_Default" not in animation:  # replace sprite with default if disable animation
                                                sprite_pic = \
                                                current_in_pool[tuple(current_in_pool.keys())[0]][new_direction][0][
                                                    "sprite"]

                                            # Find optimal cropped sprite size that all animation will share exact same center point
                                            size = sprite_pic.get_size()
                                            data = pygame.image.tostring(sprite_pic,
                                                                         "RGBA")  # convert image to string data for filtering effect
                                            data = Image.frombytes("RGBA", size, data)  # use PIL to get image data
                                            bbox = data.getbbox()
                                            if low_x0 > bbox[0]:
                                                low_x0 = bbox[0]
                                            if low_y0 > bbox[1]:
                                                low_y0 = bbox[1]
                                            if high_x1 < bbox[2]:
                                                high_x1 = bbox[2]
                                            if high_y1 < bbox[3]:
                                                high_y1 = bbox[3]

                                            current_in_pool[name_input][new_direction][frame_num] = \
                                                {"sprite": sprite_pic,
                                                 "animation_property": sprite_dict["animation_property"],
                                                 "frame_property": sprite_dict["frame_property"],
                                                 "dmg_sprite": sprite_dict["dmg_sprite"]}
                                            if opposite_direction is not None:  # flip sprite for opposite direction
                                                if self.play_troop_animation == 1 or "_Default" in animation:
                                                    current_in_pool[name_input][opposite_direction][frame_num] = {
                                                        "sprite": pygame.transform.flip(sprite_dict["sprite"].copy(),
                                                                                        True, False),
                                                        "animation_property": sprite_dict["animation_property"],
                                                        "frame_property": sprite_dict["frame_property"],
                                                        "dmg_sprite": sprite_dict["dmg_sprite"]}
                                                elif self.play_troop_animation == 0:
                                                    current_in_pool[name_input][opposite_direction][frame_num] = {
                                                        "sprite": current_in_pool[tuple(current_in_pool.keys())[0]][
                                                            opposite_direction][0]["sprite"],
                                                        "animation_property": sprite_dict["animation_property"],
                                                        "frame_property": sprite_dict["frame_property"],
                                                        "dmg_sprite": sprite_dict["dmg_sprite"]}

                for animation in current_in_pool:
                    for direction in current_in_pool[animation]:
                        for frame in current_in_pool[animation][direction]:
                            # Crop transparent area only of surface, only do for battle sprite
                            sprite_pic = current_in_pool[animation][direction][frame]["sprite"]
                            size = sprite_pic.get_size()
                            sprite_pic = pygame.image.tostring(sprite_pic,
                                                               "RGBA")  # convert image to string data for filtering effect
                            sprite_pic = Image.frombytes("RGBA", size, sprite_pic)  # use PIL to get image data
                            sprite_pic = sprite_pic.crop((low_x0, low_y0, high_x1, high_y1))
                            size = sprite_pic.size
                            sprite_pic = sprite_pic.tobytes()
                            sprite_pic = pygame.image.fromstring(sprite_pic, size,
                                                                 "RGBA")  # convert image back to a pygame surface
                            current_in_pool[animation][direction][frame]["sprite"] = sprite_pic

    # except KeyError:  # any key error will return nothing
    #     pass
    return animation_sprite_pool
