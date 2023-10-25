import os.path
import sys
import csv
import configparser

import pygame
import screeninfo

from pathlib import Path

from engine.battlemap import battlemap
from engine.game.game import Game
from engine.data.datalocalisation import Localisation
from engine.weather import weather
from engine.camera import camera
from engine.effect import effect
from engine.data import datasprite, datamap
from engine.uibattle import uibattle


from engine.utils.utility import csv_read, load_images, stat_convert
from engine.battle.spawn_weather_matter import spawn_weather_matter
from engine.game.setup.make_faction_troop_leader_data import make_faction_troop_leader_data
from engine.game.create_unit_sprite_pool import create_unit_sprite_pool

team_colour = Game.team_colour

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

rotation_list = (90, -90)
rotation_name = ("l_side", "r_side")
rotation_dict = {key: rotation_name[index] for index, key in enumerate(rotation_list)}


class DummyTeam:
    def __init__(self, team):
        self.team = team


dummy_troop = [DummyTeam(team) for team in team_colour]


class TroopModel(pygame.sprite.Sprite):
    hitbox_image_list = {}

    def __init__(self, image, pos, leader, team, troop_size):
        self.pos = (pos[0] * 5, pos[1] * 5)
        layer = int(self.pos[0] + (self.pos[1] * 10))
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image.copy()
        self.base_image = image.copy()
        self.team = team

        # Create hitbox sprite
        self.hitbox_front_distance = troop_size
        hitbox_size = (troop_size * 10, troop_size * 10)
        if self.team not in self.hitbox_image_list:
            self.hitbox_image_list[self.team] = {"troop": {}, "leader": {}}
        if leader:  # leader unit
            if hitbox_size not in self.hitbox_image_list[self.team]["leader"]:
                self.hitbox_image = pygame.Surface(hitbox_size, pygame.SRCALPHA)
                pygame.draw.circle(self.hitbox_image, (team_colour[self.team][0], team_colour[self.team][1],
                                                       team_colour[self.team][2], 150),
                                   (self.hitbox_image.get_width() / 2, self.hitbox_image.get_height() / 2),
                                   self.hitbox_image.get_width() / 2)

                pygame.draw.circle(self.hitbox_image,
                                   (220, 120, 20, 150),
                                   (self.hitbox_image.get_width() / 2, self.hitbox_image.get_height() / 2),
                                   self.hitbox_image.get_width() / 2.4)
            else:
                self.hitbox_image = self.hitbox_image_list[self.team]["leader"][hitbox_size]
        else:  # troop unit
            if hitbox_size not in self.hitbox_image_list[self.team]["troop"]:
                self.hitbox_image = pygame.Surface(hitbox_size,
                                                   pygame.SRCALPHA)
                pygame.draw.circle(self.hitbox_image, (team_colour[self.team][0], team_colour[self.team][1],
                                                       team_colour[self.team][2], 150),
                                   (self.hitbox_image.get_width() / 2, self.hitbox_image.get_height() / 2),
                                   self.hitbox_image.get_width() / 2)

                pygame.draw.circle(self.hitbox_image,
                                   (100, 100, 100, 150),
                                   (self.hitbox_image.get_width() / 2, self.hitbox_image.get_height() / 2),
                                   self.hitbox_image.get_width() / 2.4)
            else:
                self.hitbox_image = self.hitbox_image_list[self.team]["troop"][hitbox_size]

        self.rect = self.image.get_rect(center=self.pos)


class Studio(Game):
    spawn_weather_matter = spawn_weather_matter
    create_unit_sprite_pool = create_unit_sprite_pool

    def __init__(self, photo_size, map_name, battle_data_name, module, art_style, day_time, weather_event):
        pygame.init()  # Initialize pygame
        self.screen_rect = pygame.Rect(0, 0, photo_size[0], photo_size[1])
        camera.Camera.screen_rect = self.screen_rect
        self.screen_scale = (self.screen_rect.width / 1920, self.screen_rect.height / 1080)
        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, 0, 32)
        self.screen = pygame.display.set_mode(self.screen_rect.size, 0 | pygame.RESIZABLE, self.best_depth)

        self.main_dir = main_dir
        self.data_dir = data_dir

        part_folder = Path(os.path.join(self.data_dir, "module"))
        self.module_list = {os.path.split(
            os.sep.join(os.path.normpath(x).split(os.sep)))[-1]: x for x
            in part_folder.iterdir() if x.is_dir()}  # get module list
        if "tutorial" in self.module_list:
            self.module_list.pop("tutorial")  # get tutorial module from list
        self.module_folder = self.module_list[module]

        self.module_dir = os.path.join(data_dir, "module", self.module_folder)

        Game.main_dir = main_dir
        Game.data_dir = data_dir
        Game.module_dir = self.module_dir
        Game.screen_scale = self.screen_scale
        Game.language = "en"
        self.localisation = Localisation()
        Game.localisation = self.localisation
        Game.art_style_dir = os.path.join(self.module_dir, "animation", art_style)
        Game.font_dir = os.path.join(data_dir, "font")
        Game.ui_font = csv_read(self.module_dir, "ui_font.csv", ("ui",), header_key=True)
        for item in Game.ui_font:  # add ttf file extension for font data reading.
            Game.ui_font[item] = os.path.join(Game.font_dir, Game.ui_font[item]["Font"] + ".ttf")

        part_folder = Path(os.path.join(self.module_dir, "animation"))
        Game.art_style_list = {os.path.split(
            os.sep.join(os.path.normpath(x).split(os.sep)))[-1]: x for x
            in part_folder.iterdir() if x.is_dir()}  # get art style list
        config.read_file(open(os.path.join(self.art_style_dir, "stat.ini")))  # read config file

        self.design_sprite_size = (int(config["DEFAULT"]["design_sprite_width"]),
                                   int(config["DEFAULT"]["design_sprite_height"]))

        self.troop_data, self.leader_data, self.faction_data = make_faction_troop_leader_data(self.module_dir,
                                                                                              self.screen_scale)
        self.battle_map_data = datamap.BattleMapData()

        self.battle_base_map = battlemap.BaseMap()  # create base terrain map
        self.battle_feature_map = battlemap.FeatureMap()  # create terrain feature map
        self.battle_height_map = battlemap.HeightMap()  # create height map
        self.battle_map = battlemap.FinalMap(self.battle_height_map)

        self.battle_base_map.terrain_list = self.battle_map_data.terrain_list
        self.battle_base_map.terrain_colour = self.battle_map_data.terrain_colour
        self.battle_feature_map.feature_list = self.battle_map_data.feature_list
        self.battle_feature_map.feature_colour = self.battle_map_data.feature_colour
        self.battle_feature_map.feature_mod = self.battle_map_data.feature_mod
        self.battle_campaign = self.battle_map_data.battle_campaign  # for reference to preset campaign
        self.preset_map_data = self.battle_map_data.preset_map_data

        self.battle_map.battle_map_colour = self.battle_map_data.battle_map_colour

        self.map_move_array = []
        self.map_def_array = []

        images = load_images(data_dir, subfolder=("module", self.module_folder, "map", "preset",
                                                  self.battle_campaign[map_name], map_name))
        if not images:
            images = load_images(data_dir, subfolder=("module", self.module_folder, "map", "custom", map_name))

        self.battle_base_map.draw_image(images["base"])
        self.battle_feature_map.draw_image(images["feature"])
        self.battle_height_map.draw_image(images["height"])

        self.max_camera = (len(self.battle_base_map.map_array[0]), len(self.battle_base_map.map_array))

        if "place_name" in images:  # place_name map layer is optional, if not existed in folder then assign None
            place_name_map = images["place_name"]
        else:
            place_name_map = None
        self.battle_map.draw_image(self.battle_base_map, self.battle_feature_map, place_name_map, {})

        self.weather_updater = pygame.sprite.Group()  # updater for weather objects
        self.weather_matter = pygame.sprite.Group()  # sprite of weather effect group such as rain sprite
        self.weather_effect = pygame.sprite.Group()  # sprite of special weather effect group such as fog that cover whole screen

        self.center_screen = [self.screen_rect.width / 2, self.screen_rect.height / 2]  # center position of the screen
        self.true_camera_pos = pygame.Vector2(500, 500)  # camera pos on map
        self.camera_pos = pygame.Vector2(self.true_camera_pos[0] * self.screen_scale[0],
                                  self.true_camera_pos[1] * self.screen_scale[1]) * 5  # Camera pos with screen scale

        self.camera_topleft_corner = (self.camera_pos[0] - self.center_screen[0],
                                      self.camera_pos[1] - self.center_screen[
                                          1])  # calculate top left corner of camera position

        self.camera = camera.Camera(self.camera_pos, self.screen_rect)
        self.ground_camera = pygame.sprite.LayeredUpdates()  # layer drawer camera
        self.ground_camera.add(self.battle_map)
        self.sky_camera = pygame.sprite.LayeredUpdates()  # layer drawer camera
        self.troop_model = pygame.sprite.Group()

        TroopModel.containers = self.troop_model
        weather.MatterSprite.containers = self.weather_matter, self.sky_camera, self.weather_updater
        weather.SpecialWeatherEffect.containers = self.weather_effect, self.sky_camera, self.weather_updater
        effect.Effect.containers = self.ground_camera
        uibattle.SpriteIndicator.containers = self.ground_camera

        battle_ui_image = load_images(self.module_dir, subfolder=("ui", "battle_ui"))

        weather.Weather.wind_compass_images = {"wind_compass": battle_ui_image["wind_compass"],
                                               "wind_arrow": battle_ui_image["wind_arrow"]}

        self.weather_matter_images = self.battle_map_data.weather_matter_images

        self.weather_screen_adjust = self.screen_rect.width / self.screen_rect.height  # for weather sprite spawn position
        self.current_weather = weather.Weather(TroopModel(pygame.Surface((0, 0)), (0, 0), 0, 0, 1), weather_event[0], weather_event[1],
                                               weather_event[2], self.battle_map_data.weather_data)

        self.battle_map.change_map_stuff("effect", self.battle_map_data.weather_effect_images[self.current_weather.name][self.current_weather.level],
                                         self.battle_map.day_effect_images[day_time])
        self.weather_spawn_timer = 0

        self.troop_animation = datasprite.TroopAnimationData([str(self.troop_data.race_list[key]["Name"]) for key in
                                                              self.troop_data.race_list], self.team_colour)
        self.unit_animation_data = self.troop_animation.unit_animation_data  # animation data pool
        self.body_sprite_pool = self.troop_animation.body_sprite_pool  # body sprite pool
        self.weapon_sprite_pool = self.troop_animation.weapon_sprite_pool  # weapon sprite pool
        self.armour_sprite_pool = self.troop_animation.armour_sprite_pool  # armour sprite pool
        self.weapon_joint_list = self.troop_animation.weapon_joint_list  # weapon joint data
        self.colour_list = self.troop_animation.colour_list  # skin colour list

        self.effect_sprite_pool = self.troop_animation.effect_sprite_pool
        self.effect_animation_pool = self.troop_animation.effect_animation_pool

        effect.Effect.effect_list = self.troop_data.effect_list

        effect.Effect.effect_sprite_pool = self.effect_sprite_pool
        effect.Effect.effect_animation_pool = self.effect_animation_pool

        self.battle_data = {}
        with open(os.path.join(main_dir, "photo-studio", module, battle_data_name + ".csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = tuple(csv.reader(edit_file, quoting=csv.QUOTE_ALL))
            header = rd[0]
            tuple_column = ["POS"]  # value in tuple only
            tuple_column = [index for index, item in enumerate(header) if item in tuple_column]
            dict_column = ["Other Data"]
            dict_column = [index for index, item in enumerate(header) if item in dict_column]
            for index, row in enumerate(rd[1:]):
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, tuple_column=tuple_column, dict_column=dict_column)
                self.battle_data[index] = {header[index]: stuff for index, stuff in enumerate(row)}
            edit_file.close()

        for stuff in self.battle_data.values():
            if stuff["Type"] == "unit":
                if "-" in stuff["ID"]:
                    is_leader = True
                    who_todo = {key: value for key, value in self.leader_data.leader_list.items() if key == stuff["ID"]}
                    troop_size = self.troop_data.race_list[self.leader_data.leader_list[stuff["ID"]]["Race"]]["Size"]
                    if self.leader_data.leader_list[stuff["ID"]]["Mount"]:
                        troop_size = self.troop_data.race_list[self.troop_data.mount_list[self.leader_data.leader_list[stuff["ID"]]["Mount"][0]]["Race"]]["Size"]
                else:
                    is_leader = False
                    who_todo = {key: value for key, value in self.troop_data.troop_list.items() if key == stuff["ID"]}
                    troop_size = self.troop_data.race_list[self.troop_data.troop_list[stuff["ID"]]["Race"]]["Size"]
                    if self.troop_data.troop_list[stuff["ID"]]["Mount"]:
                        troop_size = self.troop_data.race_list[self.troop_data.mount_list[self.troop_data.troop_list[stuff["ID"]]["Mount"][0]]["Race"]]["Size"]
                sprite_direction = rotation_dict[min(rotation_list, key=lambda x: abs(x - stuff["Angle"]))]  # find closest in list of rotation for sprite direction
                preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True, specific_preview=(stuff["Animation"],
                                                                                                                 int(stuff["Frame"]),
                                                                                                                 sprite_direction),
                                                                       max_preview_size=None)
                new_troop = TroopModel(preview_sprite_pool[stuff["ID"]]["sprite"], stuff["POS"], is_leader, int(stuff["Other Data"]["Team"]),
                                       troop_size)
                # uibattle.SpriteIndicator(new_troop.hitbox_image, new_troop, self)

            elif stuff["Type"] == "effect":
                if "Team" in stuff["Other Data"]:
                    this_effect = effect.Effect(dummy_troop[int(stuff["Other Data"]["Team"])], stuff["POS"],
                                                 stuff["POS"], stuff["ID"], stuff["Animation"])
                else:
                    this_effect = effect.Effect(dummy_troop[0], stuff["POS"], stuff["POS"],
                    stuff["ID"], stuff["Animation"])
                if this_effect.current_animation:
                    this_effect.image = this_effect.current_animation[int(stuff["Frame"])]
                this_effect.rect = this_effect.image.get_rect(center=this_effect.pos)

                if stuff["Angle"] != 0:
                    this_effect.image = pygame.transform.rotate(this_effect.image, stuff["Angle"])

        troop_model = {}  # blit troop based on layer to battle map directly to reduce workload
        for troop in self.troop_model:
            troop_model[troop] = troop._layer
        troop_model = sorted(troop_model.items(), key=lambda item: item[1])
        for new_troop in troop_model:
            self.battle_map.image.blit(new_troop[0].image, new_troop[0].rect)

        self.clock = pygame.time.Clock()
        self.run()

    def camera_process(self, key_state):
        if key_state[pygame.K_s]:  # Camera move down
            self.true_camera_pos[1] += 4
            self.camera_fix()

        elif key_state[pygame.K_w]:  # Camera move up
            self.true_camera_pos[1] -= 4
            self.camera_fix()

        if key_state[pygame.K_a]:  # Camera move left
            self.true_camera_pos[0] -= 4
            self.camera_fix()

        elif key_state[pygame.K_d]:  # Camera move right
            self.true_camera_pos[0] += 4
            self.camera_fix()

    def camera_fix(self):
        if self.true_camera_pos[0] > self.max_camera[0]:  # camera cannot go further than max x
            self.true_camera_pos[0] = self.max_camera[0]
        elif self.true_camera_pos[0] < 0:  # camera cannot go less than 0 x
            self.true_camera_pos[0] = 0

        if self.true_camera_pos[1] > self.max_camera[1]:  # same for y
            self.true_camera_pos[1] = self.max_camera[1]
        elif self.true_camera_pos[1] < 0:
            self.true_camera_pos[1] = 0

        self.camera_pos = pygame.Vector2(self.true_camera_pos * self.screen_scale[0],
                                  self.true_camera_pos * self.screen_scale[1]) * 5

        self.camera_topleft_corner = (self.camera_pos[0] - self.center_screen[0],
                                      self.camera_pos[1] - self.center_screen[
                                          1])  # calculate top left corner of camera position

    def run(self):
        while True:
            dt = self.clock.get_time() / 1000
            key_state = pygame.key.get_pressed()

            for event in pygame.event.get():
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.camera_process(key_state)

            if self.current_weather.spawn_rate:  # spawn weather matter like snow or rain
                self.weather_spawn_timer += dt
                if self.weather_spawn_timer >= self.current_weather.spawn_rate:
                    self.weather_spawn_timer = 0
                    self.spawn_weather_matter()

            self.weather_updater.update(dt, 100)

            self.screen.fill((0, 0, 0))
            self.camera.update(self.camera_pos, self.ground_camera)

            self.screen.blit(self.camera.image, (0, 0))
            self.sky_camera.draw(self.screen)

            pygame.display.update()  # update self display, draw everything
            self.clock.tick(60)  # clock update


screen = screeninfo.get_monitors()[0]
screen_width = int(screen.width)
screen_height = int(screen.height)

# Read config file
config = configparser.ConfigParser()

config.read_file(open(os.path.join(main_dir, "photo-studio", "configuration.ini")))  # read config file

screen_width = int(config["DEFAULT"]["screen_width"])
screen_height = int(config["DEFAULT"]["screen_height"])
photo_map = config["DEFAULT"]["map"]
battle_data = config["DEFAULT"]["battle_data"]
module = config["DEFAULT"]["module"]
art_style = config["DEFAULT"]["art_style"]
day_time = config["DEFAULT"]["day_time"]
weather_type = int(config["DEFAULT"]["weather_type"])
wind_direction = int(config["DEFAULT"]["wind_direction"])
weather_strength = int(config["DEFAULT"]["weather_strength"])

Studio((screen_width, screen_height), photo_map, battle_data, module, art_style, day_time,
       (weather_type, wind_direction, weather_strength))  # change screen width and height for custom screen size
