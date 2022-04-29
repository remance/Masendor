import math
import pygame

from PIL import Image, ImageOps, ImageFilter, ImageEnhance

from gamescript import datastat
from gamescript.common import utility, animation
from gamescript.common.subunit import common_subunit_movement

stat_convert = datastat.stat_convert
rotation_xy = utility.rotation_xy

default_sprite_size = (200, 200)

rotation_list = common_subunit_movement.rotation_list
rotation_name = common_subunit_movement.rotation_name
rotation_dict = common_subunit_movement.rotation_dict


def start_set(self, zoom):
    """run once when battle start or subunit just get created"""
    self.zoom = zoom
    self.front_pos = self.make_front_pos()
    self.make_pos_range()
    self.zoom_scale()
    self.find_nearby_subunit()

    try:
        self.terrain, self.feature = self.get_feature(self.base_pos,
                                                      self.base_map)  # get new terrain and feature at each subunit position
        self.height = self.height_map.get_height(self.base_pos)  # current terrain height
        self.front_height = self.height_map.get_height(self.front_pos)  # terrain height at front position
    except AttributeError:
        pass

    self.grade_social_effect = self.unit.leader_social[self.grade_name]
    self.status_update()

    self.battle.alive_subunit_list.append(self)
    if self.team == 1:  # add sprite to team subunit group for collision
        group_collide = self.battle.team1_subunit
    elif self.team == 2:
        group_collide = self.battle.team2_subunit
    group_collide.add(self)

    self.sprite_pool = self.animation_sprite_pool[self.troop_id]  # grab only animation sprite that the subunit can use

    self.pick_animation()


def skill_convert(self, skill_list, add_charge_skill=False):
    """
    Convert skill id list to dict with its stat
    :param self: Subunit object
    :param skill_list: List of skill id
    :param add_charge_skill: Add charge skill to dict or not
    :return: Dict of skill with id as key and stat as value
    """
    skill_dict = list(set(skill_list))
    skill_dict = {x: self.troop_data.skill_list[x].copy() for x in skill_dict if
                  x != 0 and x in self.troop_data.skill_list}  # grab skill stat into dict
    if add_charge_skill:
        skill_dict[0] = self.troop_data.skill_list[self.charge_skill].copy()  # add charge skill with key 0
    skill_dict = {skill: skill_dict[skill] for skill in skill_dict if skill == 0 or   # keep skill if class match
                  (skill != 0 and (self.troop_data.skill_list[skill]["Troop Type"] == 0 or
                                   self.troop_data.skill_list[skill]["Troop Type"] == self.subunit_type + 1))}
    return skill_dict


def process_trait_skill(self):
    """
    Process subunit traits and skills into dict with their stat
    :param self: Subunit object
    """
    self.trait += self.armour_data.armour_list[self.armour_gear[0]]["Trait"]  # Apply armour trait to subunit
    self.trait = list(set([trait for trait in self.trait if trait != 0]))  # remove empty and duplicate traits
    if len(self.trait) > 0:
        self.trait = {x: self.troop_data.trait_list[x] for x in self.trait if
                      x in self.troop_data.trait_list}  # Any trait not available in ruleset will be ignored
        self.add_trait()

    self.troop_skill = [skill for skill in self.troop_skill if skill != 0 and
                        (self.troop_data.skill_list[skill]["Troop Type"] == 0 or
                         self.troop_data.skill_list[skill]["Troop Type"] == self.subunit_type + 1)]  # keep matched

    for weapon_set in self.weapon_skill:
        for weapon in self.weapon_skill[weapon_set]:
            skill = self.weapon_skill[weapon_set][weapon]
            if skill != 0 and (self.troop_data.skill_list[skill]["Troop Type"] != 0 and
                               self.troop_data.skill_list[skill]["Troop Type"] != self.subunit_type + 1):
                self.weapon_skill[weapon_set][weapon] = 0  # remove unmatch class skill
            else:
                self.skill.append(skill)
    self.skill = skill_convert(self, self.skill, add_charge_skill=True)


def create_inspect_sprite(self):
    """
    Create subunit sprite for furthest zoom and inspect ui
    :param self: Subunit object
    :return: Dict with sprites
    """
    # v Subunit image sprite in inspect ui and far zoom
    ui_image = self.unit_ui_images["ui_squad_player.png"].copy()  # Subunit block blue colour for team1 for shown in inspect ui
    if self.team == 2:
        ui_image = self.unit_ui_images["ui_squad_enemy.png"].copy()  # red colour

    image = pygame.Surface((ui_image.get_width() + 10, ui_image.get_height() + 10), pygame.SRCALPHA)  # subunit sprite image
    pygame.draw.circle(image, self.unit.colour, (image.get_width() / 2, image.get_height() / 2), ui_image.get_width() / 2)

    if self.subunit_type == 2:  # cavalry draw line on block
        pygame.draw.line(ui_image, (0, 0, 0), (0, 0), (ui_image.get_width(), ui_image.get_height()), 2)
        radian = 45 * 0.0174532925  # top left
        start = (
            image.get_width() / 3 * math.cos(radian),
            image.get_width() / 3 * math.sin(radian))  # draw line from 45 degree in circle
        radian = 225 * 0.0174532925  # bottom right
        end = (image.get_width() * -math.cos(radian), image.get_width() * -math.sin(radian))  # draw line to 225 degree in circle
        pygame.draw.line(image, (0, 0, 0), start, end, 2)

    selected_image = pygame.Surface((ui_image.get_width(), ui_image.get_height()), pygame.SRCALPHA)
    pygame.draw.circle(selected_image, (255, 255, 255, 150), (ui_image.get_width() / 2, ui_image.get_height() / 2), ui_image.get_width() / 2)
    pygame.draw.circle(selected_image, (0, 0, 0, 255), (ui_image.get_width() / 2, ui_image.get_height() / 2), ui_image.get_width() / 2, 1)
    selected_image_original = selected_image.copy()
    selected_image_original2 = selected_image.copy()
    selected_image_rect = selected_image.get_rect(topleft=(0, 0))

    far_image = image.copy()
    pygame.draw.circle(far_image, (0, 0, 0), (far_image.get_width() / 2, far_image.get_height() / 2),
                       far_image.get_width() / 2, 4)
    far_selected_image = selected_image.copy()
    pygame.draw.circle(far_selected_image, (0, 0, 0), (far_selected_image.get_width() / 2, far_selected_image.get_height() / 2),
                       far_selected_image.get_width() / 2, 4)

    dim = pygame.Vector2(image.get_width() * 1 / self.max_zoom, image.get_height() * 1 / self.max_zoom)
    far_image = pygame.transform.scale(far_image, (int(dim[0]), int(dim[1])))
    far_selected_image = pygame.transform.scale(far_selected_image, (int(dim[0]), int(dim[1])))

    block = ui_image.copy()  # image shown in inspect ui as square instead of circle
    # ^ End subunit base sprite

    # v health and stamina related
    health_image_list = [self.unit_ui_images["ui_health_circle_100.png"], self.unit_ui_images["ui_health_circle_75.png"],
                         self.unit_ui_images["ui_health_circle_50.png"], self.unit_ui_images["ui_health_circle_25.png"],
                         self.unit_ui_images["ui_health_circle_0.png"]]
    stamina_image_list = [self.unit_ui_images["ui_stamina_circle_100.png"], self.unit_ui_images["ui_stamina_circle_75.png"],
                          self.unit_ui_images["ui_stamina_circle_50.png"], self.unit_ui_images["ui_stamina_circle_25.png"],
                          self.unit_ui_images["ui_stamina_circle_0.png"]]

    health_image = self.unit_ui_images["ui_health_circle_100.png"]
    health_image_rect = health_image.get_rect(center=image.get_rect().center)  # for battle sprite
    health_block_rect = health_image.get_rect(center=block.get_rect().center)  # for ui sprite
    image.blit(health_image, health_image_rect)
    block.blit(health_image, health_block_rect)

    stamina_image = self.unit_ui_images["ui_stamina_circle_100.png"]
    stamina_image_rect = stamina_image.get_rect(center=image.get_rect().center)  # for battle sprite
    stamina_block_rect = stamina_image.get_rect(center=block.get_rect().center)  # for ui sprite
    image.blit(stamina_image, stamina_image_rect)
    block.blit(stamina_image, stamina_block_rect)
    # ^ End health and stamina

    # v weapon class icon in middle circle or leader
    image1 = self.weapon_data.images[self.weapon_data.weapon_list[self.primary_main_weapon[0]]["ImageID"]]  # image on subunit sprite
    if type(self.troop_id) != int and "h" in self.troop_id:
        try:
            image1 = self.leader_data.images[self.troop_id.replace("h", "") + ".png"].copy()
        except KeyError:
            image1 = self.leader_data.images["9999999.png"].copy()
        image1 = pygame.transform.scale(image1.copy(), stamina_image.get_size())
    image_rect = image1.get_rect(center=image.get_rect().center)
    image.blit(image1, image_rect)

    image_rect = image1.get_rect(center=block.get_rect().center)
    block.blit(image1, image_rect)
    block_original = block.copy()

    corner_image_rect = self.unit_ui_images["ui_squad_combat.png"].get_rect(
        center=block.get_rect().center)  # red corner when take melee_dmg shown in image block
    # ^ End weapon icon

    inspect_image_original = image.copy()  # original for rotate
    inspect_image_original2 = image.copy()  # original2 for saving original not clicked
    inspect_image_original3 = image.copy()  # original3 for saving original zoom level

    return {"image": image, "original": inspect_image_original, "original2": inspect_image_original2, "original3": inspect_image_original3,
            "block": block, "block_original": block_original, "selected": selected_image, "selected_rect": selected_image_rect,
            "selected_original": selected_image_original, "selected_original2": selected_image_original2,
            "far": far_image, "far_selected": far_selected_image, "health_rect": health_image_rect, "health_block_rect": health_block_rect,
            "stamina_rect": stamina_image_rect, "stamina_block_rect": stamina_block_rect,
            "corner_rect": corner_image_rect, "health_list": health_image_list, "stamina_list": stamina_image_list}


def grab_face_part(pool, race, side, part, part_check, part_default):
    """For creating body part like eye or mouth in animation that accept any part (1) so use default instead"""
    if part_check == 1:  # any part
        surface = pool[race][side][part][part_default].copy()
    else:
        surface = pool[race][side][part][part_check].copy()
    return surface


def generate_head(p, animation_part_list, body_part_list, sprite_list, pool, armour_pool, armour, hair_colour_list, skin_colour_list):
    apply_colour = animation.apply_colour

    head_sprite_surface = None
    try:
        head_race = body_part_list[0]
        head_side = body_part_list[1]
        head = pool[head_race][head_side]["head"][body_part_list[2]].copy()
        head_sprite_surface = pygame.Surface((head.get_width(), head.get_height()), pygame.SRCALPHA)
        head_rect = head.get_rect(midtop=(head_sprite_surface.get_width() / 2, 0))
        head_sprite_surface.blit(head, head_rect)
        face = [pool[head_race][head_side]["eyebrow"][sprite_list[p + "_eyebrow"][0]].copy(),
                grab_face_part(pool, head_race, head_side, "eye", animation_part_list[p + "_eye"], sprite_list[p + "_eye"][0]),
                pool[head_race][head_side]["beard"][sprite_list[p + "_beard"][0]].copy(),
                grab_face_part(pool, head_race, head_side, "mouth", animation_part_list[p + "_mouth"], sprite_list[p + "_mouth"])]

    # if skin != "white":
    #     face[0] = self.apply_colour(face[0], skin_colour)

        face[0] = apply_colour(face[0], sprite_list[p + "_hair"][1], hair_colour_list)
        face[1] = apply_colour(face[1], sprite_list[p + "_eye"][1], hair_colour_list)
        face[2] = apply_colour(face[2], sprite_list[p + "_beard"][1], hair_colour_list)

        head_sprite_surface = pygame.Surface((face[0].get_width(), face[0].get_height()), pygame.SRCALPHA)
        rect = head.get_rect(center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
        head_sprite_surface.blit(head, rect)

        for index, item in enumerate(face):
            rect = item.get_rect(center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
            head_sprite_surface.blit(item, rect)
    except KeyError:  # some head direction show no face
        pass
    except TypeError:  # empty
        pass

    if sprite_list[p + "_head"] != "none":
        try:
            gear_image = armour_pool[head_race][armour][sprite_list[p + "_head"]][head_side]["helmet"][body_part_list[2]]
            rect = gear_image.get_rect(center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
            head_sprite_surface.blit(gear_image, rect)
        except KeyError:  # helmet folder not existed
            pass

    return head_sprite_surface


def generate_body(part, body_part_list, troop_sprite_list, sprite_pool, armour_sprite_pool=None, colour=None,
                  weapon=None, armour=None, colour_list=None):
    apply_colour = animation.apply_colour

    # main/body first
    sprite_image = None
    try:
        if "weapon" in part:
            weapon_part = part[:3] + "primary_" + part[3:]  # primary set
            if weapon_part == 1:
                weapon_part = part[:3] + "secondary_" + part[3:]  # secondary set
            part_name = weapon[1][0]  # main weapon
            if "sub" in part:
                part_name = weapon[1][1]  # sub weapon
            if part_name is not None and part_name != "Unarmed":
                sprite_image = sprite_pool[part_name][troop_sprite_list[weapon_part]][body_part_list[0]][body_part_list[1]].copy()
        else:
            new_part_name = part
            part_name = part
            if "p1_" in part or "p2_" in part:
                part_name = part[3:]  # remove p1_ or p2_ to get part name
                new_part_name = part_name
            if "special" in part:
                part_name = "special"
            if "r_" in part_name[0:2] or "l_" in part_name[0:2]:
                new_part_name = part_name[2:]  # remove side
            sprite_image = sprite_pool[body_part_list[0]][body_part_list[1]][new_part_name][body_part_list[2]].copy()

        if colour is not None:  # apply skin colour, maybe add for armour colour later
            sprite_image = apply_colour(sprite_image, colour, colour_list)

        # add armour if there is one
        if armour is not None and armour != "None":
            part_name = part
            if "p1_" in part or "p2_" in part:
                part_name = part[3:]  # remove p1_ or p2_ to get part name
            gear_image = armour_sprite_pool[body_part_list[0]][armour][troop_sprite_list[part]][body_part_list[1]][part_name][body_part_list[2]]
            new_sprite_image = pygame.Surface(gear_image.get_size(), pygame.SRCALPHA)  # create sprite based on armour size since it can be larger than body part
            rect = sprite_image.get_rect(center=(new_sprite_image.get_width() / 2, new_sprite_image.get_height() / 2))
            new_sprite_image.blit(sprite_image, rect)
            rect = gear_image.get_rect(center=(new_sprite_image.get_width() / 2, new_sprite_image.get_height() / 2))
            new_sprite_image.blit(gear_image, rect)
            sprite_image = new_sprite_image
    except KeyError:  # sprite simply not existed
        pass

    return sprite_image


def make_sprite(animation_name, size, animation_part_list, troop_sprite_list, body_sprite_pool, weapon_sprite_pool, armour_sprite_pool,
                effect_sprite_pool, animation_property, weapon_joint_list, weapon, armour, hair_colour_list, skin_colour_list, genre_sprite_size,
                screen_scale):
    apply_colour = animation.apply_colour

    frame_property = animation_part_list["frame_property"].copy()
    animation_property = animation_property.copy()
    check_prop = frame_property + animation_property

    surface = pygame.Surface((default_sprite_size[0] * size, default_sprite_size[1] * size), pygame.SRCALPHA)  # default size will scale down later

    except_list = ["eye", "mouth", "size", "property"]
    pose_layer_list = {k: v[7] for k, v in animation_part_list.items() if v != [0] and v != "" and
                       any(ext in k for ext in except_list) is False and "weapon" not in k}  # layer list
    pose_layer_list.update({k: v[6] for k, v in animation_part_list.items() if v != [0] and v != "" and "weapon" in k})
    pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))
    for index, layer in enumerate(pose_layer_list):
        part = animation_part_list[layer]
        new_part = part.copy()
        if "p1_" in layer:
            this_armour = armour[0]
        elif "p2_" in layer:
            this_armour = armour[1]
        if "head" in layer:
            image_part = generate_head(layer[:2], animation_part_list, part[0:3], troop_sprite_list, body_sprite_pool, armour_sprite_pool,
                                       this_armour, hair_colour_list, skin_colour_list)
        elif "weapon" in layer:
            new_part.insert(2, "Dummy")  # insert dummy value for weapon list so can use indexing similar as other part
            image_part = generate_body(layer, part[0:2], troop_sprite_list, weapon_sprite_pool, weapon=weapon)
        elif "effect" in layer and "dmg" not in layer:
            image_part = generate_body(layer, part[0:3], troop_sprite_list, effect_sprite_pool)
        else:  # other body part
            image_part = generate_body(layer, part[0:3], troop_sprite_list, body_sprite_pool, armour_sprite_pool=armour_sprite_pool,
                                       colour_list=skin_colour_list, armour=this_armour)
        if image_part is not None:  # skip for empty image
            target = (new_part[3], new_part[4])
            angle = new_part[5]
            flip = new_part[6]
            scale = new_part[8]

            part_rotated = image_part.copy()
            if scale != 1:
                part_rotated = pygame.transform.scale(part_rotated, (part_rotated.get_width() * scale,
                                                                     part_rotated.get_height() * scale))
            if flip != 0:
                if flip == 1:
                    part_rotated = pygame.transform.flip(part_rotated, True, False)
                elif flip == 2:
                    part_rotated = pygame.transform.flip(part_rotated, False, True)
                elif flip == 3:
                    part_rotated = pygame.transform.flip(part_rotated, True, True)
            if angle != 0:
                part_rotated = pygame.transform.rotate(part_rotated, angle)  # rotate part sprite

            new_target = target

            if "weapon" in layer:  # only weapon use joint to calculate position
                part_name = weapon[1][0]  # main weapon
                if "sub" in layer:
                    part_name = weapon[1][1]  # sub weapon
                center = pygame.Vector2(image_part.get_width() / 2, image_part.get_height() / 2)
                use_center = False
                if ("p1_main" in layer and "p1_fix_main_weapon" not in check_prop) or \
                    ("p2_main" in layer and "p2_fix_main_weapon" not in check_prop) or \
                    ("p1_sub" in layer and "p1_fix_sub_weapon" not in check_prop) or \
                    ("p2_sub" in layer and "p2_fix_sub_weapon" not in check_prop):

                    target = (animation_part_list["p1_r_hand"][3], animation_part_list["p1_r_hand"][4])
                    if "p2_main" in layer:  # change p2 main weapon pos to p2 right hand
                        target = (animation_part_list["p2_r_hand"][3], animation_part_list["p2_r_hand"][4])
                    elif "sub" in layer and ("2hand" in animation_name or "2pole" in animation_name):  # has sub weapon but main is 2 hands weapon
                        use_center = True  # use pos according to data instead of hand, usually attach to the back of body part. and use center not joint
                    else:
                        if "p1_sub" in layer:
                            target = (animation_part_list["p1_l_hand"][3], animation_part_list["p1_l_hand"][4])
                        elif "p2_sub" in layer:
                            target = (animation_part_list["p2_l_hand"][3], animation_part_list["p2_l_hand"][4])
                    new_target = target

                if weapon_joint_list[new_part[0]][part_name] != "center" and use_center is False:  # use weapon joint pos and hand pos for weapon position blit
                    main_joint_pos = [weapon_joint_list[new_part[0]][part_name][0], weapon_joint_list[new_part[0]][part_name][1]]

                    # change pos from flip
                    if flip in (1, 3):  # horizontal flip
                        hori_diff = image_part.get_width() - main_joint_pos[0]
                        main_joint_pos = (hori_diff, main_joint_pos[1])
                    if flip >= 2:  # vertical flip
                        vert_diff = image_part.get_height() - main_joint_pos[1]
                        main_joint_pos = (main_joint_pos[0], vert_diff)

                    pos_different = center - main_joint_pos  # find distance between image center and connect point main_joint_pos
                    new_target = new_target + pos_different
                    if angle != 0:
                        radians_angle = math.radians(360 - angle)
                        if angle < 0:
                            radians_angle = math.radians(-angle)
                        new_target = rotation_xy(target, new_target, radians_angle)  # find new center point with rotation

            rect = part_rotated.get_rect(center=new_target)
            surface.blit(part_rotated, rect)

    for prop in check_prop:
        if "effect" in prop:
            if "grey" in prop:  # not work with just convert L for some reason
                width, height = surface.get_size()
                for x in range(width):
                    for y in range(height):
                        red, green, blue, alpha = surface.get_at((x, y))
                        average = (red + green + blue) // 3
                        gs_color = (average, average, average, alpha)
                        surface.set_at((x, y), gs_color)
            data = pygame.image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
            surface = Image.frombytes("RGBA", surface.get_size(), data)  # use PIL to get image data
            alpha = surface.split()[-1]  # save alpha
            if "blur" in prop:
                surface = surface.filter(
                    ImageFilter.GaussianBlur(radius=float(prop[prop.rfind("_") + 1:])))  # blur Image (or apply other filter in future)
            if "contrast" in prop:
                enhancer = ImageEnhance.Contrast(surface)
                surface = enhancer.enhance(float(prop[prop.rfind("_") + 1:]))
            if "brightness" in prop:
                enhancer = ImageEnhance.Brightness(surface)
                surface = enhancer.enhance(float(prop[prop.rfind("_") + 1:]))
            if "fade" in prop:
                empty = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
                empty.fill((255, 255, 255, 255))
                empty = pygame.image.tostring(empty, "RGBA")  # convert image to string data for filtering effect
                empty = Image.frombytes("RGBA", surface.get_size(), empty)  # use PIL to get image data
                surface = Image.blend(surface, empty, alpha=float(prop[prop.rfind("_") + 1:]) / 10)
            surface.putalpha(alpha)  # put back alpha
            surface = surface.tobytes()
            surface = pygame.image.fromstring(surface, surface.get_size(),
                                              "RGBA")  # convert image back to a pygame surface
            if "colour" in prop:
                colour = prop[prop.rfind("_") + 1:]
                colour = [int(this_colour) for this_colour in colour.split(".")]
                surface = apply_colour(surface, colour)

            if prop in frame_property:
                frame_property.remove(prop)
            if prop in animation_property:
                animation_property.remove(prop)

    # change to whatever genre's specific size
    surface = pygame.transform.scale(surface, (genre_sprite_size[0] * size * screen_scale[0], genre_sprite_size[1] * size * screen_scale[1]))

    return {"sprite": surface, "animation_property": tuple(animation_property), "frame_property": tuple(frame_property)}
