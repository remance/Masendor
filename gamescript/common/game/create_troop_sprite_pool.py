import random

from PIL import Image

import pygame


def create_troop_sprite_pool(self, who_todo, preview=False, max_preview_size=200):
    weapon_list = self.troop_data.weapon_list
    animation_sprite_pool = {}  # TODO need to add for subunit creator
    weapon_common_type_list = tuple(set(["_" + value["Common"] + "_" for key, value in weapon_list.items() if
                                         key != "" and type(value["Common"]) is not int]))  # common type animation set
    weapon_attack_type_list = tuple(set(["_" + value["Attack"] + "_" for key, value in weapon_list.items() if
                                         key != "" and type(value["Attack"]) is not int]))  # attack animation set
    who_todo = {key: value for key, value in who_todo.items() if key not in (0, "h1") and
                value["Sprite ID"] != ""}  # skip None troop or one with no sprite data
    for subunit_id, this_subunit in who_todo.items():
        sprite_id = str(this_subunit["Sprite ID"])
        race = self.troop_data.race_list[this_subunit["Race"]]["Name"]
        mount_race = "None"
        final_race_name = race + "_"
        troop_armour = "None"
        troop_armour_id = 0
        if this_subunit["Armour"]:
            troop_armour_id = this_subunit["Armour"][0]
            troop_armour = self.troop_data.armour_list[troop_armour_id]["Name"]

        armour_name = (troop_armour, "None")
        armour_id = (troop_armour_id, 0)
        if this_subunit["Mount"]:
            mount_race = self.troop_data.mount_list[this_subunit["Mount"][0]]["Race"]  # get mount id
            mount_race = self.troop_data.race_list[mount_race]["Name"]  # replace id with name
            final_race_name = race + "&" + mount_race + "_"
            armour_name = (troop_armour, self.troop_data.mount_armour_list[this_subunit["Mount"][2]]["Name"])
            armour_id = (troop_armour_id, this_subunit["Mount"][2])

        primary_main_weapon = 1
        primary_sub_weapon = 1
        secondary_main_weapon = 1
        secondary_sub_weapon = 1

        if this_subunit["Primary Main Weapon"]:
            primary_main_weapon = this_subunit["Primary Main Weapon"][0]
        if this_subunit["Primary Sub Weapon"]:
            primary_sub_weapon = this_subunit["Primary Sub Weapon"][0]
        if this_subunit["Secondary Main Weapon"]:
            secondary_main_weapon = this_subunit["Secondary Main Weapon"][0]
        if this_subunit["Secondary Sub Weapon"]:
            secondary_sub_weapon = this_subunit["Secondary Sub Weapon"][0]

        hand_weapon_list = (
            (primary_main_weapon, primary_sub_weapon), (secondary_main_weapon, secondary_sub_weapon))

        weapon_key = (str(primary_main_weapon) + "," + str(primary_sub_weapon),
                      str(secondary_main_weapon) + "," + str(secondary_sub_weapon))
        if type(subunit_id) is int:
            skill_data = self.troop_data.skill_list
        else:
            skill_data = self.leader_data.skill_list

        skill_list = [skill_data[skill]["Action"][0] for skill in this_subunit["Skill"] if skill in skill_data]

        weapon_skill_list = weapon_list[primary_main_weapon]["Skill"] + \
                            weapon_list[primary_sub_weapon]["Skill"] + \
                            weapon_list[secondary_main_weapon]["Skill"] + \
                            weapon_list[secondary_sub_weapon]["Skill"]
        weapon_skill_list = [self.troop_data.skill_list[skill]["Action"][0] for skill in weapon_skill_list if
                             skill in self.troop_data.skill_list]
        skill_list += weapon_skill_list
        skill_list = tuple(set([item for item in skill_list if item != "Action"]))

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
            animation = [this_animation for this_animation in self.generic_animation_pool if final_race_name in
                         this_animation]
            # get animation with weapon
            animation = [this_animation for this_animation in animation
                         if (any(ext in this_animation for ext in weapon_common_type_list) is False or
                             "_any_" in this_animation or weapon_common_action[0][0] in this_animation) and
                         (any(ext in this_animation for ext in weapon_attack_type_list) is False or
                          (weapon_attack_action[0][0] in this_animation and ("_Main_" in this_animation or
                                                                             "_Both_" in this_animation)))]
            # remove animation not suitable for preview
            animation = [this_animation for this_animation in animation if
                         any(ext in this_animation for ext in
                             ("_Default", "_Die", "_Flee", "_Damaged", "KnockDown",
                              "_Standup", "_HeavyDamaged")) is False and "_Sub_" not in this_animation]
            if len(animation) > 0:
                animation = random.choice(animation)  # random animation
            else:  # no animation found, use race default
                animation = race + "_Default"
            frame_data = random.choice(self.generic_animation_pool[animation])  # random frame
            animation_property = self.generic_animation_pool[animation][0]["animation_property"].copy()

            if type(subunit_id) is int:
                sprite_data = self.troop_data.troop_sprite_list[sprite_id]
            else:
                sprite_data = self.leader_data.leader_sprite_list[sprite_id]

            idle_animation_name = final_race_name + weapon_common_action[0][0] + "_Idle"
            if idle_animation_name not in self.generic_animation_pool:  # try any
                idle_animation_name = final_race_name + "any_Idle"

            sprite_dict = self.create_troop_sprite(animation, this_subunit["Size"], frame_data,
                                                   sprite_data, animation_property,
                                                   (0, subunit_weapon_list[0],
                                                    (self.troop_data.weapon_list[primary_main_weapon]["Hand"],
                                                     self.troop_data.weapon_list[primary_sub_weapon]["Hand"])), armour_name,
                                                   self.generic_animation_pool[idle_animation_name][0], False)
            sprite_pic, center_offset = crop_sprite(sprite_dict["sprite"])

            scale = min(max_preview_size * self.screen_scale[0] / sprite_pic.get_width(),
                        max_preview_size * self.screen_scale[1] / sprite_pic.get_height())
            if scale < 1:  # scale down to fit ui like encyclopedia
                sprite_pic = pygame.transform.smoothscale(sprite_pic, (
                    sprite_pic.get_width() * scale,
                    sprite_pic.get_height() * scale))

            animation_sprite_pool[subunit_id] = {"sprite": sprite_pic,
                                                 "animation_property": sprite_dict["animation_property"],
                                                 "frame_property": sprite_dict[
                                                     "frame_property"],
                                                 "center_offset": center_offset}  # preview pool use subunit_id only

        else:
            if sprite_id not in animation_sprite_pool:  # troop can share sprite preset id but different gear
                animation_sprite_pool[sprite_id] = {}

            next_level = animation_sprite_pool[sprite_id]
            if race not in next_level:
                next_level[race] = {}

            next_level = next_level[race]
            if mount_race not in next_level:
                next_level[mount_race] = {}

            next_level = next_level[mount_race]
            if armour_id[0] not in next_level:
                next_level[armour_id[0]] = {}

            next_level = next_level[armour_id[0]]
            if armour_id[1] not in next_level:
                next_level[armour_id[1]] = {}

            next_level = next_level[armour_id[1]]
            if weapon_key[0] not in next_level:
                next_level[weapon_key[0]] = {}
            if weapon_key[1] not in next_level:
                next_level[weapon_key[1]] = {}
            animation_list = list(self.generic_animation_pool.keys())
            animation_list = [item for item in animation_list if "_Default" in item] + \
                             [item for item in animation_list if "_Default" not in item]  # move default to first
            animation_list = [this_animation for this_animation in animation_list if "_Preview" not in
                              this_animation and final_race_name in this_animation and
                              ("_Skill_" not in this_animation or any(ext in this_animation for ext in skill_list))]
            temp_animation_list = animation_list.copy()
            animation_list = [this_animation for this_animation in animation_list if "_any_" not in this_animation
                              and any(ext in this_animation for ext in ("_Main_", "_Sub_", "_Both_")) is False and
                              (any(ext in this_animation for ext in weapon_common_type_list)) is False]
            temp_list = []
            for weapon_set_index, weapon_set in enumerate(
                    subunit_weapon_list):
                for weapon_index, weapon in enumerate(weapon_set):
                    for this_animation in temp_animation_list:
                        if any(ext in this_animation for ext in
                               ("_Main_", "_Sub_", "_Both_")) is False:  # common animation
                            if (weapon_common_action[weapon_set_index][weapon_index] in this_animation or
                                    "_any_" in this_animation) and weapon_index == 0:  # keep only for main weapon
                                temp_list.append(this_animation)
                        elif ((weapon_common_action[weapon_set_index][weapon_index] in this_animation and
                                weapon_attack_action[weapon_set_index][weapon_index] in this_animation and
                               (("_Main_", "_Sub_")[weapon_index] in this_animation or "_Both_" in this_animation) or
                              "_Charge" in this_animation)):  # attack animation
                            temp_list.append(this_animation)
                    for this_animation in reversed(
                            temp_list):  # check if weapon common type and "any" for same animation exist, remove any
                        if "_any_" in this_animation and any(weapon_common_action[weapon_set_index][weapon_index] in
                                                             animation and this_animation.split("_")[-1] in animation
                                                             for animation in temp_list):
                            temp_list.remove(this_animation)
                    animation_list += temp_list

            animation_list = tuple(set(animation_list))

            for animation in animation_list:  # use one side in the list for finding animation name
                animation_property = self.generic_animation_pool[animation][0]["animation_property"].copy()
                for weapon_set_index, weapon_set in enumerate(
                        subunit_weapon_list):  # create animation for each weapon set
                    current_in_pool = next_level[weapon_key[weapon_set_index]]
                    for weapon_index, weapon in enumerate(weapon_set):
                        make_animation = False
                        both_weapon_set = False
                        both_main_sub_weapon = False
                        name_input = animation + "/" + str(weapon_set_index)
                        # TODO consider later whether to make any animation mean no weapon at all so keep only as one for all set
                        if "_any_" in name_input:  # replace any type to weapon action name for reading later
                            name_input = name_input.replace("_any_", "_" + weapon_common_action[weapon_set_index][
                                weapon_index] + "_")
                        if "_Both_" in name_input:
                            name_input = name_input.replace("_Both_", ("_Main_", "_Sub_")[weapon_index])
                            both_main_sub_weapon = True
                        if "_Skill_" in name_input:  # skill animation
                            for skill in skill_list:  # not make animation for troop with no related skill animation
                                if skill in name_input:
                                    make_animation = True
                                    break
                        elif any(ext in name_input for ext in weapon_common_type_list) is False:
                            # animation with no weapon like die, damaged
                            if any(ext in name_input for ext in weapon_attack_type_list) is False:
                                name_input = name_input[:-2]  # no need to make it into 2 sets since no weapon
                            make_animation = True
                            if weapon_set_index == 0:  # make for another weapon set as well
                                both_weapon_set = True
                        elif weapon_common_action[weapon_set_index][weapon_index] in name_input:
                            if any(ext in name_input for ext in weapon_attack_type_list) is False and \
                                    "_Charge" not in name_input:  # common animation with weapon like idle
                                make_animation = True
                            elif (weapon_attack_action[weapon_set_index][weapon_index] in name_input or
                                  "_Charge" in name_input) and ("_Main_", "_Sub_")[weapon_index] in name_input:  # attack animation and charge
                                make_animation = True
                        if make_animation and name_input not in current_in_pool:
                            final_name = name_input
                            final_name = "_".join(final_name.split("_")[1:])  # remove race name
                            if weapon_common_action[weapon_set_index][weapon_index] in name_input:
                                # remove common action name
                                final_name = final_name.replace(weapon_common_action[weapon_set_index][weapon_index] + "_", "")
                            current_in_pool[final_name] = {}
                            if both_weapon_set:
                                next_level[weapon_key[1]][final_name] = {}
                        else:
                            make_animation = False
                        if make_animation:
                            new_direction = "r_side"
                            opposite_direction = "l_side"
                            current_in_pool[final_name][new_direction] = {}
                            if both_weapon_set:
                                next_level[weapon_key[1]][final_name][new_direction] = {}
                            current_in_pool[final_name][opposite_direction] = {}
                            if both_weapon_set:
                                next_level[weapon_key[1]][final_name][opposite_direction] = {}
                            current_in_pool[final_name]["frame_number"] = len(self.generic_animation_pool[animation]) - 1
                            for frame_num, frame_data in enumerate(
                                    self.generic_animation_pool[animation]):
                                if type(subunit_id) is int:
                                    sprite_data = self.troop_data.troop_sprite_list[sprite_id]
                                else:
                                    sprite_data = self.leader_data.leader_sprite_list[sprite_id]

                                try:
                                    idle_animation = self.generic_animation_pool[
                                        final_race_name + weapon_common_action[weapon_set_index][0] + "_Idle"]
                                except KeyError:  # try any
                                    idle_animation = self.generic_animation_pool[
                                        final_race_name + "any_Idle"]

                                if both_main_sub_weapon:
                                    for key in frame_data:
                                        if "_Sub_" in name_input:
                                            if "main_weapon" in key:
                                                old_main_weapon_stat = frame_data[key].copy()
                                                frame_data[key] = frame_data[key.replace("main", "sub")].copy()
                                                frame_data[key.replace("main", "sub")] = old_main_weapon_stat

                                sprite_dict = self.create_troop_sprite(name_input, this_subunit["Size"],
                                                                       frame_data, sprite_data, animation_property,
                                                                       (weapon_set_index, weapon_set,
                                                                        (self.troop_data.weapon_list[
                                                                             hand_weapon_list[weapon_set_index][
                                                                            0]]["Hand"],
                                                                         self.troop_data.weapon_list[
                                                                             hand_weapon_list[weapon_set_index][
                                                                                 1]]["Hand"])),
                                                                       armour_name, idle_animation[0],
                                                                       both_main_sub_weapon)
                                sprite_pic = sprite_dict["sprite"]
                                sprite_pic, center_offset = crop_sprite(sprite_pic)
                                sprite_pic = pygame.transform.smoothscale(sprite_pic, (
                                    sprite_pic.get_width() * self.screen_scale[0],
                                    sprite_pic.get_height() * self.screen_scale[1]))

                                play_time_mod = 1  # add play_time_mod if existed in property
                                for this_property in sprite_dict["frame_property"]:
                                    if "play_time_mod_" in this_property:
                                        play_time_mod = float(this_property.split("_")[-1])
                                if play_time_mod == 1:  # no time mod in frame property, check for animation
                                    for this_property in sprite_dict["animation_property"]:
                                        if "play_time_mod_" in this_property:
                                            play_time_mod = float(this_property.split("_")[-1])
                                current_in_pool[final_name][frame_num] = \
                                    {"animation_property": sprite_dict["animation_property"],
                                     "frame_property": sprite_dict["frame_property"],
                                     "dmg_sprite": sprite_dict["dmg_sprite"]}
                                if play_time_mod != 1:
                                    current_in_pool[final_name][frame_num]["play_time_mod"] = play_time_mod
                                current_in_pool[final_name][new_direction][frame_num] = \
                                    {"sprite": sprite_pic, "center_offset": center_offset}

                                if both_weapon_set:
                                    next_level[weapon_key[1]][final_name][frame_num] = \
                                        {"animation_property": sprite_dict["animation_property"],
                                         "frame_property": sprite_dict["frame_property"],
                                         "dmg_sprite": sprite_dict["dmg_sprite"]}
                                    if play_time_mod != 1:
                                        next_level[weapon_key[1]][final_name][frame_num]["play_time_mod"] = play_time_mod

                                    next_level[weapon_key[1]][final_name][new_direction][frame_num] = \
                                        {"sprite": sprite_pic, "center_offset": center_offset}
                                if opposite_direction is not None:  # flip sprite for opposite direction
                                    current_in_pool[final_name][opposite_direction][frame_num] = {
                                        "sprite": pygame.transform.flip(sprite_pic,
                                                                        True, False),
                                        "center_offset": (-center_offset[0], center_offset[1])}
                                    if both_weapon_set:
                                        next_level[weapon_key[1]][final_name][opposite_direction][frame_num] = {
                                            "sprite": pygame.transform.flip(sprite_pic,
                                                                            True, False),
                                            "center_offset": (-center_offset[0], center_offset[1])}

    return animation_sprite_pool


def crop_sprite(sprite_pic):
    low_x0 = float("inf")  # lowest x0
    low_y0 = float("inf")  # lowest y0
    high_x1 = 0  # highest x1
    high_y1 = 0  # highest y1

    # Find optimal cropped sprite size and center offset
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

    center = ((sprite_pic.get_width() / 2), (sprite_pic.get_height() / 2))

    # Crop transparent area only of surface
    size = sprite_pic.get_size()
    sprite_pic = pygame.image.tostring(sprite_pic,
                                       "RGBA")  # convert image to string data for filtering effect
    sprite_pic = Image.frombytes("RGBA", size, sprite_pic)  # use PIL to get image data
    sprite_pic = sprite_pic.crop((low_x0, low_y0, high_x1, high_y1))
    size = sprite_pic.size
    sprite_pic = sprite_pic.tobytes()
    sprite_pic = pygame.image.fromstring(sprite_pic, size,
                                         "RGBA")  # convert image back to a pygame surface

    # Find center offset after crop by finding width and height difference of longer side
    center_x_offset = ((low_x0 + high_x1) / 2) + (((100 - low_x0) - (high_x1 - 100)) / 10)
    center_y_offset = ((low_y0 + high_y1) / 2) + (((100 - low_y0) - (high_y1 - 100)) / 10)
    center_offset = (center[0] - center_x_offset, center[1] - center_y_offset)

    # sprite_pic_new = pygame.Surface(size)
    # sprite_pic_new.fill((0,0,0))
    # rect = sprite_pic.get_rect(topleft=(0, 0))
    # sprite_pic_new.blit(sprite_pic, rect)
    return sprite_pic, center_offset