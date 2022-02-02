import pygame
import pygame.freetype


def change_leader_genre(genre):
    if genre == "tactical":
        from gamescript.tactical.leader import engage
    elif genre == "arcade":
        from gamescript.arcade.leader import engage

    Leader.pos_change_stat = engage.pos_change_stat
    Leader.gone = engage.gone


class Leader(pygame.sprite.Sprite):
    battle = None

    # method that change based on genre
    pos_change_stat = None
    gone = None

    def __init__(self, leader_id, position, army_position, unit, leader_stat):
        self._layer = 15
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.morale = 100
        stat = leader_stat.leader_list[leader_id]
        self.leader_id = leader_id  # Different from self id, leader_id is only used as reference to the data
        self.name = stat["Name"]
        self.health = stat["Health"]
        self.authority = stat["Authority"]
        self.melee_command = stat["Melee Command"]
        self.range_command = stat["Range Command"]
        self.cav_command = stat["Cavalry Command"]
        self.combat = stat["Combat"] * 2
        self.social = leader_stat.leader_class[stat["Social Class"]]
        self.description = stat["Description"]

        self.player = False  # for arcade mode, indicate player character

        self.subunit_pos = position  # Squad position is the index of subunit in subunit sprite loop
        # self.trait = stat
        # self.skill = stat
        self.state = 0  # 0 = alive, 96 = retreated, 97 = captured, 98 = missing, 99 = wound, 100 = dead

        if self.name == "None":  # None leader is considered dead by default, function the same way as dead one
            self.health = 0
            self.state = 100  # no leader is same as dead so no need to update

        self.unit = unit
        # self.mana = stat["Mana"]
        self.army_position = army_position  # position in the unit (i.e. general (0) or sub-general (1, 2) or advisor (3))
        self.base_image_position = [(134, 185), (80, 235), (190, 235), (134, 283)]  # leader image position in command ui
        self.image_position = self.base_image_position[self.army_position]  # image position based on army_position

        try:  # Put leader image into leader slot
            image_name = str(leader_id) + ".png"
            self.full_image = leader_stat.images[image_name].copy()
        except:  # Use Unknown leader image if there is none in list
            self.full_image = leader_stat.images["9999999.png"].copy()
            font = pygame.font.SysFont("timesnewroman", 300)
            text_image = font.render(str(self.leader_id), True, pygame.Color("white"))
            text_rect = text_image.get_rect(center=(self.full_image.get_width() / 2, self.full_image.get_height() / 1.3))
            self.full_image.blit(text_image, text_rect)

        self.image = pygame.transform.scale(self.full_image, (50 * self.battle.screen_scale[0], 50 * self.battle.screen_scale[1]))
        self.rect = self.image.get_rect(center=self.image_position)
        self.image_original = self.image.copy()

        self.bad_morale = (20, 30)  # other position morale lost
        self.commander = False  # army commander
        self.original_commander = False  # the first army commander at the start of battle

    def start_set(self):
        row = int(self.subunit_pos / 8)
        column = self.subunit_pos - (row * 8)
        self.subunit = self.unit.subunit_sprite[self.subunit_pos]  # setup subunit that leader belong
        self.subunit.leader = self  # put in leader to subunit with the set pos
        if self.army_position == 0:  # unit leader
            self.unit.leader_subunit = self.subunit  # TODO add this to when change leader or start_set leader move ot other subunit
            # self.unit.leader_subunit - self.unit.base_pos
            self.subunit.unit_leader = True

            squad_penal = int(
                (self.subunit_pos / len(self.unit.subunit_list[0])) * 10)  # Authority get reduced the further leader stay in the back line
            self.authority = self.authority - ((self.authority * squad_penal / 100) / 2)
            self.bad_morale = (30, 50)  # start_set general morale lost when destroyed
            if self.unit.commander:
                self.commander = True
                self.original_commander = True

    def update(self):
        if self.state not in (96, 97, 98, 99, 100):
            if self.health <= 0:  # health reach 0, destroyed. may implement wound state chance later
                self.health = 0
                self.state = 100
                # if random.randint(0,1) == 1: self.state = 99 ## chance to become wound instead when hp reach 0
                self.gone()

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.unit
