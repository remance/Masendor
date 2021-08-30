import ast
import csv
import datetime
import math
import os
import random
import re

import numpy as np
import pygame
import pygame.freetype

"""This file contains fuctions of various purposes"""

# Default game mechanic value

battlesidecal = (1, 0.5, 0.1, 0.5)  # battlesidecal is for melee combat side modifier,

letterboard = ("a", "b", "c", "d", "e", "f", "g", "h")  # letter according to subunit position in inspect ui similar to chess board
numberboard = ("8", "7", "6", "5", "4", "3", "2", "1")  # same as above
boardpos = []
for dd in numberboard:
    for ll in letterboard:
        boardpos.append(ll + dd)


# Data Loading gamescript


def makebarlist(main, listtodo, menuimage):
    """Make a drop down bar list option button"""
    from gamescript import gameprepare
    main_dir = main.main_dir
    barlist = []
    img = load_image(main_dir, "bar_normal.jpg", "ui\\mainmenu_ui")
    img2 = load_image(main_dir, "bar_mouse.jpg", "ui\\mainmenu_ui")
    img3 = img2
    for index, bar in enumerate(listtodo):
        barimage = (img.copy(), img2.copy(), img3.copy())
        bar = gameprepare.Menubutton(main, images=barimage, pos=(menuimage.pos[0], menuimage.pos[1] + img.get_height() * (index + 1)), text=bar)
        barlist.append(bar)
    return barlist


def load_base_button(main_dir):
    img = load_image(main_dir, "idle_button.png", "ui\\mainmenu_ui")
    img2 = load_image(main_dir, "mouse_button.png", "ui\\mainmenu_ui")
    img3 = load_image(main_dir, "click_button.png", "ui\\mainmenu_ui")
    return [img, img2, img3]


def text_objects(text, font):
    textsurface = font.render(text, True, (200, 200, 200))
    return textsurface, textsurface.get_rect()


def game_intro(screen, clock, introoption):
    intro = introoption
    if introoption:
        intro = True
    timer = 0
    # quote = ["Those attacker fail to learn from the mistakes of their predecessors are destined to repeat them. George Santayana",
    # "It is more important to outhink your enemy, than to outfight him, Sun Tzu"]
    while intro:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                intro = False
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        large_text = pygame.font.Font("freesansbold.ttf", 115)
        text_surf, text_rect = text_objects("Test Intro", large_text)
        text_rect.center = (700, 600)
        screen.blit(text_surf, text_rect)
        pygame.display.update()
        clock.tick(60)
        timer += 1
        if timer == 1000:
            intro = False


def load_image(main_dir, file, subfolder=""):
    """loads an image, prepares it for play"""
    thisfile = os.path.join(main_dir, "data", subfolder, file)
    try:
        surface = pygame.image.load(thisfile).convert_alpha()
    except pygame.error:
        raise SystemExit("Could not load image" "%s" "%s" % (thisfile, pygame.get_error()))
    return surface.convert_alpha()


def load_images(main_dir, subfolder=None, loadorder=True, returnorder=False):
    """loads all images(files) in folder using loadorder list file use only png file"""
    imgs = []
    dirpath = os.path.join(main_dir, "data")
    if subfolder is not None:
        for folder in subfolder:
            dirpath = os.path.join(dirpath, folder)

    if loadorder:  # load in the order of load_order file
        loadorderfile = open(dirpath + "/load_order.txt", "r")
        loadorderfile = ast.literal_eval(loadorderfile.read())
        for file in loadorderfile:
            imgs.append(load_image(main_dir, dirpath + "/" + file))
    else:  # load every file
        loadorderfile = [f for f in os.listdir(dirpath) if f.endswith("." + "png")]  # read all file
        loadorderfile.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", var)])
        for file in loadorderfile:
            imgs.append(load_image(main_dir, dirpath + "/" + file))

    if returnorder is False:
        return imgs
    else:  # return order of the file as list
        loadorderfile = [int(name.replace(".png", "")) for name in loadorderfile]
        return imgs, loadorderfile


def load_game_data(game):
    """Load various game data and encyclopedia object"""
    import csv
    from pathlib import Path

    main_dir = game.main_dir
    SCREENRECT = game.SCREENRECT
    Soundvolume = game.Soundvolume
    from gamescript import gamemap, gamelorebook, gameweather, gameunitstat, gameui, gamefaction, gameunit, \
        gamesubunit, gamerangeattack, gamemenu, gamepopup, gamedrama, gameunitedit

    # v Craete feature terrain modifier
    game.featuremod = {}
    with open(main_dir + "/data/map" + "/unit_terrainbonus.csv", encoding="utf-8", mode="r") as unitfile:
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
    game.weathermatterimgs = []

    for weather in ("0", "1", "2", "3"):  # Load weather matter sprite image
        imgs = load_images(game.main_dir, ["map", "weather", weather], loadorder=False)
        game.weathermatterimgs.append(imgs)

    game.weathereffectimgs = []
    for weather in ("0", "1", "2", "3", "4", "5", "6", "7"):  # Load weather effect sprite image
        imgs = load_images(game.main_dir, ["map", "weather", "effect", weather], loadorder=False)
        # imgs = []
        # for img in imgsold:
        #     img = pygame.transform.scale(img, (SCREENRECT.width, SCREENRECT.height))
        #     imgs.append(img)
        game.weathereffectimgs.append(imgs)

    imgs = load_images(game.main_dir, ["map", "weather", "icon"], loadorder=False)  # Load weather icon
    gameweather.Weather.images = imgs
    # ^ End weather

    # v Faction class
    gamefaction.Factiondata.main_dir = main_dir
    game.allfaction = gamefaction.Factiondata(option=game.rulesetfolder)
    imgsold = load_images(game.main_dir, ["ruleset", game.rulesetfolder.strip("/"), "faction", "coa"], loadorder=False)  # coa imagelist
    imgs = []
    for img in imgsold:
        imgs.append(img)
    game.coa = imgs
    game.faction_list = [item[0] for item in game.allfaction.faction_list.values()][1:]
    # ^ End faction

    # v create game map texture and their default variables
    game.featurelist = []
    with open(main_dir + "/data/map" + "/unit_terrainbonus.csv", encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        for row in rd:
            game.featurelist.append(row[1])  # get terrain feature combination name for folder
    unitfile.close()
    game.featurelist = game.featurelist[1:]

    gamemap.Mapfeature.main_dir = main_dir
    gamemap.Mapfeature.featuremod = game.featuremod
    gamemap.Beautifulmap.main_dir = main_dir

    game.battlemap_base = gamemap.Basemap(1)  # create base terrain map
    game.battlemap_feature = gamemap.Mapfeature(1)  # create terrain feature map
    game.battlemap_height = gamemap.Mapheight(1)  # create height map
    game.showmap = gamemap.Beautifulmap(1)

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
    gamemap.Beautifulmap.textureimages = maptexture
    gamemap.Beautifulmap.loadtexturelist = loadtexturefolder
    gamemap.Beautifulmap.emptyimage = emptyimage
    # ^ End game map

    # v Load map list
    mapfolder = Path(main_dir + "/data/ruleset/" + game.rulesetfolder + "/map")
    subdirectories = [x for x in mapfolder.iterdir() if x.is_dir()]

    for index, filemap in enumerate(subdirectories):
        if "custom" in str(filemap):  # remove custom from this folder list to load
            subdirectories.pop(index)
            break

    game.maplist = []  # map name list for map selection list
    game.mapfoldername = []  # folder for reading later

    for filemap in subdirectories:
        game.mapfoldername.append(str(filemap).split("\\")[-1])
        with open(str(filemap) + "/info.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[0] != "name":
                    game.maplist.append(row[0])
        unitfile.close()
    # ^ End load map list

    # v Load custom map list
    mapfolder = Path(main_dir + "/data/ruleset/" + game.rulesetfolder + "/map/custom/")
    subdirectories = [x for x in mapfolder.iterdir() if x.is_dir()]

    game.mapcustomlist = []
    game.mapcustomfoldername = []

    for filemap in subdirectories:
        game.mapcustomfoldername.append(str(filemap).split("\\")[-1])
        with open(str(filemap) + "/info.csv", encoding="utf-8", mode="r") as unitfile:
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
    game.allweapon = gameunitstat.Weaponstat(game.main_dir, imgs, game.ruleset)  # Create weapon class

    imgs = load_images(game.main_dir, ["ui", "unit_ui", "armour"])
    game.allarmour = gameunitstat.Armourstat(main_dir, imgs, game.ruleset)  # Create armour class

    game.statusimgs = load_images(game.main_dir, ["ui", "status_icon"], loadorder=False)
    game.roleimgs = load_images(game.main_dir, ["ui", "role_icon"], loadorder=False)
    game.traitimgs = load_images(game.main_dir, ["ui", "trait_icon"], loadorder=False)
    game.skillimgs = load_images(game.main_dir, ["ui", "skill_icon"], loadorder=False)

    cooldown = pygame.Surface((game.skillimgs[0].get_width(), game.skillimgs[0].get_height()), pygame.SRCALPHA)
    cooldown.fill((230, 70, 80, 200))  # red colour filter for skill cooldown timer
    gameui.Skillcardicon.cooldown = cooldown

    activeskill = pygame.Surface((game.skillimgs[0].get_width(), game.skillimgs[0].get_height()), pygame.SRCALPHA)
    activeskill.fill((170, 220, 77, 200))  # green colour filter for skill active timer
    gameui.Skillcardicon.activeskill = activeskill

    game.gameunitstat = gameunitstat.Unitstat(main_dir, game.ruleset, game.rulesetfolder)

    gameunit.Unitarmy.status_list = game.gameunitstat.status_list
    gamerangeattack.Rangearrow.gamemapheight = game.battlemap_height

    imgs = load_images(game.main_dir, ["ui", "unit_ui"])
    gamesubunit.Subunit.images = imgs
    gamesubunit.Subunit.gamemap = game.battlemap_base  # add gamebattle map to all parentunit class
    gamesubunit.Subunit.gamemapfeature = game.battlemap_feature  # add gamebattle map to all parentunit class
    gamesubunit.Subunit.gamemapheight = game.battlemap_height
    gamesubunit.Subunit.weapon_list = game.allweapon
    gamesubunit.Subunit.armour_list = game.allarmour
    gamesubunit.Subunit.stat_list = game.gameunitstat
    gameunitedit.Armybuildslot.images = imgs
    gameunitedit.Armybuildslot.weapon_list = game.allweapon
    gameunitedit.Armybuildslot.armour_list = game.allarmour
    gameunitedit.Armybuildslot.stat_list = game.gameunitstat

    game.squadwidth, game.squadheight = imgs[0].get_width(), imgs[0].get_height()  # size of subnit image at closest zoom
    # ^ End subunit class

    # v create leader list
    imgs, order = load_images(game.main_dir, ["ruleset", game.rulesetfolder.strip("/"), "leader", "portrait"], loadorder=False, returnorder=True)
    game.leader_stat = gameunitstat.Leaderstat(main_dir, imgs, order, option=game.rulesetfolder)
    # ^ End leader

    # v Game Effect related class
    imgs = load_images(game.main_dir, ["effect"])
    # imgs = []
    # for img in imgsold:
    # x, y = img.get_width(), img.get_height()
    # img = pygame.transform.scale(img, (int(x ), int(y / 2)))
    # imgs.append(img)
    gamerangeattack.Rangearrow.images = [imgs[0]]
    # ^ End game effect

    # v Encyclopedia related objects
    gamelorebook.Lorebook.concept_stat = csv_read(game.main_dir, "concept_stat.csv", ["data", "ruleset", game.rulesetfolder.strip("/"), "lore"])
    gamelorebook.Lorebook.concept_lore = csv_read(game.main_dir, "concept_lore.csv", ["data", "ruleset", game.rulesetfolder.strip("/"), "lore"])
    gamelorebook.Lorebook.history_stat = csv_read(game.main_dir, "history_stat.csv", ["data", "ruleset", game.rulesetfolder.strip("/"), "lore"])
    gamelorebook.Lorebook.history_lore = csv_read(game.main_dir, "history_lore.csv", ["data", "ruleset", game.rulesetfolder.strip("/"), "lore"])

    gamelorebook.Lorebook.faction_lore = game.allfaction.faction_list
    gamelorebook.Lorebook.unit_stat = game.gameunitstat.unit_list
    gamelorebook.Lorebook.unit_lore = game.gameunitstat.unit_lore
    gamelorebook.Lorebook.armour_stat = game.allarmour.armour_list
    gamelorebook.Lorebook.weapon_stat = game.allweapon.weapon_list
    gamelorebook.Lorebook.mount_stat = game.gameunitstat.mount_list
    gamelorebook.Lorebook.mount_armour_stat = game.gameunitstat.mount_armour_list
    gamelorebook.Lorebook.status_stat = game.gameunitstat.status_list
    gamelorebook.Lorebook.skillstat = game.gameunitstat.ability_list
    gamelorebook.Lorebook.trait_stat = game.gameunitstat.trait_list
    gamelorebook.Lorebook.leader = game.leader_stat
    gamelorebook.Lorebook.leader_lore = game.leader_stat.leader_lore
    gamelorebook.Lorebook.terrain_stat = game.featuremod
    gamelorebook.Lorebook.weather_stat = game.allweather
    gamelorebook.Lorebook.landmark_stat = None
    gamelorebook.Lorebook.unit_grade_stat = game.gameunitstat.grade_list
    gamelorebook.Lorebook.unit_class_list = game.gameunitstat.role
    gamelorebook.Lorebook.leader_class_list = game.leader_stat.leader_class
    gamelorebook.Lorebook.mount_grade_stat = game.gameunitstat.mount_grade_list
    gamelorebook.Lorebook.race_list = game.gameunitstat.race_list
    gamelorebook.Lorebook.SCREENRECT = SCREENRECT
    gamelorebook.Lorebook.main_dir = main_dir
    gamelorebook.Lorebook.statetext = game.statetext

    imgs = load_images(game.main_dir, ["ui", "lorebook_ui"], loadorder=False)
    game.lorebook = gamelorebook.Lorebook(game, imgs[0])  # encyclopedia sprite
    game.lorenamelist = gamelorebook.SubsectionList(game, game.lorebook.rect.topleft, imgs[1])

    imgs = load_images(game.main_dir, ["ui", "lorebook_ui", "button"], loadorder=False)
    for index, img in enumerate(imgs):
        imgs[index] = pygame.transform.scale(img, (int(img.get_width() * game.width_adjust),
                                                   int(img.get_height() * game.height_adjust)))
    game.lorebuttonui = [
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5), game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                        imgs[0], 0, 13),  # concept section button
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 2,
                        game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                        imgs[1], 1, 13),  # history section button
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 3,
                        game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                        imgs[2], 2, 13),  # faction section button
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 4,
                        game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                        imgs[3], 3, 13),  # troop section button
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 5,
                        game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                        imgs[4], 4, 13),  # troop equipment section button
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 6,
                        game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                        imgs[5], 5, 13),  # troop status section button
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 7,
                        game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                        imgs[6], 6, 13),  # troop ability section button
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 8,
                        game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                        imgs[7], 7, 13),  # troop property section button
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 9,
                        game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                        imgs[8], 8, 13),  # leader section button
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 10,
                        game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[9], 9, 13),  # terrain section button
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 11,
                        game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[10], 10, 13),  # weather section button
        gameui.Uibutton(game.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 13,
                        game.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[12], 19, 13),  # close button
        gameui.Uibutton(game.lorebook.rect.bottomleft[0] + (imgs[13].get_width()), game.lorebook.rect.bottomleft[1] - imgs[13].get_height(),
                        imgs[13], 20, 24),  # previous page button
        gameui.Uibutton(game.lorebook.rect.bottomright[0] - (imgs[14].get_width()), game.lorebook.rect.bottomright[1] - imgs[14].get_height(),
                        imgs[14], 21, 24)]  # next page button
    game.pagebutton = (game.lorebuttonui[12], game.lorebuttonui[13])
    game.lorescroll = gameui.Uiscroller(game.lorenamelist.rect.topright, game.lorenamelist.image.get_height(),
                                        game.lorebook.max_subsection_show, layer=25)  # add subsection list scroller
    # ^ End encyclopedia objects

    # v Create gamebattle game ui objects
    game.minimap = gameui.Minimap((SCREENRECT.width, SCREENRECT.height))

    # Popup Ui
    imgs = load_images(game.main_dir, ["ui", "popup_ui", "terraincheck"], loadorder=False)
    gamepopup.TerrainPopup.images = imgs
    gamepopup.TerrainPopup.SCREENRECT = SCREENRECT
    imgs = load_images(game.main_dir, ["ui", "popup_ui", "dramatext"], loadorder=False)
    gamedrama.Textdrama.images = imgs

    # Load all image of ui and icon from folder
    topimage = load_images(game.main_dir, ["ui", "battle_ui"])
    iconimage = load_images(game.main_dir, ["ui", "battle_ui", "topbar_icon"])

    # Army select list ui
    game.unitselector = gameui.Armyselect((0, 0), topimage[30])
    game.selectscroll = gameui.Uiscroller(game.unitselector.rect.topright, topimage[30].get_height(),
                                          game.unitselector.max_row_show)  # scroller for unit select ui

    # Right top bar ui that show rough information of selected battalions
    game.gameui = [
        gameui.Gameui(x=SCREENRECT.width - topimage[0].get_size()[0] / 2, y=topimage[0].get_size()[1] / 2, image=topimage[0],
                      icon=iconimage, uitype="topbar")]
    game.gameui[0].options1 = game.statetext

    game.inspectuipos = [game.gameui[0].rect.bottomleft[0] - game.squadwidth / 1.25,
                         game.gameui[0].rect.bottomleft[1] - game.squadheight / 3]

    # Left top command ui with leader and parentunit behavious button
    iconimage = load_images(game.main_dir, ["ui", "battle_ui", "commandbar_icon"])
    game.gameui.append(gameui.Gameui(x=topimage[1].get_size()[0] / 2, y=(topimage[1].get_size()[1] / 2) + game.unitselector.image.get_height(),
                                     image=topimage[1], icon=iconimage,
                                     uitype="commandbar"))

    # Subunit information card ui
    game.gameui.append(
        gameui.Gameui(x=SCREENRECT.width - topimage[2].get_size()[0] / 2, y=(topimage[0].get_size()[1] * 2.5) + topimage[5].get_size()[1],
                      image=topimage[2], icon="", uitype="unitcard"))
    game.gameui[2].featurelist = game.featurelist  # add terrain feature list name to subunit card

    game.gameui.append(gameui.Gameui(x=SCREENRECT.width - topimage[5].get_size()[0] / 2, y=topimage[0].get_size()[1] * 4,
                                     image=topimage[5], icon="", uitype="unitbox"))  # inspect ui that show subnit in selected parentunit
    # v Subunit shown in inspect ui
    width, height = game.inspectuipos[0], game.inspectuipos[1]
    subunitnum = 0  # Number of subnit based on the position in row and column
    imgsize = (game.squadwidth, game.squadheight)
    game.inspectsubunit = []
    for subunit in list(range(0, 64)):
        width += imgsize[0]
        game.inspectsubunit.append(gameui.Inspectsubunit((width, height)))
        subunitnum += 1
        if subunitnum == 8:  # Reach the last subnit in the row, go to the next one
            width = game.inspectuipos[0]
            height += imgsize[1]
            subunitnum = 0
    # ^ End subunit shown

    # Time bar ui
    game.timeui = gameui.Timeui(game.unitselector.rect.topright, topimage[31])
    game.timenumber = gameui.Timer(game.timeui.rect.topleft)  # time number on time ui
    game.speednumber = gameui.Speednumber((game.timeui.rect.center[0] + 40, game.timeui.rect.center[1]),
                                          1)  # game speed number on the time ui

    image = pygame.Surface((topimage[31].get_width(), 15))
    game.scaleui = gameui.Scaleui(game.timeui.rect.bottomleft, image)

    # Button related to subunit card and command
    game.buttonui = [gameui.Uibutton(game.gameui[2].x - 152, game.gameui[2].y + 10, topimage[3], 0),  # subunit card description button
                     gameui.Uibutton(game.gameui[2].x - 152, game.gameui[2].y - 70, topimage[4], 1),  # subunit card stat button
                     gameui.Uibutton(game.gameui[2].x - 152, game.gameui[2].y - 30, topimage[7], 2),  # subunit card skill button
                     gameui.Uibutton(game.gameui[2].x - 152, game.gameui[2].y + 50, topimage[22], 3),  # subunit card equipment button
                     gameui.Uibutton(game.gameui[0].x - 206, game.gameui[0].y - 1, topimage[6], 1),  # unit inspect open/close button
                     gameui.Uibutton(game.gameui[1].x - 115, game.gameui[1].y + 26, topimage[8], 0),  # split by middle coloumn button
                     gameui.Uibutton(game.gameui[1].x - 115, game.gameui[1].y + 56, topimage[9], 1),  # split by middle row button
                     gameui.Uibutton(game.gameui[1].x + 100, game.gameui[1].y + 56, topimage[14], 1)]  # decimation button

    # Behaviour button that once click switch to other mode for subunit behaviour
    game.switch_button = [gameui.Switchuibutton(game.gameui[1].x - 40, game.gameui[1].y + 96, topimage[10:14]),  # skill condition button
                          gameui.Switchuibutton(game.gameui[1].x - 80, game.gameui[1].y + 96, topimage[15:17]),  # fire at will button
                          gameui.Switchuibutton(game.gameui[1].x, game.gameui[1].y + 96, topimage[17:20]),  # behaviour button
                          gameui.Switchuibutton(game.gameui[1].x + 40, game.gameui[1].y + 96, topimage[20:22]),  # shoot range button
                          gameui.Switchuibutton(game.gameui[1].x - 125, game.gameui[1].y + 96, topimage[35:38]),  # arcshot button
                          gameui.Switchuibutton(game.gameui[1].x + 80, game.gameui[1].y + 96, topimage[38:40]),  # toggle run button
                          gameui.Switchuibutton(game.gameui[1].x + 120, game.gameui[1].y + 96, topimage[40:43])]  # toggle melee mode

    game.eventlog = gameui.Eventlog(topimage[23], (0, SCREENRECT.height))

    game.logscroll = gameui.Uiscroller(game.eventlog.rect.topright, topimage[23].get_height(), game.eventlog.max_row_show)  # event log scroller
    game.eventlog.logscroll = game.logscroll  # Link scroller to ui since it is easier to do here with the current order
    gamesubunit.Subunit.eventlog = game.eventlog  # Assign eventlog to subunit class to broadcast event to the log

    game.buttonui.append(gameui.Uibutton(game.eventlog.pos[0] + (topimage[24].get_width() / 2),
                                         game.eventlog.pos[1] - game.eventlog.image.get_height() - (topimage[24].get_height() / 2), topimage[24],
                                         0))  # war tab log button

    game.buttonui += [gameui.Uibutton(game.buttonui[8].pos[0] + topimage[24].get_width(), game.buttonui[8].pos[1], topimage[25], 1),
                      # army tab log button
                      gameui.Uibutton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 2), game.buttonui[8].pos[1], topimage[26], 2),
                      # leader tab log button
                      gameui.Uibutton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 3), game.buttonui[8].pos[1], topimage[27], 3),
                      # subunit tab log button
                      gameui.Uibutton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 5), game.buttonui[8].pos[1], topimage[28], 4),
                      # delete current tab log button
                      gameui.Uibutton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 6), game.buttonui[8].pos[1], topimage[29], 5),
                      # delete all log button
                      gameui.Uibutton(game.timeui.rect.center[0] - 30, game.timeui.rect.center[1], topimage[32], 0),  # time pause button
                      gameui.Uibutton(game.timeui.rect.center[0], game.timeui.rect.center[1], topimage[33], 1),  # time decrease button
                      gameui.Uibutton(game.timeui.rect.midright[0] - 60, game.timeui.rect.center[1], topimage[34], 2)]  # time increase button

    game.screenbuttonlist = game.buttonui[8:17]  # event log and time buttons
    game.unitcardbutton = game.buttonui[0:4]
    game.inspectbutton = game.buttonui[4]
    game.col_split_button = game.buttonui[5]  # parentunit split by column button
    game.rowsplitbutton = game.buttonui[6]  # parentunit split by row button

    game.timebutton = game.buttonui[14:17]
    game.battleui.add(game.buttonui[8:17])
    game.battleui.add(game.logscroll, game.selectscroll)

    gameui.Selectedsquad.image = topimage[-1]  # subunit border image always the last one
    game.inspectselectedborder = gameui.Selectedsquad((15000, 15000))  # yellow border on selected subnit in inspect ui
    game.mainui.remove(game.inspectselectedborder)  # remove subnit border sprite from gamestart menu drawer
    game.terraincheck = gamepopup.TerrainPopup()  # popup box that show terrain information when right click on map
    game.button_name_popup = gamepopup.OnelinePopup()  # popup box that show button name when mouse over
    game.leaderpopup = gamepopup.OnelinePopup()  # popup box that show leader name when mouse over
    game.effectpopup = gamepopup.EffecticonPopup()  # popup box that show skill/trait/status name when mouse over

    gamedrama.Textdrama.SCREENRECT = SCREENRECT
    game.textdrama = gamedrama.Textdrama()  # messege at the top of screen that show up for important event

    game.fpscount = gameui.FPScount()  # FPS number counter

    game.battledone_box = gameui.Battledone(game, topimage[-3], topimage[-4])
    game.gamedone_button = gameui.Uibutton(game.battledone_box.pos[0], game.battledone_box.boximage.get_height() * 0.8, topimage[-2], newlayer=19)
    # ^ End game ui

    # v Esc menu related objects
    imgs = load_images(game.main_dir, ["ui", "battlemenu_ui"], loadorder=False)
    gamemenu.Escbox.images = imgs  # Create ESC Menu box
    gamemenu.Escbox.SCREENRECT = SCREENRECT
    game.battle_menu = gamemenu.Escbox()

    buttonimage = load_images(game.main_dir, ["ui", "battlemenu_ui", "button"], loadorder=False)
    menurectcenter0 = game.battle_menu.rect.center[0]
    menurectcenter1 = game.battle_menu.rect.center[1]

    game.battle_menu_button = [
        gamemenu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 - 100), text="Resume", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 - 50), text="Encyclopedia", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1), text="Option", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 + 50), text="End Battle", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 + 100), text="Desktop", size=14)]

    game.escoption_menu_button = [
        gamemenu.Escbutton(buttonimage, (menurectcenter0 - 50, menurectcenter1 + 70), text="Confirm", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0 + 50, menurectcenter1 + 70), text="Apply", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0 + 150, menurectcenter1 + 70), text="Cancel", size=14)]

    sliderimage = load_images(game.main_dir, ["ui", "battlemenu_ui", "slider"], loadorder=False)
    game.escslidermenu = [gamemenu.Escslider(sliderimage[0], sliderimage[1:3],
                                             (menurectcenter0 * 1.1, menurectcenter1), Soundvolume, 0)]
    game.escvaluebox = [gamemenu.Escvaluebox(sliderimage[3], (game.battle_menu.rect.topright[0] * 1.2, menurectcenter1), Soundvolume)]
    # ^ End esc menu objects


def csv_read(maindir, file, subfolder=(), outputtype=0):
    """output type 0 = dict, 1 = list"""
    main_dir = maindir
    returnoutput = {}
    if outputtype == 1:
        returnoutput = []

    folderlist = ""
    for folder in subfolder:
        folderlist += "/" + folder
    folderlist += "/" + file
    with open(main_dir + folderlist, encoding="utf-8", mode="r") as unitfile:
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
    file = os.path.join(main_dir, "data/sound/", file)
    sound = pygame.mixer.Sound(file)
    return sound


def editconfig(section, option, value, filename, config):
    config.set(section, option, value)
    with open(filename, "w") as configfile:
        config.write(configfile)


# Other gamebattle gamescript

def convert_str_time(event):
    for index, item in enumerate(event):
        newtime = datetime.datetime.strptime(item[1], "%H:%M:%S").time()
        newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
        event[index] = [item[0], newtime]
        if len(item) == 3:
            event[index].append(item[2])


def traitskillblit(self):
    """For blitting skill and trait icon into subunit info ui"""
    from gamescript import gameui
    SCREENRECT = self.SCREENRECT

    position = self.gameui[2].rect.topleft
    position = [position[0] + 70, position[1] + 60]  # start position
    startrow = position[0]

    for icon in self.skill_icon.sprites():
        icon.kill()

    for trait in self.gameui[2].value2[0]:
        self.skill_icon.add(gameui.Skillcardicon(self.traitimgs[0], (position[0], position[1]), 0, gameid=trait))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow

    position = self.gameui[2].rect.topleft
    position = [position[0] + 70, position[1] + 100]
    startrow = position[0]

    for skill in self.gameui[2].value2[1]:
        self.skill_icon.add(gameui.Skillcardicon(self.skillimgs[0], (position[0], position[1]), 1, gameid=skill))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow


def effecticonblit(self):
    """For blitting all status effect icon"""
    from gamescript import gameui
    SCREENRECT = self.SCREENRECT

    position = self.gameui[2].rect.topleft
    position = [position[0] + 70, position[1] + 140]
    startrow = position[0]

    for icon in self.effect_icon.sprites():
        icon.kill()

    for status in self.gameui[2].value2[4]:
        self.effect_icon.add(gameui.Skillcardicon(self.statusimgs[0], (position[0], position[1]), 4, gameid=status))
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow


def countdownskillicon(self):
    """Count down timer on skill icon for activate and cooldown time"""
    for skill in self.skill_icon:
        if skill.icontype == 1:  # only do skill icon not trait
            cd = 0
            activetime = 0
            if skill.gameid in self.gameui[2].value2[2]:
                cd = int(self.gameui[2].value2[2][skill.gameid])
            if skill.gameid in self.gameui[2].value2[3]:
                activetime = int(self.gameui[2].value2[3][skill.gameid][3])
            skill.iconchange(cd, activetime)
    # for effect in self.effect_icon:
    #     cd = 0
    #     if effect.id in self.gameui[2].value2[4]:
    #         cd = int(self.gameui[2].value2[4][effect.id][3])
    #     effect.iconchange(cd, 0)


# Battle Start related gamescript


def addunit(subunitlist, position, gameid, colour, leader, leaderstat, control, coa, command, startangle, starthp, startstamina, team):
    """Create batalion object into the battle and leader of the parentunit"""
    from gamescript import gameunit, gameleader
    oldsubunitlist = subunitlist[~np.all(subunitlist == 0, axis=1)]  # remove whole empty column in subunit list
    subunitlist = oldsubunitlist[:, ~np.all(oldsubunitlist == 0, axis=0)]  # remove whole empty row in subunit list
    unit = gameunit.Unitarmy(position, gameid, subunitlist, colour, control, coa, command, abs(360 - startangle), starthp, startstamina, team)

    # add leader
    unit.leader = [gameleader.Leader(leader[0], leader[4], 0, unit, leaderstat),
                   gameleader.Leader(leader[1], leader[5], 1, unit, leaderstat),
                   gameleader.Leader(leader[2], leader[6], 2, unit, leaderstat),
                   gameleader.Leader(leader[3], leader[7], 3, unit, leaderstat)]
    return unit


def generateunit(gamebattle, whicharmy, row, control, command, colour, coa, subunitgameid):
    """generate unit data into game object
    row[1:9] is subunit troop id array, row[9][0] is leader id and row[9][1] is position of sub-unt the leader located in"""
    from gamescript import gameunit, gamesubunit
    unit = addunit(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                   colour, row[10] + row[11], gamebattle.leader_stat, control,
                   coa, command, row[13], row[14], row[15], row[16])
    whicharmy.add(unit)
    armysubunitindex = 0  # armysubunitindex is list index for subunit list in a specific army

    # v Setup subunit in unit to subunit group
    row, column = 0, 0
    maxcolumn = len(unit.armysubunit[0])
    for subunitnum in np.nditer(unit.armysubunit, op_flags=["readwrite"], order="C"):
        if subunitnum != 0:
            addsubunit = gamesubunit.Subunit(subunitnum, subunitgameid, unit, unit.subunit_position_list[armysubunitindex],
                                             unit.starthp, unit.startstamina, gamebattle.unitscale)
            gamebattle.subunit.add(addsubunit)
            addsubunit.board_pos = boardpos[armysubunitindex]
            subunitnum[...] = subunitgameid
            unit.subunit_sprite_array[row][column] = addsubunit
            unit.subunit_sprite.append(addsubunit)
            subunitgameid += 1
        else:
            unit.subunit_sprite_array[row][column] = None  # replace numpy None with python None

        column += 1
        if column == maxcolumn:
            column = 0
            row += 1
        armysubunitindex += 1
    gamebattle.troopnumbersprite.add(gameunit.Troopnumber(gamebattle, unit))  # create troop number text sprite

    return subunitgameid


def unitsetup(gamebattle):
    """read parentunit from unit_pos(source) file and create object with addunit function"""
    main_dir = gamebattle.main_dir
    # defaultunit = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
    # [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])

    teamcolour = gamebattle.teamcolour
    teamarmy = (gamebattle.team0unit, gamebattle.team1unit, gamebattle.team2unit)

    with open(
            main_dir + "/data/ruleset" + gamebattle.rulesetfolder + "/map/" + gamebattle.mapselected + "/" + gamebattle.source + "/unit_pos" + ".csv",
            encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        subunitgameid = 1
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit():
                    row[n] = int(i)
                if n in range(1, 12):
                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]

            control = False
            if gamebattle.playerteam == row[16] or gamebattle.enactment:  # player can control only his team or both in enactment mode
                control = True

            colour = teamcolour[row[16]]
            whicharmy = teamarmy[row[16]]

            command = False  # Not commander parentunit by default
            if len(whicharmy) == 0:  # First parentunit is commander
                command = True
            coa = pygame.transform.scale(gamebattle.coa[row[12]], (60, 60))  # get coa image and scale smaller to fit ui
            subunitgameid = generateunit(gamebattle, whicharmy, row, control, command, colour, coa, subunitgameid)
            # ^ End subunit setup

    unitfile.close()


def convertedit_unit(gamebattle, whicharmy, row, colour, coa, subunitgameid):
    for n, i in enumerate(row):
        if type(i) == str and i.isdigit():
            row[n] = int(i)
        if n in range(1, 12):
            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
    subunitgameid = generateunit(gamebattle, whicharmy, row, True, True, colour, coa, subunitgameid)


# Battle related gamescript

def setrotate(self, set_target=None):
    """set base_target and new angle for sprite rotation"""
    if set_target is None:  # For auto chase rotate
        myradians = math.atan2(self.base_target[1] - self.base_pos[1], self.base_target[0] - self.base_pos[0])
    else:  # Command move or rotate
        myradians = math.atan2(set_target[1] - self.base_pos[1], set_target[0] - self.base_pos[0])
    newangle = math.degrees(myradians)

    # """upper left -"""
    if -180 <= newangle <= -90:
        newangle = -newangle - 90

    # """upper right +"""
    elif -90 < newangle < 0:
        newangle = (-newangle) - 90

    # """lower right -"""
    elif 0 <= newangle <= 90:
        newangle = -(newangle + 90)

    # """lower left +"""
    elif 90 < newangle <= 180:
        newangle = 270 - newangle

    return round(newangle)


def rotationxy(self, origin, point, angle):
    ox, oy = origin
    px, py = point
    x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return pygame.Vector2(x, y)


def losscal(attacker, defender, hit, defense, dmgtype, defside=None):
    """Calculate dmg, type 0 is melee attack and will use attacker subunit stat,
    type that is not 0 will use the type object stat instead (mostly used for range attack)"""
    who = attacker
    target = defender

    heightadventage = who.height - target.height
    if dmgtype != 0:
        heightadventage = int(heightadventage / 2)  # Range attack use less height advantage
    hit += heightadventage

    if defense < 0 or who.ignore_def:  # Ignore def trait
        defense = 0

    hitchance = hit - defense
    if hitchance < 0:
        hitchance = 0
    elif hitchance > 80:  # Critical hit
        hitchance *= who.crit_effect  # modify with crit effect further
        if hitchance > 200:
            hitchance = 200
    else:  # infinity number can cause nan value
        hitchance = 200

    combatscore = round(hitchance / 100, 1)
    if combatscore == 0 and random.randint(0, 10) > 9:  # Final chence to not miss
        combatscore = 0.1

    leaderdmgbonus = 0
    if who.leader is not None:
        leaderdmgbonus = who.leader.combat  # Get extra dmg from leader combat ability

    if dmgtype == 0:  # Melee dmg
        dmg = random.uniform(who.dmg[0], who.dmg[1])
        if who.chargeskill in who.skill_effect:  # Include charge in dmg if attacking
            if who.ignore_chargedef is False:  # Ignore charge defense if have ignore trait
                sidecal = battlesidecal[defside]
                if target.fulldef or target.temp_fulldef:  # Defense all side
                    sidecal = 1
                dmg = dmg + ((who.charge - (target.chargedef * sidecal)) * 2)
                if target.chargedef >= who.charge / 2:
                    who.charge_momentum = 1  # charge get stopped by charge def
                else:
                    who.charge_momentum -= target.chargedef / who.charge
            else:
                dmg = dmg + (who.charge * 2)

        if target.chargeskill in target.skill_effect:  # Also include chargedef in dmg if enemy charging
            if target.ignore_chargedef is False:
                chargedefcal = who.chargedef - target.charge
                if chargedefcal < 0:
                    chargedefcal = 0
                dmg = dmg + (chargedefcal * 2)  # if charge def is higher than enemy charge then deal back addtional dmg
        elif who.chargeskill not in who.skill_effect:  # not charging or defend from charge, use attack speed roll
            dmg += sum([random.uniform(who.dmg[0], who.dmg[1]) for x in range(who.meleespeed)])

        dmg = dmg * ((100 - (target.armour * who.melee_penetrate)) / 100) * combatscore

    else:  # Range Damage
        dmg = dmgtype.dmg * ((100 - (target.armour * dmgtype.penetrate)) / 100) * combatscore

    leaderdmg = dmg
    unitdmg = (dmg * who.troopnumber) + leaderdmgbonus  # dmg on subunit is dmg multiply by troop number with addition from leader combat
    if (who.anti_inf and target.unit_type in (1, 2)) or (who.anti_cav and target.unit_type in (4, 5, 6, 7)):  # Anti trait dmg bonus
        unitdmg = unitdmg * 1.25
    # if type == 0: # melee do less dmg per hit because the combat happen more frequently than range
    #     unitdmg = unitdmg / 20

    moraledmg = dmg / 50

    # Damage cannot be negative (it would heal instead), same for morale and leader dmg
    if unitdmg < 0:
        unitdmg = 0
    if leaderdmg < 0:
        leaderdmg = 0
    if moraledmg < 0:
        moraledmg = 0

    return unitdmg, moraledmg, leaderdmg


def applystatustoenemy(statuslist, inflictstatus, receiver, attackerside, receiverside):
    """apply aoe status effect to enemy subunits"""
    for status in inflictstatus.items():
        if status[1] == 1 and attackerside == 0:  # only front enemy
            receiver.status_effect[status[0]] = statuslist[status[0]].copy()
        elif status[1] == 2:  # aoe effect to side enemy
            receiver.status_effect[status[0]] = statuslist[status[0]].copy()
            if status[1] == 3:  # apply to corner enemy subunit (left and right of self front enemy subunit)
                corner_enemy_apply = receiver.nearby_subunit_list[0:2]
                if receiverside in (1, 2):  # attack on left/right side means corner enemy would be from front and rear side of the enemy
                    corner_enemy_apply = [receiver.nearby_subunit_list[2], receiver.nearby_subunit_list[5]]
                for subunit in corner_enemy_apply:
                    if subunit != 0:
                        subunit.status_effect[status[0]] = statuslist[status[0]].copy()
        elif status[1] == 3:  # whole parentunit aoe
            for subunit in receiver.parentunit.subunit_sprite:
                if subunit.state != 100:
                    subunit.status_effect[status[0]] = statuslist[status[0]].copy()


def complexdmg(attacker, receiver, dmg, moraledmg, leaderdmg, dmgeffect, timermod):
    final_dmg = round(dmg * dmgeffect * timermod)
    final_moraledmg = round(moraledmg * dmgeffect * timermod)
    if final_dmg > receiver.unit_health:  # dmg cannot be higher than remaining health
        final_dmg = receiver.unit_health

    receiver.unit_health -= final_dmg
    receiver.base_morale -= (final_moraledmg + attacker.bonus_morale_dmg) * receiver.mental
    receiver.stamina -= attacker.bonus_stamina_dmg

    # v Add red corner to indicate combat
    if receiver.red_corner is False:
        receiver.imageblock.blit(receiver.images[11], receiver.corner_image_rect)
        receiver.red_corner = True
    # ^ End red corner

    if attacker.elem_melee not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
        receiver.elem_count[attacker.elem_melee - 1] += round(final_dmg * (100 - receiver.elem_res[attacker.elem_melee - 1] / 100))

    attacker.base_morale += round((final_moraledmg / 5))  # recover some morale when deal morale dmg to enemy

    if receiver.leader is not None and receiver.leader.health > 0 and random.randint(0, 10) > 9:  # dmg on subunit leader, only 10% chance
        finalleaderdmg = round(leaderdmg - (leaderdmg * receiver.leader.combat / 101) * timermod)
        if finalleaderdmg > receiver.leader.health:
            finalleaderdmg = receiver.leader.health
        receiver.leader.health -= finalleaderdmg


def dmgcal(attacker, target, attackerside, targetside, statuslist, combattimer):
    """base_target position 0 = Front, 1 = Side, 3 = Rear, attackerside and targetside is the side attacking and defending respectively"""
    wholuck = random.randint(-50, 50)  # attacker luck
    targetluck = random.randint(-50, 50)  # defender luck
    whopercent = battlesidecal[attackerside]  # attacker attack side modifier

    """34 battlemaster fulldef or 91 allrounddef status = no flanked penalty"""
    if attacker.fulldef or 91 in attacker.status_effect:
        whopercent = 1
    targetpercent = battlesidecal[targetside]  # defender defend side

    if target.fulldef or 91 in target.status_effect:
        targetpercent = 1

    dmgeffect = attacker.front_dmg_effect
    targetdmgeffect = target.front_dmg_effect

    if attackerside != 0 and whopercent != 1:  # if attack or defend from side will use discipline to help reduce penalty a bit
        whopercent = battlesidecal[attackerside] + (attacker.discipline / 300)
        dmgeffect = attacker.side_dmg_effect  # use side dmg effect as some skill boost only front dmg
        if whopercent > 1:
            whopercent = 1

    if targetside != 0 and targetpercent != 1:  # same for the base_target defender
        targetpercent = battlesidecal[targetside] + (target.discipline / 300)
        targetdmgeffect = target.side_dmg_effect
        if targetpercent > 1:
            targetpercent = 1

    whohit = float(attacker.attack * whopercent) + wholuck
    whodefense = float(attacker.meleedef * whopercent) + wholuck
    targethit = float(attacker.attack * targetpercent) + targetluck
    targetdefense = float(target.meleedef * targetpercent) + targetluck

    """33 backstabber ignore def when attack rear side, 55 Oblivious To Unexpected can't defend from rear at all"""
    if (attacker.backstab and targetside == 2) or (target.oblivious and targetside == 2) or (
            target.flanker and attackerside in (1, 3)):  # Apply only for attacker
        targetdefense = 0

    whodmg, whomoraledmg, wholeaderdmg = losscal(attacker, target, whohit, targetdefense, 0, targetside)  # get dmg by attacker
    targetdmg, targetmoraledmg, targetleaderdmg = losscal(target, attacker, targethit, whodefense, 0, attackerside)  # get dmg by defender

    timermod = combattimer / 0.5  # Since the update happen anytime more than 0.5 second, high speed that pass by longer than x1 speed will become inconsistent
    complexdmg(attacker, target, whodmg, whomoraledmg, wholeaderdmg, dmgeffect, timermod)  # Inflict dmg to defender
    complexdmg(target, attacker, targetdmg, targetmoraledmg, targetleaderdmg, targetdmgeffect, timermod)  # Inflict dmg to attacker

    # v Attack corner (side) of self with aoe attack
    if attacker.corner_atk:
        listloop = [target.nearby_subunit_list[2], target.nearby_subunit_list[5]]  # Side attack get (2) front and (5) rear nearby subunit
        if targetside in (0, 2):
            listloop = target.nearby_subunit_list[0:2]  # Front/rear attack get (0) left and (1) right nearbysubunit
        for subunit in listloop:
            if subunit != 0 and subunit.state != 100:
                targethit, targetdefense = float(attacker.attack * targetpercent) + targetluck, float(subunit.meleedef * targetpercent) + targetluck
                whodmg, whomoraledmg = losscal(attacker, subunit, whohit, targetdefense, 0)
                complexdmg(attacker, subunit, whodmg, whomoraledmg, wholeaderdmg, dmgeffect, timermod)
    # ^ End attack corner

    # v inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy subunit, 4 entire parentunit
    if attacker.inflictstatus != {}:
        applystatustoenemy(statuslist, attacker.inflictstatus, target, attackerside, targetside)
    if target.inflictstatus != {}:
        applystatustoenemy(statuslist, target.inflictstatus, attacker, targetside, attackerside)
    # ^ End inflict status


def die(who, battle, moralehit=True):
    """remove subunit when it dies"""
    if who.team == 1:
        group = battle.team1unit
        enemygroup = battle.team2unit
        battle.team1poslist.pop(who.gameid)
    else:
        group = battle.team2unit
        enemygroup = battle.team1unit
        battle.team2poslist.pop(who.gameid)

    if moralehit:
        if who.commander:  # more morale penalty if the parentunit is a command parentunit
            for army in group:
                for subunit in army.subunit_sprite:
                    subunit.base_morale -= 30

        for thisarmy in enemygroup:  # get bonus authority to the another army
            thisarmy.authority += 5

        for thisarmy in group:  # morale dmg to every subunit in army when allied parentunit destroyed
            for subunit in thisarmy.subunit_sprite:
                subunit.base_morale -= 20

    battle.allunitlist.remove(who)
    battle.allunitindex.remove(who.gameid)
    group.remove(who)
    who.got_killed = True


def change_leader(self, event):
    """Leader change subunit or gone/die, event can be "die" or "broken" """
    checkstate = [100]
    if event == "broken":
        checkstate = [99, 100]
    if self.leader is not None and self.leader.state != 100:  # Find new subunit for leader if there is one in this subunit
        for subunit in self.nearby_subunit_list:
            if subunit != 0 and subunit.state not in checkstate and subunit.leader is None:
                subunit.leader = self.leader
                self.leader.subunit = subunit
                for index, subunit2 in enumerate(self.parentunit.subunit_sprite):  # loop to find new subunit pos based on new subunit_sprite list
                    if subunit2 == self.leader.subunit:
                        self.leader.subunitpos = index
                        if self.unit_leader:  # set leader subunit to new one
                            self.parentunit.leadersubunit = subunit2
                            subunit2.unit_leader = True
                            self.unit_leader = False
                        break

                self.leader = None
                break

        if self.leader is not None:  # if can't find near subunit to move leader then find from first subunit to last place in parentunit
            for index, subunit in enumerate(self.parentunit.subunit_sprite):
                if subunit.state not in checkstate and subunit.leader is None:
                    subunit.leader = self.leader
                    self.leader.subunit = subunit
                    subunit.leader.subunitpos = index
                    self.leader = None
                    if self.unit_leader:  # set leader subunit to new one
                        self.parentunit.leadersubunit = subunit
                        subunit.unit_leader = True

                    break

            if self.leader is not None and event == "die":  # Still can't find new subunit so leader disappear with chance of different result
                self.leader.state = random.randint(97, 100)  # captured, retreated, wounded, dead
                self.leader.health = 0
                self.leader.gone()

        self.unit_leader = False


def add_new_unit(gamebattle, who, addunitlist=True):
    from gamescript import gameunit
    # generate subunit sprite array for inspect ui
    who.subunit_sprite_array = np.empty((8, 8), dtype=object)  # array of subunit object(not index)
    foundcount = 0  # for subunit_sprite index
    foundcount2 = 0  # for positioning
    for row in range(0, len(who.armysubunit)):
        for column in range(0, len(who.armysubunit[0])):
            if who.armysubunit[row][column] != 0:
                who.subunit_sprite_array[row][column] = who.subunit_sprite[foundcount]
                who.subunit_sprite[foundcount].unitposition = (who.subunit_position_list[foundcount2][0] / 10,
                                                               who.subunit_position_list[foundcount2][1] / 10)  # position in parentunit sprite
                foundcount += 1
            else:
                who.subunit_sprite_array[row][column] = None
            foundcount2 += 1
    # ^ End generate subunit array

    for index, subunit in enumerate(who.subunit_sprite):  # reset leader subunitpos
        if subunit.leader is not None:
            subunit.leader.subunitpos = index

    who.zoom = 11 - gamebattle.camerascale
    who.new_angle = who.angle

    who.startset(gamebattle.subunit)
    who.set_target(who.front_pos)

    numberpos = (who.base_pos[0] - who.base_width_box,
                 (who.base_pos[1] + who.base_height_box))
    who.number_pos = who.rotationxy(who.base_pos, numberpos, who.radians_angle)
    who.change_pos_scale()  # find new position for troop number text

    for subunit in who.subunit_sprite:
        subunit.gamestart(subunit.zoom)

    if addunitlist:
        gamebattle.allunitlist.append(who)
        gamebattle.allunitindex.append(who.gameid)

    numberspite = gameunit.Troopnumber(gamebattle, who)
    gamebattle.troopnumbersprite.add(numberspite)


def move_leader_subunit(leader, oldarmysubunit, newarmysubunit, alreadypick=()):
    """oldarmysubunit is armysubunit list that the subunit currently in and need to be move out to the new one (newarmysubunit),
    alreadypick is list of position need to be skipped"""
    replace = [np.where(oldarmysubunit == leader.subunit.gameid)[0][0],
               np.where(oldarmysubunit == leader.subunit.gameid)[1][0]]  # grab old array position of subunit
    newrow = int((len(newarmysubunit) - 1) / 2)  # set up new row subunit will be place in at the middle at the start
    newplace = int((len(newarmysubunit[newrow]) - 1) / 2)  # setup new column position
    placedone = False  # finish finding slot to place yet

    while placedone is False:
        if leader.subunit.parentunit.armysubunit.flat[newrow * newplace] != 0:
            for subunit in leader.subunit.parentunit.subunit_sprite:
                if subunit.gameid == leader.subunit.parentunit.armysubunit.flat[newrow * newplace]:
                    if subunit.leader is not None or (newrow, newplace) in alreadypick:
                        newplace += 1
                        if newplace > len(newarmysubunit[newrow]) - 1:  # find new column
                            newplace = 0
                        elif newplace == int(len(newarmysubunit[newrow]) / 2):  # find in new row when loop back to the first one
                            newrow += 1
                        placedone = False
                    else:  # found slot to replace
                        placedone = True
                        break
        else:  # fill in the subunit if the slot is empty
            placedone = True

    oldarmysubunit[replace[0]][replace[1]] = newarmysubunit[newrow][newplace]
    newarmysubunit[newrow][newplace] = leader.subunit.gameid
    newposition = (newplace, newrow)
    return oldarmysubunit, newarmysubunit, newposition


def splitunit(battle, who, how):
    """split parentunit either by row or column into two seperate parentunit"""  # TODO check split when moving
    from gamescript import gameunit, gameleader

    if how == 0:  # split by row
        newarmysubunit = np.array_split(who.armysubunit, 2)[1]
        who.armysubunit = np.array_split(who.armysubunit, 2)[0]
        newpos = pygame.Vector2(who.base_pos[0], who.base_pos[1] + (who.base_height_box / 2))
        newpos = who.rotationxy(who.base_pos, newpos, who.radians_angle)  # new unit pos (back)
        base_pos = pygame.Vector2(who.base_pos[0], who.base_pos[1] - (who.base_height_box / 2))
        who.base_pos = who.rotationxy(who.base_pos, base_pos, who.radians_angle)  # new position for original parentunit (front)
        who.base_height_box /= 2

    else:  # split by column
        newarmysubunit = np.array_split(who.armysubunit, 2, axis=1)[1]
        who.armysubunit = np.array_split(who.armysubunit, 2, axis=1)[0]
        newpos = pygame.Vector2(who.base_pos[0] + (who.base_width_box / 3.3), who.base_pos[1])  # 3.3 because 2 make new unit position overlap
        newpos = who.rotationxy(who.base_pos, newpos, who.radians_angle)  # new unit pos (right)
        base_pos = pygame.Vector2(who.base_pos[0] - (who.base_width_box / 2), who.base_pos[1])
        who.base_pos = who.rotationxy(who.base_pos, base_pos, who.radians_angle)  # new position for original parentunit (left)
        who.base_width_box /= 2
        frontpos = (who.base_pos[0], (who.base_pos[1] - who.base_height_box))  # find new front position of unit
        who.front_pos = who.rotationxy(who.base_pos, frontpos, who.radians_angle)
        who.set_target(who.front_pos)

    if who.leader[1].subunit.gameid not in newarmysubunit.flat:  # move the left sub-general leader subunit if it not in new one
        who.armysubunit, newarmysubunit, newposition = move_leader_subunit(who.leader[1], who.armysubunit, newarmysubunit)
        who.leader[1].subunitpos = newposition[0] * newposition[1]
    who.leader[1].subunit.unit_leader = True  # make the sub-unit of this leader a gamestart leader sub-unit

    alreadypick = []
    for leader in (who.leader[0], who.leader[2], who.leader[3]):  # move other leader subunit to original one if they are in new one
        if leader.subunit.gameid not in who.armysubunit:
            newarmysubunit, who.armysubunit, newposition = move_leader_subunit(leader, newarmysubunit, who.armysubunit, alreadypick)
            leader.subunitpos = newposition[0] * newposition[1]
            alreadypick.append(newposition)

    newleader = [who.leader[1], gameleader.Leader(1, 0, 1, who, battle.leader_stat), gameleader.Leader(1, 0, 2, who, battle.leader_stat),
                 gameleader.Leader(1, 0, 3, who, battle.leader_stat)]  # create new leader list for new parentunit

    who.subunit_position_list = []

    width, height = 0, 0
    subunitnum = 0  # Number of subunit based on the position in row and column
    for subunit in who.armysubunit.flat:
        width += who.imgsize[0]
        who.subunit_position_list.append((width, height))
        subunitnum += 1
        if subunitnum >= len(who.armysubunit[0]):  # Reach the last subunit in the row, go to the next one
            width = 0
            height += who.imgsize[1]
            subunitnum = 0

    # v Sort so the new leader subunit position match what set before
    subunitsprite = [subunit for subunit in who.subunit_sprite if subunit.gameid in newarmysubunit.flat]  # new list of sprite not sorted yet
    new_subunit_sprite = []
    for thisid in newarmysubunit.flat:
        for subunit in subunitsprite:
            if thisid == subunit.gameid:
                new_subunit_sprite.append(subunit)

    subunitsprite = [subunit for subunit in who.subunit_sprite if subunit.gameid in who.armysubunit.flat]
    who.subunit_sprite = []
    for thisid in who.armysubunit.flat:
        for subunit in subunitsprite:
            if thisid == subunit.gameid:
                who.subunit_sprite.append(subunit)
    # ^ End sort

    # v Reset position of sub-unit in inspectui for both old and new unit
    for sprite in (who.subunit_sprite, new_subunit_sprite):
        width, height = 0, 0
        subunitnum = 0
        for subunit in sprite:
            width += battle.squadwidth

            if subunitnum >= len(who.armysubunit[0]):
                width = 0
                width += battle.squadwidth
                height += battle.squadheight
                subunitnum = 0

            subunit.inspposition = (width + battle.inspectuipos[0], height + battle.inspectuipos[1])
            subunit.rect = subunit.image.get_rect(topleft=subunit.inspposition)
            subunit.pos = pygame.Vector2(subunit.rect.centerx, subunit.rect.centery)
            subunitnum += 1
    # ^ End reset position

    # v Change the original parentunit stat and sprite
    originalleader = [who.leader[0], who.leader[2], who.leader[3], gameleader.Leader(1, 0, 3, who, battle.leader_stat)]
    for index, leader in enumerate(originalleader):  # Also change army position of all leader in that parentunit
        leader.armyposition = index  # Change army position to new one
        leader.imgposition = leader.baseimgposition[leader.armyposition]
        leader.rect = leader.image.get_rect(center=leader.imgposition)
    teamcommander = who.teamcommander
    who.teamcommander = teamcommander
    who.leader = originalleader

    add_new_unit(battle, who, False)
    # ^ End change original unit

    # v start making new parentunit
    if who.team == 1:
        whosearmy = battle.team1unit
    else:
        whosearmy = battle.team2unit
    newgameid = battle.allunitlist[-1].gameid + 1

    newunit = gameunit.Unitarmy(startposition=newpos, gameid=newgameid, squadlist=newarmysubunit, colour=who.colour,
                                control=who.control, coa=who.coa, commander=False, startangle=who.angle, team=who.team)

    whosearmy.add(newunit)
    newunit.teamcommander = teamcommander
    newunit.leader = newleader
    newunit.subunit_sprite = new_subunit_sprite

    for subunit in newunit.subunit_sprite:
        subunit.parentunit = newunit

    for index, leader in enumerate(newunit.leader):  # Change army position of all leader in new parentunit
        leader.parentunit = newunit  # Set leader parentunit to new one
        leader.armyposition = index  # Change army position to new one
        leader.imgposition = leader.baseimgposition[leader.armyposition]  # Change image pos
        leader.rect = leader.image.get_rect(center=leader.imgposition)
        leader.poschangestat(leader)  # Change stat based on new army position

    add_new_unit(battle, newunit)

    # ^ End making new parentunit


# Other scripts

def playgif(imageset, framespeed=100):
    """framespeed in millisecond"""
    animation = {}
    frames = ["image1.png", "image2.png"]
