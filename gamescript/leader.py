import pygame
import pygame.freetype

from gamescript.common import utility


class Leader(pygame.sprite.Sprite):
    empty_method = utility.empty_method

    battle = None
    leader_pos = None

    # Import from *genre*.leader
    gone = empty_method
    leader_role_change = empty_method

    def __init__(self, leader_id, subunit_position, role, unit, leader_data, layer=15):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.morale = 100
        self.leader_data = leader_data
        stat = self.leader_data.leader_list[leader_id]
        lore = self.leader_data.leader_lore[leader_id]
        self.leader_id = leader_id  # leader_id is only used as reference to the data
        self.name = lore[0]

        self.strength = stat["Strength"]
        self.dexterity = stat["Dexterity"]
        self.agility = stat["Agility"]
        self.constitution = stat["Constitution"]
        self.intelligence = stat["Intelligence"]
        self.wisdom = stat["Wisdom"]
        self.authority = stat["Charisma"]
        self.melee_command = stat["Melee Speciality"]
        self.range_command = stat["Range Speciality"]
        self.cav_command = stat["Cavalry Speciality"]
        self.health = ((self.strength * 0.2) + (self.constitution * 0.8)) * 10
        self.combat = ((self.strength * 0.5) + (self.dexterity * 0.5) + (self.agility * 0.5) +
                       (self.wisdom * 0.5))
        self.social = self.leader_data.leader_class[stat["Social Class"]]
        self.formation = ["Cluster"] + stat["Formation"]
        self.description = lore[1]

        self.subunit_pos = int(subunit_position)  # Squad position is the index of subunit in subunit sprite loop
        # self.trait = stat
        self.skill = stat["Skill"]

        self.state = 0  # 0 = alive, 96 = retreated, 97 = captured, 98 = missing, 99 = wound, 100 = dead

        if self.name == "None":  # None leader is considered dead by default, function the same way as dead one
            self.health = 0
            self.state = 100  # no leader is same as dead so no need to update

        self.unit = unit
        self.subunit = None  # get assigned in enter_battle
        # self.mana = stat["Mana"]
        self.role = role  # role in the unit (i.e. general (0) or sub-general (1, 2) or advisor (3))

        self.full_image, self.image = self.create_portrait()

        self.image_position = self.leader_pos[self.role]  # image position based on role in command ui
        self.rect = self.image.get_rect(midbottom=self.image_position)
        self.image_original = self.image.copy()

        self.bad_morale = (20, 30)  # other position morale lost
        self.commander = False  # army commander
        self.original_commander = False  # the first army commander at the start of battle

        self.leader_skill = self.skill.copy()  # save list of leader skill
        self.skill = {value: self.leader_data.skill_list[value] for
                      value in self.skill if value in self.leader_data.skill_list}
        self.assign_commander()

    def create_portrait(self):
        try:  # Put leader image into leader slot
            image_name = str(self.leader_id)
            full_image = self.leader_data.images[image_name].copy()
        except KeyError:  # Use Unknown leader image if there is none in list
            full_image = self.leader_data.images["9999999"].copy()
            font = pygame.font.SysFont("timesnewroman", 50)
            text_image = font.render(str(self.leader_id), True, pygame.Color("white"))
            text_rect = text_image.get_rect(center=(full_image.get_width() / 2, full_image.get_height() / 1.3))
            full_image.blit(text_image, text_rect)
        image = pygame.transform.scale(full_image, (75 * self.battle.screen_scale[0], 75 * self.battle.screen_scale[1]))
        return full_image, image

    def assign_commander(self):
        if self.role == 0:
            self.bad_morale = (30, 50)  # general morale lost when destroyed
            if self.unit is not None and self.unit.commander:
                self.commander = True
                self.original_commander = True
                for key, value in self.skill.items():  # replace leader skill with commander skill version
                    for key2, value2 in self.leader_data.commander_skill_list.items():
                        if key in value2["Replace"]:
                            old_action = self.skill[key]["Action"]
                            self.skill[key] = value2
                            self.skill[key]["Action"] = old_action  # get action from normal leader skill


    def enter_battle(self):
        if self.name != "None":
            self.subunit = self.unit.subunit_object_array.flat[self.subunit_pos]  # setup subunit that leader belong
            self.subunit.leader = self  # put in leader to subunit with the set pos
            if self.role == 0:  # unit leader
                self.unit.leader_subunit = self.subunit
                # self.unit.leader_subunit - self.unit.base_pos
                self.subunit.unit_leader = True

                squad_penal = int(
                    (self.subunit_pos / len(self.unit.subunit_id_array[
                                                0])) * 10)  # Authority get reduced the further leader stay in the back line
                self.authority = self.authority - ((self.authority * squad_penal / 100) / 2)

    def update(self):
        if self.state not in (96, 97, 98, 99, 100):
            if self.health <= 0:  # health reach 0, destroyed. may implement wound state chance later
                self.health = 0
                self.state = 100
                # if random.randint(0,1) == 1: self.state = 99 ## chance to become wound instead when hp reach 0
                self.gone()

    def change_preview_leader(self, leader_id):
        """Change only stat that will be shown for preview leader"""
        self.leader_id = leader_id  # leader_id is only used as reference to the leader data

        stat = self.leader_data.leader_list[self.leader_id]

        self.name = stat["Name"]
        self.authority = stat["Charisma"]
        self.social = self.leader_data.leader_class[stat["Social Class"]]

        self.full_image, self.image = self.create_portrait()
        self.image_original = self.image.copy()

        self.image_position = self.leader_pos[self.role]  # image position based on role in command ui
        self.rect = self.image.get_rect(midbottom=self.image_position)

        self.commander = False
        self.original_commander = False

        # self.__init__(leader_id, self.subunit_pos, self.role, None, self.leader_data, layer=11)

    def change_editor_subunit(self, subunit):
        self.subunit = subunit
        if subunit is None:
            self.subunit_pos = 0
        else:
            self.subunit_pos = subunit.game_id
