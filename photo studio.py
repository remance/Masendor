import os.path
import sys
import csv
import configparser

import glob
from pathlib import Path

import pygame
import screeninfo
from gamescript import battlemap, weather, battleui, menu, effectsprite, battle, camera, datasprite, datamap, game

from gamescript.common.utility import csv_read, load_images, stat_convert
from gamescript.common.battle import setup_battle_troop
from gamescript.common.battle.spawn_weather_matter import spawn_weather_matter
from gamescript.common.game.setup.make_faction_troop_leader_data import make_faction_troop_leader_data
from gamescript.common.game.create_troop_sprite_pool import create_troop_sprite_pool

team_colour = game.Game.team_colour

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
        if leader:  # leader subunit
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
        else:  # troop subunit
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


class Studio(game.Game):
    spawn_weather_matter = spawn_weather_matter
    create_troop_sprite_pool = create_troop_sprite_pool

    def __init__(self, photo_size, map_name, battle_data_name, module, day_time, weather_event):
        pygame.init()  # Initialize pygame
        self.screen_rect = pygame.Rect(0, 0, photo_size[0], photo_size[1])
        camera.Camera.screen_rect = self.screen_rect
        self.screen_scale = (self.screen_rect.width / 1920, self.screen_rect.height / 1080)
        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, 0, 32)
        self.screen = pygame.display.set_mode(self.screen_rect.size, 0 | pygame.RESIZABLE, self.best_depth)

        self.module_list = csv_read(data_dir, "module_list.csv", ("module",))  # get module list
        self.module_folder = str(self.module_list[module][0]).strip("/")

        self.main_dir = main_dir
        self.data_dir = data_dir
        self.module_dir = os.path.join(data_dir, "module", self.module_folder)

        self.troop_data, self.leader_data, self.faction_data = make_faction_troop_leader_data(self.data_dir, self.module_dir,
                                                                                              self.screen_scale, "en")
        self.battle_map_data = datamap.BattleMapData(self.module_dir, self.screen_scale, "en")

        self.battle_base_map = battlemap.BaseMap(data_dir)  # create base terrain map
        self.battle_feature_map = battlemap.FeatureMap(data_dir)  # create terrain feature map
        self.battle_height_map = battlemap.HeightMap()  # create height map
        self.battle_map = battlemap.BeautifulMap(data_dir, self.screen_scale, self.battle_height_map)

        self.battle_base_map.terrain_list = self.battle_map_data.terrain_list
        self.battle_base_map.terrain_colour = self.battle_map_data.terrain_colour
        self.battle_feature_map.feature_list = self.battle_map_data.feature_list
        self.battle_feature_map.feature_colour = self.battle_map_data.feature_colour
        self.battle_feature_map.feature_mod = self.battle_map_data.feature_mod

        self.battle_map.battle_map_colour = self.battle_map_data.battle_map_colour
        self.battle_map.texture_images = self.battle_map_data.map_texture
        self.battle_map.load_texture_list = self.battle_map_data.texture_folder
        self.battle_map.empty_texture = self.battle_map_data.empty_image
        self.battle_map.camp_texture = self.battle_map_data.camp_image

        self.map_move_array = []
        self.map_def_array = []

        images = load_images(data_dir, subfolder=("module", self.module_folder, "map", "preset", map_name))
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
        self.battle_map.draw_image(self.battle_base_map, self.battle_feature_map, place_name_map, {}, self)

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
        weather.SpecialEffect.containers = self.weather_effect, self.sky_camera, self.weather_updater
        effectsprite.EffectSprite.containers = self.ground_camera
        battleui.SpriteIndicator.containers = self.ground_camera

        battle_ui_image = load_images(data_dir, subfolder=("ui", "battle_ui"))

        weather.Weather.wind_compass_images = {"wind_compass": battle_ui_image["wind_compass"],
                                               "wind_arrow": battle_ui_image["wind_arrow"]}

        self.weather_matter_images = self.battle_map_data.weather_matter_images

        self.weather_screen_adjust = self.screen_rect.width / self.screen_rect.height  # for weather sprite spawn position
        self.current_weather = weather.Weather(TroopModel(pygame.Surface((0, 0)), (0, 0), 0, 0, 1), weather_event[0], weather_event[1],
                                               weather_event[2], self.battle_map_data.weather_data)

        self.battle_map.change_map_stuff("effect", self.battle_map_data.weather_effect_images[self.current_weather.name][self.current_weather.level],
                                         self.battle_map_data.day_effect_images[day_time])
        self.weather_spawn_timer = 0

        self.troop_animation = datasprite.TroopAnimationData(data_dir, self.module_dir,
                                                             [str(self.troop_data.race_list[key]["Name"]) for key in
                                                              self.troop_data.race_list], self.team_colour)
        self.subunit_animation_data = self.troop_animation.subunit_animation_data  # animation data pool
        self.gen_body_sprite_pool = self.troop_animation.gen_body_sprite_pool  # body sprite pool
        self.gen_weapon_sprite_pool = self.troop_animation.gen_weapon_sprite_pool  # weapon sprite pool
        self.gen_armour_sprite_pool = self.troop_animation.gen_armour_sprite_pool  # armour sprite pool
        self.weapon_joint_list = self.troop_animation.weapon_joint_list  # weapon joint data
        self.colour_list = self.troop_animation.colour_list  # skin colour list

        self.effect_sprite_pool = self.troop_animation.effect_sprite_pool
        self.effect_animation_pool = self.troop_animation.effect_animation_pool

        effectsprite.EffectSprite.effect_list = self.troop_data.effect_list

        effectsprite.EffectSprite.effect_sprite_pool = self.effect_sprite_pool
        effectsprite.EffectSprite.effect_animation_pool = self.effect_animation_pool

        self.battle_data = {}
        with open(os.path.join(main_dir, "photo studio", self.module_folder, battle_data_name + ".csv"), encoding="utf-8",
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
            if stuff["Type"] == "subunit":
                if type(stuff["ID"]) is str:
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
                # battleui.SpriteIndicator(new_troop.hitbox_image, new_troop, self)

            elif stuff["Type"] == "effect":
                if "Team" in stuff["Other Data"]:
                    effect = effectsprite.EffectSprite(dummy_troop[int(stuff["Other Data"]["Team"])], stuff["POS"],
                                                       (stuff["POS"][0] * 5, stuff["POS"][1] * 5),
                                                       (stuff["POS"][0] * 5, stuff["POS"][1] * 5), stuff["ID"], stuff["Animation"])
                else:
                    effect = effectsprite.EffectSprite(dummy_troop[0], stuff["POS"], (stuff["POS"][0] * 5, stuff["POS"][1] * 5),
                                                       (stuff["POS"][0] * 5, stuff["POS"][1] * 5), stuff["ID"], stuff["Animation"])
                effect.image = effect.current_animation[int(stuff["Frame"])]
                effect.rect = effect.image.get_rect(center=effect.pos)

                if stuff["Angle"] != 0:
                    effect.image = pygame.transform.rotate(effect.image, stuff["Angle"])

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

config.read_file(open(os.path.join(main_dir, "photo studio", "configuration.ini")))  # read config file

screen_width = int(config["DEFAULT"]["screen_width"])
screen_height = int(config["DEFAULT"]["screen_height"])
photo_map = config["DEFAULT"]["map"]
battle_data = config["DEFAULT"]["battle_data"]
module = int(config["DEFAULT"]["module"])
day_time = config["DEFAULT"]["day_time"]
weather_type = int(config["DEFAULT"]["weather_type"])
wind_direction = int(config["DEFAULT"]["wind_direction"])
weather_strength = int(config["DEFAULT"]["weather_strength"])

Studio((screen_width, screen_height), photo_map, battle_data, module, day_time,
       (weather_type, wind_direction, weather_strength))  # change screen width and height for custom screen size
