import ast
import csv
import datetime
import math
import os
import re
from pathlib import Path

import pygame
import pygame.freetype
from gamescript import readstat, map, lorebook, weather, drama, battleui, menu, faction, popup


def load_game_data(game):
    """Load various game data and encyclopedia object"""
    main_dir = game.main_dir
    SCREENRECT = game.SCREENRECT
    Soundvolume = game.Soundvolume

    # v Craete feature terrain modifier
    game.featuremod = {}
    with open(os.path.join(main_dir, "data", "map", "unit_terrainbonus.csv"), encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        run = 0  # for skipping the first row
        for row in rd:
            for n, i in enumerate(row):
                if run != 0:
                    if n == 12:  # effect list is at column 12
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                        elif i.isdigit():
                            row[n] = [int(i)]

                    elif n in (2, 3, 4, 5, 6, 7):  # other modifer column
                        if i != "":
                            row[n] = float(i) / 100
                        else:  # empty row assign 1.0 default
                            row[n] = 1.0

                    elif i.isdigit() or "-" in i:  # modifer bonus (including negative) in other column
                        row[n] = int(i)

            run += 1
            game.featuremod[row[0]] = row[1:]
    unitfile.close()
    # ^ End feature terrain mod

    # v Create weather related class
    game.allweather = csv_read(game.main_dir, "weather.csv", ["data", "map", "weather"])
    weatherlist = [item[0] for item in game.allweather.values()][2:]
    strengthlist = ["Light ", "Normal ", "Strong "]
    game.weather_list = []
    for item in weatherlist:
        for strength in strengthlist:
            game.weather_list.append(strength + item)
    game.weather_matter_imgs = []

    for weather_sprite in ("0", "1", "2", "3"):  # Load weather matter sprite image
        imgs = load_images(game.main_dir, ["map", "weather", weather_sprite], loadorder=False)
        game.weather_matter_imgs.append(imgs)

    game.weather_effect_imgs = []
    for weather_effect in ("0", "1", "2", "3", "4", "5", "6", "7"):  # Load weather effect sprite image
        imgs = load_images(game.main_dir, ["map", "weather", "effect", weather_effect], loadorder=False)
        # imgs = []
        # for img in imgsold:
        #     img = pygame.transform.scale(img, (SCREENRECT.width, SCREENRECT.height))
        #     imgs.append(img)
        game.weather_effect_imgs.append(imgs)

    imgs = load_images(game.main_dir, ["map", "weather", "icon"], loadorder=False)  # Load weather icon
    weather.Weather.images = imgs
    # ^ End weather

    # v Faction class
    faction.Factiondata.main_dir = main_dir
    game.allfaction = faction.Factiondata(option=game.ruleset_folder)
    imgsold = load_images(game.main_dir, ["ruleset", game.ruleset_folder, "faction", "coa"], loadorder=False)  # coa imagelist
    imgs = []
    for img in imgsold:
        imgs.append(img)
    game.coa = imgs
    game.faction_list = [item[0] for item in game.allfaction.faction_list.values()][1:]
    # ^ End faction

    # v create game map texture and their default variables
    game.featurelist = []
    with open(os.path.join(main_dir, "data", "map", "unit_terrainbonus.csv"), encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        for row in rd:
            game.featurelist.append(row[1])  # get terrain feature combination name for folder
    unitfile.close()
    game.featurelist = game.featurelist[1:]

    map.FeatureMap.main_dir = main_dir
    map.FeatureMap.featuremod = game.featuremod
    map.BeautifulMap.main_dir = main_dir

    game.battlemap_base = map.BaseMap(1)  # create base terrain map
    game.battlemap_feature = map.FeatureMap(1)  # create terrain feature map
    game.battlemap_height = map.HeightMap(1)  # create height map
    game.showmap = map.BeautifulMap(1)

    emptyimage = load_image(game.main_dir, "empty.png", "map/texture")  # empty texture image
    maptexture = []
    loadtexturefolder = []
    for feature in game.featurelist:
        loadtexturefolder.append(feature.replace(" ", "").lower())  # convert terrain feature list to lower case with no space
    loadtexturefolder = list(set(loadtexturefolder))  # list of terrian folder to load
    loadtexturefolder = [item for item in loadtexturefolder if item != ""]  # For now remove terrain with no planned name/folder yet
    for index, texturefolder in enumerate(loadtexturefolder):
        imgs = load_images(game.main_dir, ["map", "texture", texturefolder], loadorder=False)
        maptexture.append(imgs)
    map.BeautifulMap.textureimages = maptexture
    map.BeautifulMap.loadtexturelist = loadtexturefolder
    map.BeautifulMap.emptyimage = emptyimage
    # ^ End game map

    # v Load genre list
    genrefolder = Path(os.path.join(main_dir, "gamescript"))
    subdirectories = [x for x in genrefolder.iterdir() if x.is_dir()]
    subdirectories = [str(foldername).split("\\")[-1].capitalize() for foldername in subdirectories]
    subdirectories.remove("__pycache__")
    game.genrelist = subdirectories  # map name list for map selection list
    # ^ End genre list

    # v Load map list
    mapfolder = Path(os.path.join(main_dir, "data", "ruleset", game.ruleset_folder, "map"))
    subdirectories = [x for x in mapfolder.iterdir() if x.is_dir()]

    for index, filemap in enumerate(subdirectories):
        if "custom" in str(filemap):  # remove custom from this folder list to load
            subdirectories.pop(index)
            break

    game.maplist = []  # map name list for map selection list
    game.mapfoldername = []  # folder for reading later

    for filemap in subdirectories:
        game.mapfoldername.append(str(filemap).split("\\")[-1])
        with open(os.path.join(str(filemap), "info.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[0] != "name":
                    game.maplist.append(row[0])
        unitfile.close()
    # ^ End load map list

    # v Load custom map list
    mapfolder = Path(os.path.join(main_dir, "data", "ruleset", game.ruleset_folder, "map", "custom"))
    subdirectories = [x for x in mapfolder.iterdir() if x.is_dir()]

    game.mapcustomlist = []
    game.mapcustomfoldername = []

    for filemap in subdirectories:
        game.mapcustomfoldername.append(str(filemap).split("\\")[-1])
        with open(os.path.join(str(filemap), "info.csv"), encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[0] != "name":
                    game.mapcustomlist.append(row[0])
        unitfile.close()
    # ^ End load custom map list

    game.statetext = {0: "Idle", 1: "Walking", 2: "Running", 3: "Walk (M)", 4: "Run (M)", 5: "Walk (R)", 6: "Run (R)",
                      7: "Walk (F)", 8: "Run (F)", 10: "Fighting", 11: "shooting", 65: "Sleeping", 66: "Camping", 67: "Resting", 68: "Dancing",
                      69: "Partying", 95: "Disobey", 96: "Retreating", 97: "Collapse", 98: "Retreating", 99: "Broken", 100: "Destroyed"}

    # v create subunit related class
    imgsold = load_images(game.main_dir, ["ui", "unit_ui", "weapon"])
    imgs = []
    for img in imgsold:
        x, y = img.get_width(), img.get_height()
        img = pygame.transform.scale(img, (int(x / 1.7), int(y / 1.7)))  # scale 1.7 seem to be most fitting as a placeholder
        imgs.append(img)
    game.allweapon = readstat.Weaponstat(game.main_dir, imgs, game.ruleset)  # Create weapon class

    imgs = load_images(game.main_dir, ["ui", "unit_ui", "armour"])
    game.allarmour = readstat.Armourstat(main_dir, imgs, game.ruleset)  # Create armour class

    game.status_imgs = load_images(game.main_dir, ["ui", "status_icon"], loadorder=False)
    game.role_imgs = load_images(game.main_dir, ["ui", "role_icon"], loadorder=False)
    game.trait_imgs = load_images(game.main_dir, ["ui", "trait_icon"], loadorder=False)
    game.skill_imgs = load_images(game.main_dir, ["ui", "skill_icon"], loadorder=False)

    cooldown = pygame.Surface((game.skill_imgs[0].get_width(), game.skill_imgs[0].get_height()), pygame.SRCALPHA)
    cooldown.fill((230, 70, 80, 200))  # red colour filter for skill cooldown timer
    battleui.SkillCardIcon.cooldown = cooldown

    activeskill = pygame.Surface((game.skill_imgs[0].get_width(), game.skill_imgs[0].get_height()), pygame.SRCALPHA)
    activeskill.fill((170, 220, 77, 200))  # green colour filter for skill active timer
    battleui.SkillCardIcon.activeskill = activeskill

    game.troop_data = readstat.Unitstat(main_dir, game.ruleset, game.ruleset_folder)

    # v create leader list
    imgs, order = load_images(game.main_dir, ["ruleset", game.ruleset_folder, "leader", "portrait"], loadorder=False, returnorder=True)
    game.leader_stat = readstat.Leaderstat(main_dir, imgs, order, option=game.ruleset_folder)
    # ^ End leader

    # v Encyclopedia related objects
    lorebook.Lorebook.concept_stat = csv_read(game.main_dir, "concept_stat.csv", ["data", "ruleset", game.ruleset_folder, "lore"])
    lorebook.Lorebook.concept_lore = csv_read(game.main_dir, "concept_lore.csv", ["data", "ruleset", game.ruleset_folder, "lore"])
    lorebook.Lorebook.history_stat = csv_read(game.main_dir, "history_stat.csv", ["data", "ruleset", game.ruleset_folder, "lore"])
    lorebook.Lorebook.history_lore = csv_read(game.main_dir, "history_lore.csv", ["data", "ruleset", game.ruleset_folder, "lore"])

    lorebook.Lorebook.faction_lore = game.allfaction.faction_list
    lorebook.Lorebook.unit_stat = game.troop_data.troop_list
    lorebook.Lorebook.troop_lore = game.troop_data.troop_lore
    lorebook.Lorebook.armour_stat = game.allarmour.armour_list
    lorebook.Lorebook.weapon_stat = game.allweapon.weapon_list
    lorebook.Lorebook.mount_stat = game.troop_data.mount_list
    lorebook.Lorebook.mount_armour_stat = game.troop_data.mount_armour_list
    lorebook.Lorebook.status_stat = game.troop_data.status_list
    lorebook.Lorebook.skillstat = game.troop_data.skill_list
    lorebook.Lorebook.trait_stat = game.troop_data.trait_list
    lorebook.Lorebook.leader = game.leader_stat
    lorebook.Lorebook.leader_lore = game.leader_stat.leader_lore
    lorebook.Lorebook.terrain_stat = game.featuremod
    lorebook.Lorebook.weather_stat = game.allweather
    lorebook.Lorebook.landmark_stat = None
    lorebook.Lorebook.unit_grade_stat = game.troop_data.grade_list
    lorebook.Lorebook.unit_class_list = game.troop_data.role
    lorebook.Lorebook.leader_class_list = game.leader_stat.leader_class
    lorebook.Lorebook.mount_grade_stat = game.troop_data.mount_grade_list
    lorebook.Lorebook.race_list = game.troop_data.race_list
    lorebook.Lorebook.SCREENRECT = SCREENRECT
    lorebook.Lorebook.main_dir = main_dir
    lorebook.Lorebook.statetext = game.statetext

    imgs = load_images(game.main_dir, ["ui", "lorebook_ui"], loadorder=False)
    game.lorebook = lorebook.Lorebook(game.main_dir, game.screen_scale, game.SCREENRECT, imgs[0])  # encyclopedia sprite
    game.lorenamelist = lorebook.SubsectionList(game.screen_scale, game.lorebook.rect.topleft, imgs[1])

    imgs = load_images(game.main_dir, ["ui", "lorebook_ui", "button"], loadorder=False)
    for index, img in enumerate(imgs):
        imgs[index] = pygame.transform.scale(img, (int(img.get_width() * game.screen_scale[0]),
                                                   int(img.get_height() * game.screen_scale[1])))
    game.lorebuttonui = [
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5), game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[0], 0, 13),  # concept section button
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 2,
                          game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[1], 1, 13),  # history section button
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 3,
                          game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[2], 2, 13),  # faction section button
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 4,
                          game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[3], 3, 13),  # troop section button
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 5,
                          game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[4], 4, 13),  # troop equipment section button
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 6,
                          game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[5], 5, 13),  # troop status section button
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 7,
                          game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[6], 6, 13),  # troop skill section button
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 8,
                          game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[7], 7, 13),  # troop property section button
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 9,
                          game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[8], 8, 13),  # leader section button
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 10,
                          game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[9], 9, 13),  # terrain section button
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 11,
                          game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[10], 10, 13),  # weather section button
        battleui.UIButton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 13,
                          game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[12], 19, 13),  # close button
        battleui.UIButton(game.lorebook.rect.bottomleft[0] + (imgs[13].get_width()), game.lorebook.rect.bottomleft[1] - imgs[13].get_height(),
                          imgs[13], 20, 24),  # previous page button
        battleui.UIButton(game.lorebook.rect.bottomright[0] - (imgs[14].get_width()), game.lorebook.rect.bottomright[1] - imgs[14].get_height(),
                          imgs[14], 21, 24)]  # next page button
    game.pagebutton = (game.lorebuttonui[12], game.lorebuttonui[13])
    game.lorescroll = battleui.UIScroller(game.lorenamelist.rect.topright, game.lorenamelist.image.get_height(),
                                          game.lorebook.max_subsection_show, layer=25)  # add subsection list scroller
    # ^ End encyclopedia objects

    # v Create gamebattle game ui objects
    game.minimap = battleui.Minimap((SCREENRECT.width, SCREENRECT.height))

    # Popup Ui
    imgs = load_images(game.main_dir, ["ui", "popup_ui", "terraincheck"], loadorder=False)
    popup.TerrainPopup.images = imgs
    popup.TerrainPopup.SCREENRECT = SCREENRECT
    imgs = load_images(game.main_dir, ["ui", "popup_ui", "dramatext"], loadorder=False)
    drama.TextDrama.images = imgs

    topimage = load_images(game.main_dir, ["ui", "battle_ui"])

    game.eventlog = battleui.EventLog(topimage[23], (0, SCREENRECT.height))
    game.trooplog_button = battleui.UIButton(game.eventlog.pos[0] + (topimage[24].get_width() / 2), game.eventlog.pos[1] -
                                             game.eventlog.image.get_height() - (topimage[24].get_height() / 2), topimage[24], 0)  # troop tab log

    game.eventlog_button = [
        battleui.UIButton(game.trooplog_button.pos[0] + topimage[24].get_width(), game.trooplog_button.pos[1], topimage[25], 1),
        # army tab log button
        battleui.UIButton(game.trooplog_button.pos[0] + (topimage[24].get_width() * 2), game.trooplog_button.pos[1], topimage[26], 2),
        # leader tab log button
        battleui.UIButton(game.trooplog_button.pos[0] + (topimage[24].get_width() * 3), game.trooplog_button.pos[1], topimage[27], 3),
        # subunit tab log button
        battleui.UIButton(game.trooplog_button.pos[0] + (topimage[24].get_width() * 5), game.trooplog_button.pos[1], topimage[28], 4),
        # delete current tab log button
        battleui.UIButton(game.trooplog_button.pos[0] + (topimage[24].get_width() * 6), game.trooplog_button.pos[1], topimage[29], 5)]
    # delete all log button

    game.eventlog_button = [game.trooplog_button] + game.eventlog_button
    game.buttonui.add(game.eventlog_button)

    game.logscroll = battleui.UIScroller(game.eventlog.rect.topright, topimage[23].get_height(), game.eventlog.max_row_show)  # event log scroller
    game.eventlog.logscroll = game.logscroll  # Link scroller to ui since it is easier to do here with the current order

    game.troopcard_ui = battleui.GameUI(x=SCREENRECT.width - topimage[2].get_size()[0] / 2,
                                        y=(topimage[0].get_size()[1] * 2.5) + topimage[5].get_size()[1],
                                        image=topimage[2], icon="", uitype="troopcard")
    game.gameui.add(game.troopcard_ui)
    game.troopcard_ui.featurelist = game.featurelist  # add terrain feature list name to subunit card

    # Button related to subunit card and command
    game.troopcard_button = [battleui.UIButton(game.troopcard_ui.x - 152, game.troopcard_ui.y + 10, topimage[3], 0),
                             # subunit card description button
                             battleui.UIButton(game.troopcard_ui.x - 152, game.troopcard_ui.y - 70, topimage[4], 1),  # subunit card stat button
                             battleui.UIButton(game.troopcard_ui.x - 152, game.troopcard_ui.y - 30, topimage[7], 2),  # subunit card skill button
                             battleui.UIButton(game.troopcard_ui.x - 152, game.troopcard_ui.y + 50, topimage[22], 3)]  # subunit card equipment button

    game.buttonui.add(game.troopcard_button)

    game.terraincheck = popup.TerrainPopup()  # popup box that show terrain information when right click on map
    game.button_name_popup = popup.OnelinePopup()  # popup box that show button name when mouse over
    game.leader_popup = popup.OnelinePopup()  # popup box that show leader name when mouse over
    game.effect_popup = popup.EffecticonPopup()  # popup box that show skill/trait/status name when mouse over

    drama.TextDrama.SCREENRECT = SCREENRECT
    game.textdrama = drama.TextDrama()  # messege at the top of screen that show up for important event

    game.fpscount = battleui.FPScount()  # FPS number counter

    game.battledone_box = battleui.BattleDone(game.screen_scale, (game.screen_width / 2, game.screen_height / 2), topimage[-3], topimage[-4])
    game.gamedone_button = battleui.UIButton(game.battledone_box.pos[0], game.battledone_box.boximage.get_height() * 0.8, topimage[-2], newlayer=19)

    # v Esc menu related objects
    imgs = load_images(game.main_dir, ["ui", "battlemenu_ui"], loadorder=False)
    menu.Escbox.images = imgs  # Create ESC Menu box
    menu.Escbox.SCREENRECT = SCREENRECT
    game.battle_menu = menu.Escbox()

    buttonimage = load_images(game.main_dir, ["ui", "battlemenu_ui", "button"], loadorder=False)
    menurectcenter0 = game.battle_menu.rect.center[0]
    menurectcenter1 = game.battle_menu.rect.center[1]

    game.battle_menu_button = [
        menu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 - 100), text="Resume", size=14),
        menu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 - 50), text="Encyclopedia", size=14),
        menu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1), text="Option", size=14),
        menu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 + 50), text="End Battle", size=14),
        menu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 + 100), text="Desktop", size=14)]

    game.escoption_menu_button = [
        menu.Escbutton(buttonimage, (menurectcenter0 - 50, menurectcenter1 + 70), text="Confirm", size=14),
        menu.Escbutton(buttonimage, (menurectcenter0 + 50, menurectcenter1 + 70), text="Apply", size=14),
        menu.Escbutton(buttonimage, (menurectcenter0 + 150, menurectcenter1 + 70), text="Cancel", size=14)]

    sliderimage = load_images(game.main_dir, ["ui", "battlemenu_ui", "slider"], loadorder=False)
    game.escslidermenu = [menu.SliderMenu(sliderimage[0], sliderimage[1:3],
                                          (menurectcenter0 * 1.1, menurectcenter1), Soundvolume, 0)]
    game.escvaluebox = [menu.ValueBox(sliderimage[3], (game.battle_menu.rect.topright[0] * 1.2, menurectcenter1), Soundvolume)]
    # ^ End esc menu objects


def make_bar_list(main_dir, screen_scale, listtodo, menuimage):
    """Make a drop down bar list option button"""
    barlist = []
    img = load_image(main_dir, "bar_normal.jpg", "ui\\mainmenu_ui")
    img2 = load_image(main_dir, "bar_mouse.jpg", "ui\\mainmenu_ui")
    img3 = img2
    for index, bar in enumerate(listtodo):
        barimage = (img.copy(), img2.copy(), img3.copy())
        bar = menu.MenuButton(screen_scale, images=barimage, pos=(menuimage.pos[0], menuimage.pos[1] + img.get_height() * (index + 1)), text=bar)
        barlist.append(bar)
    return barlist


def load_base_button(main_dir):
    img = load_image(main_dir, "idle_button.png", ["ui", "mainmenu_ui"])
    img2 = load_image(main_dir, "mouse_button.png", ["ui", "mainmenu_ui"])
    img3 = load_image(main_dir, "click_button.png", ["ui", "mainmenu_ui"])
    return [img, img2, img3]


def text_objects(text, font):
    textsurface = font.render(text, True, (200, 200, 200))
    return textsurface, textsurface.get_rect()


def load_image(main_dir, file, subfolder=""):
    """loads an image, prepares it for play"""
    newsubfolder = subfolder
    if isinstance(newsubfolder, list):
        newsubfolder = ""
        for folder in subfolder:
            newsubfolder = os.path.join(newsubfolder, folder)
    thisfile = os.path.join(main_dir, "data", newsubfolder, file)
    surface = pygame.image.load(thisfile).convert_alpha()
    return surface


def load_images(main_dir, subfolder=None, loadorder=True, returnorder=False):
    """loads all images(files) in folder using loadorder list file use only png file"""
    imgs = []
    dirpath = os.path.join(main_dir, "data")
    if subfolder is not None:
        for folder in subfolder:
            dirpath = os.path.join(dirpath, folder)

    if loadorder:  # load in the order of load_order file
        loadorderfile = open(os.path.join(dirpath, "load_order.txt"), "r")
        loadorderfile = ast.literal_eval(loadorderfile.read())
        for file in loadorderfile:
            imgs.append(load_image(main_dir, file, dirpath))
    else:  # load every file
        loadorderfile = [f for f in os.listdir(dirpath) if f.endswith("." + "png")]  # read all file
        loadorderfile.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", var)])
        for file in loadorderfile:
            imgs.append(load_image(main_dir, file, dirpath))

    if returnorder is False:
        return imgs
    else:  # return order of the file as list
        loadorderfile = [int(name.replace(".png", "")) for name in loadorderfile]
        return imgs, loadorderfile


def csv_read(maindir, file, subfolder=(), outputtype=0):
    """output type 0 = dict, 1 = list"""
    main_dir = maindir
    returnoutput = {}
    if outputtype == 1:
        returnoutput = []

    folder_dir = ""
    for folder in subfolder:
        folder_dir = os.path.join(folder_dir, folder)
    folder_dir = os.path.join(folder_dir, file)
    folder_dir = os.path.join(main_dir, folder_dir)
    with open(folder_dir, encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None):
                    row[n] = int(i)
            if outputtype == 0:
                returnoutput[row[0]] = row[1:]
            elif outputtype == 1:
                returnoutput.append(row)
        unitfile.close()
    return returnoutput


def load_sound(main_dir, file):
    file = os.path.join(main_dir, "data", "sound", file)
    sound = pygame.mixer.Sound(file)
    return sound


def edit_config(section, option, value, filename, config):
    config.set(section, option, value)
    with open(filename, "w") as configfile:
        config.write(configfile)


def trait_skill_blit(self):
    """For blitting skill and trait icon into subunit info ui"""
    SCREENRECT = self.SCREENRECT

    position = self.troopcard_ui.rect.topleft
    position = [position[0] + 70, position[1] + 60]  # start position
    startrow = position[0]

    for icon in self.skill_icon.sprites():
        icon.kill()

    for trait in self.troopcard_ui.value2[0]:
        self.skill_icon.add(
            battleui.SkillCardIcon(self.trait_imgs[0], (position[0], position[1]), 0, gameid=trait))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow

    position = self.troopcard_ui.rect.topleft
    position = [position[0] + 70, position[1] + 100]
    startrow = position[0]

    for skill in self.troopcard_ui.value2[1]:
        self.skill_icon.add(
            battleui.SkillCardIcon(self.skill_imgs[0], (position[0], position[1]), 1, gameid=skill))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow


def effect_icon_blit(self):
    """For blitting all status effect icon"""
    SCREENRECT = self.SCREENRECT

    position = self.troopcard_ui.rect.topleft
    position = [position[0] + 70, position[1] + 140]
    startrow = position[0]

    for icon in self.effect_icon.sprites():
        icon.kill()

    for status in self.troopcard_ui.value2[4]:
        self.effect_icon.add(battleui.SkillCardIcon(self.status_imgs[0], (position[0], position[1]), 4, gameid=status))
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow


def countdown_skill_icon(self):
    """Count down timer on skill icon for activate and cooldown time"""
    for skill in self.skill_icon:
        if skill.icontype == 1:  # only do skill icon not trait
            cd = 0
            activetime = 0
            if skill.gameid in self.troopcard_ui.value2[2]:
                cd = int(self.troopcard_ui.value2[2][skill.gameid])
            if skill.gameid in self.troopcard_ui.value2[3]:
                activetime = int(self.troopcard_ui.value2[3][skill.gameid][3])
            skill.iconchange(cd, activetime)
    # for effect in self.effect_icon:
    #     cd = 0
    #     if effect.id in self.troopcard_ui.value2[4]:
    #         cd = int(self.troopcard_ui.value2[4][effect.id][3])
    #     effect.iconchange(cd, 0)


def rotationxy(origin, point, angle):
    ox, oy = origin
    px, py = point
    x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return pygame.Vector2(x, y)


def convert_str_time(event):
    for index, item in enumerate(event):
        newtime = datetime.datetime.strptime(item[1], "%H:%M:%S").time()
        newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
        event[index] = [item[0], newtime]
        if len(item) == 3:
            event[index].append(item[2])


def kill_effect_icon(self):
    for icon in self.skill_icon.sprites():
        icon.kill()
        del icon
    for icon in self.effect_icon.sprites():
        icon.kill()
        del icon


def setuplist(screen_scale, itemclass, currentrow, showlist, itemgroup, box, uiclass, layer=15):
    """generate list of subsection of the left side of encyclopedia"""
    row = 5 * screen_scale[1]
    column = 5 * screen_scale[0]
    pos = box.rect.topleft
    if currentrow > len(showlist) - box.maxshowlist:
        currentrow = len(showlist) - box.maxshowlist

    if len(itemgroup) > 0:  # remove previous sprite in the group before generate new one
        for stuff in itemgroup:
            stuff.kill()
            del stuff

    for index, item in enumerate(showlist):
        if index >= currentrow:
            itemgroup.add(itemclass(screen_scale, box, (pos[0] + column, pos[1] + row), item, layer=layer))  # add new subsection sprite to group
            row += (30 * screen_scale[1])  # next row
            if len(itemgroup) > box.maxshowlist:
                break  # will not generate more than space allowed

        uiclass.add(*itemgroup)


def popout_lorebook(self, section, gameid):
    """open and draw enclycopedia at the specified subsection, used for when user right click at icon that has encyclopedia section"""
    self.gamestate = 0
    self.battle_menu.mode = 2
    self.battleui.add(self.lorebook, self.lorenamelist, self.lorescroll, *self.lorebuttonui)

    self.lorebook.change_section(section, self.lorenamelist, self.subsection_name, self.lorescroll, self.pagebutton, self.battleui)
    self.lorebook.change_subsection(gameid, self.pagebutton, self.battleui)
    self.lorescroll.changeimage(newrow=self.lorebook.current_subsection_row)


def popuplist_newopen(self, newrect, newlist, uitype):
    """Move popup_listbox and scroll sprite to new location and create new name list baesd on type"""
    self.currentpopuprow = 0

    if uitype == "leader" or uitype == "genre":
        self.popup_listbox.rect = self.popup_listbox.image.get_rect(topleft=newrect)
    else:
        self.popup_listbox.rect = self.popup_listbox.image.get_rect(midbottom=newrect)

    setuplist(self.screen_scale, menu.NameList, 0, newlist, self.popup_namegroup,
                   self.popup_listbox, self.battleui, layer=19)

    self.popup_listscroll.pos = self.popup_listbox.rect.topright  # change position variable
    self.popup_listscroll.rect = self.popup_listscroll.image.get_rect(topleft=self.popup_listbox.rect.topright)  #
    self.popup_listscroll.changeimage(newrow=0, logsize=len(newlist))

    if uitype == "genre":
        self.mainui.add(self.popup_listbox, *self.popup_namegroup, self.popup_listscroll)
    else:
        self.battleui.add(self.popup_listbox, *self.popup_namegroup, self.popup_listscroll)  # add the option list to screen

    self.popup_listbox.type = uitype
