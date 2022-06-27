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

    def __init__(self, leader_id, subunit_position, role, unit, leader_data):
        self._layer = 15
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.morale = 100
        stat = leader_data.leader_list[leader_id]
        self.leader_id = leader_id  # leader_id is only used as reference to the data
        self.name = stat["Name"]
        self.health = stat["Health"]
        self.authority = stat["Authority"]
        self.melee_command = stat["Melee Command"]
        self.range_command = stat["Range Command"]
        self.cav_command = stat["Cavalry Command"]
        self.combat = stat["Combat"]
        self.social = leader_data.leader_class[stat["Social Class"]]
        self.description = stat["Description"]

        self.subunit_pos = int(subunit_position)  # Squad position is the index of subunit in subunit sprite loop
        # self.trait = stat
        self.skill = stat["Skill"]

        self.state = 0  # 0 = alive, 96 = retreated, 97 = captured, 98 = missing, 99 = wound, 100 = dead

        if self.name == "None":  # None leader is considered dead by default, function the same way as dead one
            self.health = 0
            self.state = 100  # no leader is same as dead so no need to update

        self.unit = unit
        self.team = self.unit.team
        self.subunit = None  # get assigned in start_set
        # self.mana = stat["Mana"]
        self.role = role  # role in the unit (i.e. general (0) or sub-general (1, 2) or advisor (3))
        self.image_position = self.leader_pos[self.role]  # image position based on role in command ui

        try:  # Put leader image into leader slot
            image_name = str(leader_id) + ".png"
            self.full_image = leader_data.images[image_name].copy()
        except KeyError:  # Use Unknown leader image if there is none in list
            self.full_image = leader_data.images["9999999.png"].copy()
            font = pygame.font.SysFont("timesnewroman", 50)
            text_image = font.render(str(self.leader_id), True, pygame.Color("white"))
            text_rect = text_image.get_rect(center=(self.full_image.get_width() / 2, self.full_image.get_height() / 1.3))
            self.full_image.blit(text_image, text_rect)

        self.image = pygame.transform.scale(self.full_image.copy(), (75 * self.battle.screen_scale[0], 75 * self.battle.screen_scale[1]))
        self.rect = self.image.get_rect(midbottom=self.image_position)
        self.image_original = self.image.copy()

        self.bad_morale = (20, 30)  # other position morale lost
        self.commander = False  # army commander
        self.original_commander = False  # the first army commander at the start of battle

        self.leader_skill = self.skill.copy()
        self.skill = {value: leader_data.skill_list[value] for value in self.skill if value in leader_data.skill_list}
        if self.role == 0:
            self.bad_morale = (30, 50)  # general morale lost when destroyed
            if self.unit.commander:
                self.commander = True
                self.original_commander = True
                for key, value in self.skill:  # replace leader skill with commander skill version
                    for key2, value2 in leader_data.commander_skill_list.items():
                        if key in value2["Replace"]:
                            self.skill[key] = key2

    def start_set(self):
        self.subunit = self.unit.subunit_list[self.subunit_pos]  # setup subunit that leader belong
        self.subunit.leader = self  # put in leader to subunit with the set pos
        if self.role == 0:  # unit leader
            self.unit.leader_subunit = self.subunit  # TODO add this to when change leader or leader move ot other subunit
            # self.unit.leader_subunit - self.unit.base_pos
            self.subunit.unit_leader = True

            squad_penal = int(
                (self.subunit_pos / len(self.unit.subunit_id_array[0])) * 10)  # Authority get reduced the further leader stay in the back line
            self.authority = self.authority - ((self.authority * squad_penal / 100) / 2)

    def update(self):
        if self.state not in (96, 97, 98, 99, 100):
            if self.health <= 0:  # health reach 0, destroyed. may implement wound state chance later
                self.health = 0
                self.state = 100
                # if random.randint(0,1) == 1: self.state = 99 ## chance to become wound instead when hp reach 0
                self.gone()

