import csv
import datetime
import math
import os
import random
import re

import numpy as np
import pygame
import pygame.freetype

from gamescript import commonscript, popup

load_image = commonscript.load_image
load_images = commonscript.load_images
csv_read = commonscript.csv_read

"""This file contains fuctions of various purposes"""

# Default game mechanic value

battlesidecal = (1, 0.5, 0.1, 0.5)  # battlesidecal is for melee combat side modifier
infinity = float("inf")

letterboard = ("a", "b", "c", "d", "e", "f", "g", "h")  # letter according to subunit position in inspect ui similar to chess board
numberboard = ("8", "7", "6", "5", "4", "3", "2", "1")  # same as above
boardpos = []
for dd in numberboard:
    for ll in letterboard:
        boardpos.append(ll + dd)


# Data Loading gamescript

def load_game_data(game):
    """Load various game data and encyclopedia object"""
    import csv
    from pathlib import Path

    main_dir = game.main_dir
    SCREENRECT = game.SCREENRECT
    Soundvolume = game.Soundvolume
    from gamescript import readstat, map, lorebook, weather, drama, battleui
    from gamescript.tactical import faction, unit, \
        subunit, rangeattack, menu, uniteditor

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
    mapfolder =  Path(os.path.join(main_dir, "data", "ruleset", game.ruleset_folder, "map", "custom"))
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

    unit.Unit.status_list = game.troop_data.status_list
    rangeattack.RangeArrow.gamemapheight = game.battlemap_height

    imgs = load_images(game.main_dir, ["ui", "unit_ui"])
    subunit.Subunit.images = imgs
    subunit.Subunit.gamemap = game.battlemap_base  # add gamebattle map to all parentunit class
    subunit.Subunit.gamemapfeature = game.battlemap_feature  # add gamebattle map to all parentunit class
    subunit.Subunit.gamemapheight = game.battlemap_height
    subunit.Subunit.weapon_list = game.allweapon
    subunit.Subunit.armour_list = game.allarmour
    subunit.Subunit.stat_list = game.troop_data

    skill_header = game.troop_data.skill_list_header
    status_header = game.troop_data.status_list_header

    # v Get index of effect column for skill and status
    subunit.Subunit.skill_type = skill_header['Type']
    subunit.Subunit.skill_aoe = skill_header['Area of Effect']
    subunit.Subunit.skill_duration = skill_header['Duration']
    subunit.Subunit.skill_cd = skill_header['Cooldown']
    subunit.Subunit.skill_restriction = skill_header['Restriction']
    subunit.Subunit.skill_condition = skill_header['Condition']
    subunit.Subunit.skill_discipline_req = skill_header['Discipline Requirement']
    subunit.Subunit.skill_stamina_cost = skill_header['Stamina Cost']
    subunit.Subunit.skill_mana_cost = skill_header['Mana Cost']
    subunit.Subunit.skill_melee_attack = skill_header['Melee Attack Effect']
    subunit.Subunit.skill_melee_defence = skill_header['Melee Defence Effect']
    subunit.Subunit.skill_range_defence = skill_header['Ranged Defence Effect']
    subunit.Subunit.skill_speed = skill_header['Speed Effect']
    subunit.Subunit.skill_accuracy = skill_header['Accuracy Effect']
    subunit.Subunit.skill_range = skill_header['Range Effect']
    subunit.Subunit.skill_reload = skill_header['Reload Effect']
    subunit.Subunit.skill_charge = skill_header['Charge Effect']
    subunit.Subunit.skill_charge_defence = skill_header['Charge Defence Bonus']
    subunit.Subunit.skill_hp_regen = skill_header['HP Regeneration Bonus']
    subunit.Subunit.skill_stamina_regen = skill_header['Stamina Regeneration Bonus']
    subunit.Subunit.skill_morale = skill_header['Morale Bonus']
    subunit.Subunit.skill_discipline = skill_header['Discipline Bonus']
    subunit.Subunit.skill_critical = skill_header['Critical Effect']
    subunit.Subunit.skill_damage = skill_header['Damage Effect']
    subunit.Subunit.skill_sight = skill_header['Sight Bonus']
    subunit.Subunit.skill_hide = skill_header['Hidden Bonus']
    subunit.Subunit.skill_status = skill_header['Status']
    subunit.Subunit.skill_staminadmg = skill_header['Stamina Damage']
    subunit.Subunit.skill_moraledmg = skill_header['Morale Damage']
    subunit.Subunit.skill_enemy_status = skill_header['Enemy Status']
    subunit.Subunit.skill_element = skill_header['Element']

    subunit.Subunit.status_effect = status_header['Special Effect']
    subunit.Subunit.status_conflict = status_header['Status Conflict']
    subunit.Subunit.status_duration = status_header['Duration']
    subunit.Subunit.status_melee_attack = status_header['Melee Attack Effect']
    subunit.Subunit.status_melee_defence = status_header['Melee Defence Effect']
    subunit.Subunit.status_range_defence = status_header['Ranged Defence Effect']
    subunit.Subunit.status_armour = status_header['Armour Effect']
    subunit.Subunit.status_speed = status_header['Speed Effect']
    subunit.Subunit.status_accuracy = status_header['Accuracy Effect']
    subunit.Subunit.status_reload = status_header['Reload Effect']
    subunit.Subunit.status_charge = status_header['Charge Effect']
    subunit.Subunit.status_charge_defence = status_header['Charge Defence Bonus']
    subunit.Subunit.status_hp_regen = status_header['HP Regeneration Bonus']
    subunit.Subunit.status_stamina_regen = status_header['Stamina Regeneration Bonus']
    subunit.Subunit.status_morale = status_header['Morale Bonus']
    subunit.Subunit.status_discipline = status_header['Discipline Bonus']
    subunit.Subunit.status_sight = status_header['Sight Bonus']
    subunit.Subunit.status_hide = status_header['Hidden Bonus']
    subunit.Subunit.status_temperature = status_header['Temperature Change']
    # ^ End get index

    uniteditor.Unitbuildslot.images = imgs
    uniteditor.Unitbuildslot.weapon_list = game.allweapon
    uniteditor.Unitbuildslot.armour_list = game.allarmour
    uniteditor.Unitbuildslot.stat_list = game.troop_data

    game.squadwidth, game.squadheight = imgs[0].get_width(), imgs[0].get_height()  # size of subnit image at closest zoom
    # ^ End subunit class

    # v create leader list
    imgs, order = load_images(game.main_dir, ["ruleset", game.ruleset_folder, "leader", "portrait"], loadorder=False, returnorder=True)
    game.leader_stat = readstat.Leaderstat(main_dir, imgs, order, option=game.ruleset_folder)
    # ^ End leader

    # v Game Effect related class
    imgs = load_images(game.main_dir, ["effect"])
    # imgs = []
    # for img in imgsold:
    # x, y = img.get_width(), img.get_height()
    # img = pygame.transform.scale(img, (int(x ), int(y / 2)))
    # imgs.append(img)
    rangeattack.RangeArrow.images = [imgs[0]]
    # ^ End game effect

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
    game.lorebook = lorebook.Lorebook(game, imgs[0])  # encyclopedia sprite
    game.lorenamelist = lorebook.SubsectionList(game, game.lorebook.rect.topleft, imgs[1])

    imgs = load_images(game.main_dir, ["ui", "lorebook_ui", "button"], loadorder=False)
    for index, img in enumerate(imgs):
        imgs[index] = pygame.transform.scale(img, (int(img.get_width() * game.width_adjust),
                                                   int(img.get_height() * game.height_adjust)))
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

    # Load all image of ui and icon from folder
    topimage = load_images(game.main_dir, ["ui", "battle_ui"])
    iconimage = load_images(game.main_dir, ["ui", "battle_ui", "topbar_icon"])

    # Army select list ui
    game.unitselector = battleui.ArmySelect((0, 0), topimage[30])
    game.selectscroll = battleui.UIScroller(game.unitselector.rect.topright, topimage[30].get_height(),
                                          game.unitselector.max_row_show)  # scroller for unit select ui

    # Right top bar ui that show rough information of selected battalions
    game.gameui = [
        battleui.GameUI(x=SCREENRECT.width - topimage[0].get_size()[0] / 2, y=topimage[0].get_size()[1] / 2, image=topimage[0],
                      icon=iconimage, uitype="topbar")]
    game.gameui[0].options1 = game.statetext

    game.inspectuipos = [game.gameui[0].rect.bottomleft[0] - game.squadwidth / 1.25,
                         game.gameui[0].rect.bottomleft[1] - game.squadheight / 3]

    # Left top command ui with leader and parentunit behavious button
    iconimage = load_images(game.main_dir, ["ui", "battle_ui", "commandbar_icon"])
    game.gameui.append(battleui.GameUI(x=topimage[1].get_size()[0] / 2, y=(topimage[1].get_size()[1] / 2) + game.unitselector.image.get_height(),
                                     image=topimage[1], icon=iconimage,
                                     uitype="commandbar"))

    # Subunit information card ui
    game.gameui.append(
        battleui.GameUI(x=SCREENRECT.width - topimage[2].get_size()[0] / 2, y=(topimage[0].get_size()[1] * 2.5) + topimage[5].get_size()[1],
                      image=topimage[2], icon="", uitype="unitcard"))
    game.gameui[2].featurelist = game.featurelist  # add terrain feature list name to subunit card

    game.gameui.append(battleui.GameUI(x=SCREENRECT.width - topimage[5].get_size()[0] / 2, y=topimage[0].get_size()[1] * 4,
                                     image=topimage[5], icon="", uitype="unitbox"))  # inspect ui that show subnit in selected parentunit
    # v Subunit shown in inspect ui
    width, height = game.inspectuipos[0], game.inspectuipos[1]
    subunitnum = 0  # Number of subnit based on the position in row and column
    imgsize = (game.squadwidth, game.squadheight)
    game.inspectsubunit = []
    for this_subunit in list(range(0, 64)):
        width += imgsize[0]
        game.inspectsubunit.append(battleui.InspectSubunit((width, height)))
        subunitnum += 1
        if subunitnum == 8:  # Reach the last subnit in the row, go to the next one
            width = game.inspectuipos[0]
            height += imgsize[1]
            subunitnum = 0
    # ^ End subunit shown

    # Time bar ui
    game.timeui = battleui.TimeUI(game.unitselector.rect.topright, topimage[31])
    game.timenumber = battleui.Timer(game.timeui.rect.topleft)  # time number on time ui
    game.speednumber = battleui.SpeedNumber((game.timeui.rect.center[0] + 40, game.timeui.rect.center[1]),
                                          1)  # game speed number on the time ui

    image = pygame.Surface((topimage[31].get_width(), 15))
    game.scaleui = battleui.ScaleUI(game.timeui.rect.bottomleft, image)

    # Button related to subunit card and command
    game.buttonui = [battleui.UIButton(game.gameui[2].x - 152, game.gameui[2].y + 10, topimage[3], 0),  # subunit card description button
                     battleui.UIButton(game.gameui[2].x - 152, game.gameui[2].y - 70, topimage[4], 1),  # subunit card stat button
                     battleui.UIButton(game.gameui[2].x - 152, game.gameui[2].y - 30, topimage[7], 2),  # subunit card skill button
                     battleui.UIButton(game.gameui[2].x - 152, game.gameui[2].y + 50, topimage[22], 3),  # subunit card equipment button
                     battleui.UIButton(game.gameui[0].x - 206, game.gameui[0].y - 1, topimage[6], 1),  # unit inspect open/close button
                     battleui.UIButton(game.gameui[1].x - 115, game.gameui[1].y + 26, topimage[8], 0),  # split by middle coloumn button
                     battleui.UIButton(game.gameui[1].x - 115, game.gameui[1].y + 56, topimage[9], 1),  # split by middle row button
                     battleui.UIButton(game.gameui[1].x + 100, game.gameui[1].y + 56, topimage[14], 1)]  # decimation button

    # Behaviour button that once click switch to other mode for subunit behaviour
    game.switch_button = [battleui.SwitchButton(game.gameui[1].x - 40, game.gameui[1].y + 96, topimage[10:14]),  # skill condition button
                          battleui.SwitchButton(game.gameui[1].x - 80, game.gameui[1].y + 96, topimage[15:17]),  # fire at will button
                          battleui.SwitchButton(game.gameui[1].x, game.gameui[1].y + 96, topimage[17:20]),  # behaviour button
                          battleui.SwitchButton(game.gameui[1].x + 40, game.gameui[1].y + 96, topimage[20:22]),  # shoot range button
                          battleui.SwitchButton(game.gameui[1].x - 125, game.gameui[1].y + 96, topimage[35:38]),  # arcshot button
                          battleui.SwitchButton(game.gameui[1].x + 80, game.gameui[1].y + 96, topimage[38:40]),  # toggle run button
                          battleui.SwitchButton(game.gameui[1].x + 120, game.gameui[1].y + 96, topimage[40:43])]  # toggle melee mode

    game.eventlog = battleui.EventLog(topimage[23], (0, SCREENRECT.height))

    game.logscroll = battleui.UIScroller(game.eventlog.rect.topright, topimage[23].get_height(), game.eventlog.max_row_show)  # event log scroller
    game.eventlog.logscroll = game.logscroll  # Link scroller to ui since it is easier to do here with the current order
    subunit.Subunit.eventlog = game.eventlog  # Assign eventlog to subunit class to broadcast event to the log

    game.buttonui.append(battleui.UIButton(game.eventlog.pos[0] + (topimage[24].get_width() / 2),
                                         game.eventlog.pos[1] - game.eventlog.image.get_height() - (topimage[24].get_height() / 2), topimage[24],
                                         0))  # troop tab log button

    game.buttonui += [battleui.UIButton(game.buttonui[8].pos[0] + topimage[24].get_width(), game.buttonui[8].pos[1], topimage[25], 1),
                      # army tab log button
                      battleui.UIButton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 2), game.buttonui[8].pos[1], topimage[26], 2),
                      # leader tab log button
                      battleui.UIButton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 3), game.buttonui[8].pos[1], topimage[27], 3),
                      # subunit tab log button
                      battleui.UIButton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 5), game.buttonui[8].pos[1], topimage[28], 4),
                      # delete current tab log button
                      battleui.UIButton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 6), game.buttonui[8].pos[1], topimage[29], 5),
                      # delete all log button
                      battleui.UIButton(game.timeui.rect.center[0] - 30, game.timeui.rect.center[1], topimage[32], 0),  # time pause button
                      battleui.UIButton(game.timeui.rect.center[0], game.timeui.rect.center[1], topimage[33], 1),  # time decrease button
                      battleui.UIButton(game.timeui.rect.midright[0] - 60, game.timeui.rect.center[1], topimage[34], 2)]  # time increase button

    game.screen_button_list = game.buttonui[8:17]  # event log and time buttons
    game.unitcard_button = game.buttonui[0:4]
    game.inspectbutton = game.buttonui[4]
    game.col_split_button = game.buttonui[5]  # parentunit split by column button
    game.row_split_button = game.buttonui[6]  # parentunit split by row button

    game.timebutton = game.buttonui[14:17]
    game.battleui.add(game.buttonui[8:17])
    game.battleui.add(game.logscroll, game.selectscroll)

    battleui.SelectedSquad.image = topimage[-1]  # subunit border image always the last one
    game.inspect_selected_border = battleui.SelectedSquad((15000, 15000))  # yellow border on selected subnit in inspect ui
    game.mainui.remove(game.inspect_selected_border)  # remove subnit border sprite from gamestart menu drawer
    game.terraincheck = popup.TerrainPopup()  # popup box that show terrain information when right click on map
    game.button_name_popup = popup.OnelinePopup()  # popup box that show button name when mouse over
    game.leader_popup = popup.OnelinePopup()  # popup box that show leader name when mouse over
    game.effect_popup = popup.EffecticonPopup()  # popup box that show skill/trait/status name when mouse over

    drama.TextDrama.SCREENRECT = SCREENRECT
    game.textdrama = drama.TextDrama()  # messege at the top of screen that show up for important event

    game.fpscount = battleui.FPScount()  # FPS number counter

    game.battledone_box = battleui.BattleDone(game, topimage[-3], topimage[-4])
    game.gamedone_button = battleui.UIButton(game.battledone_box.pos[0], game.battledone_box.boximage.get_height() * 0.8, topimage[-2], newlayer=19)
    # ^ End game ui

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
    game.escslidermenu = [menu.Escslider(sliderimage[0], sliderimage[1:3],
                                             (menurectcenter0 * 1.1, menurectcenter1), Soundvolume, 0)]
    game.escvaluebox = [menu.Escvaluebox(sliderimage[3], (game.battle_menu.rect.topright[0] * 1.2, menurectcenter1), Soundvolume)]
    # ^ End esc menu objects

# Other gamebattle gamescript

def convert_str_time(event):
    for index, item in enumerate(event):
        newtime = datetime.datetime.strptime(item[1], "%H:%M:%S").time()
        newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
        event[index] = [item[0], newtime]
        if len(item) == 3:
            event[index].append(item[2])

# Battle Start related gamescript


def add_unit(subunitlist, position, gameid, colour, leaderlist, leaderstat, control, coa, command, startangle, starthp, startstamina, team):
    """Create batalion object into the battle and leader of the parentunit"""
    from gamescript.tactical import unit, leader
    oldsubunitlist = subunitlist[~np.all(subunitlist == 0, axis=1)]  # remove whole empty column in subunit list
    subunitlist = oldsubunitlist[:, ~np.all(oldsubunitlist == 0, axis=0)]  # remove whole empty row in subunit list
    unit = unit.Unit(position, gameid, subunitlist, colour, control, coa, command, abs(360 - startangle), starthp, startstamina, team)

    # add leader
    unit.leader = [leader.Leader(leaderlist[0], leaderlist[4], 0, unit, leaderstat),
                   leader.Leader(leaderlist[1], leaderlist[5], 1, unit, leaderstat),
                   leader.Leader(leaderlist[2], leaderlist[6], 2, unit, leaderstat),
                   leader.Leader(leaderlist[3], leaderlist[7], 3, unit, leaderstat)]
    return unit


def generate_unit(gamebattle, whicharmy, row, control, command, colour, coa, subunitgameid):
    """generate unit data into game object
    row[1:9] is subunit troop id array, row[9][0] is leader id and row[9][1] is position of sub-unt the leader located in"""
    from gamescript.tactical import unit, subunit
    this_unit = add_unit(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                    colour, row[10] + row[11], gamebattle.leader_stat, control,
                    coa, command, row[13], row[14], row[15], row[16])
    whicharmy.add(this_unit)
    armysubunitindex = 0  # armysubunitindex is list index for subunit list in a specific army

    # v Setup subunit in unit to subunit group
    row, column = 0, 0
    maxcolumn = len(this_unit.armysubunit[0])
    for subunitnum in np.nditer(this_unit.armysubunit, op_flags=["readwrite"], order="C"):
        if subunitnum != 0:
            addsubunit = subunit.Subunit(subunitnum, subunitgameid, this_unit, this_unit.subunit_position_list[armysubunitindex],
                                             this_unit.starthp, this_unit.startstamina, gamebattle.unitscale)
            gamebattle.subunit.add(addsubunit)
            addsubunit.board_pos = boardpos[armysubunitindex]
            subunitnum[...] = subunitgameid
            this_unit.subunit_sprite_array[row][column] = addsubunit
            this_unit.subunit_sprite.append(addsubunit)
            subunitgameid += 1
        else:
            this_unit.subunit_sprite_array[row][column] = None  # replace numpy None with python None

        column += 1
        if column == maxcolumn:
            column = 0
            row += 1
        armysubunitindex += 1
    gamebattle.troop_number_sprite.add(unit.TroopNumber(gamebattle, this_unit))  # create troop number text sprite

    return subunitgameid


def unitsetup(gamebattle):
    """read parentunit from unit_pos(source) file and create object with addunit function"""
    main_dir = gamebattle.main_dir
    # defaultunit = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
    # [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])

    teamcolour = gamebattle.teamcolour
    teamarmy = (gamebattle.team0unit, gamebattle.team1unit, gamebattle.team2unit)

    with open(os.path.join(main_dir, "data", "ruleset", gamebattle.ruleset_folder, "map",
                                      gamebattle.mapselected, gamebattle.source, "unit_pos.csv"), encoding="utf-8", mode="r") as unitfile:
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
            subunitgameid = generate_unit(gamebattle, whicharmy, row, control, command, colour, coa, subunitgameid)
            # ^ End subunit setup

    unitfile.close()


def convertedit_unit(gamebattle, whicharmy, row, colour, coa, subunitgameid):
    for n, i in enumerate(row):
        if type(i) == str and i.isdigit():
            row[n] = int(i)
        if n in range(1, 12):
            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
    subunitgameid = generate_unit(gamebattle, whicharmy, row, True, True, colour, coa, subunitgameid)


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


def losscal(attacker, defender, hit, defence, dmgtype, defside=None):
    """Calculate dmg, type 0 is melee attack and will use attacker subunit stat,
    type that is not 0 will use the type object stat instead (mostly used for range attack)"""
    who = attacker
    target = defender

    heightadventage = who.height - target.height
    if dmgtype != 0:
        heightadventage = int(heightadventage / 2)  # Range attack use less height advantage
    hit += heightadventage

    if defence < 0 or who.ignore_def:  # Ignore def trait
        defence = 0

    hitchance = hit - defence
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

    if combatscore > 0:
        leaderdmgbonus = 0
        if who.leader is not None:
            leaderdmgbonus = who.leader.combat  # Get extra dmg from leader combat stat

        if dmgtype == 0:  # Melee dmg
            dmg = random.uniform(who.dmg[0], who.dmg[1])
            if who.chargeskill in who.skill_effect:  # Include charge in dmg if attacking
                if who.ignore_chargedef is False:  # Ignore charge defence if have ignore trait
                    sidecal = battlesidecal[defside]
                    if target.fulldef or target.temp_fulldef:  # defence all side
                        sidecal = 1
                    dmg = dmg + ((who.charge - (target.chargedef * sidecal)) * 2)
                    if (target.chargedef * sidecal) >= who.charge / 2:
                        who.charge_momentum = 1  # charge get stopped by charge def
                    else:
                        who.charge_momentum -= (target.chargedef * sidecal) / who.charge
                else:
                    dmg = dmg + (who.charge * 2)
                    who.charge_momentum -= 1 / who.charge

            if target.chargeskill in target.skill_effect:  # Also include chargedef in dmg if enemy charging
                if target.ignore_chargedef is False:
                    chargedefcal = who.chargedef - target.charge
                    if chargedefcal < 0:
                        chargedefcal = 0
                    dmg = dmg + (chargedefcal * 2)  # if charge def is higher than enemy charge then deal back addtional dmg
            elif who.chargeskill not in who.skill_effect:  # not charging or defend from charge, use attack speed roll
                dmg += sum([random.uniform(who.dmg[0], who.dmg[1]) for x in range(who.meleespeed)])

            penetrate = who.melee_penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmg * penetrate * combatscore

        else:  # Range Damage
            penetrate = dmgtype.penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmgtype.dmg * penetrate * combatscore

        leaderdmg = dmg
        unitdmg = (dmg * who.troop_number) + leaderdmgbonus  # dmg on subunit is dmg multiply by troop number with addition from leader combat
        if (who.anti_inf and target.subunit_type in (1, 2)) or (who.anti_cav and target.subunit_type in (4, 5, 6, 7)):  # Anti trait dmg bonus
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
    else:  # complete miss
        unitdmg = 0
        leaderdmg = 0
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
                for this_subunit in corner_enemy_apply:
                    if this_subunit != 0:
                        this_subunit.status_effect[status[0]] = statuslist[status[0]].copy()
        elif status[1] == 3:  # whole parentunit aoe
            for this_subunit in receiver.parentunit.subunit_sprite:
                if this_subunit.state != 100:
                    this_subunit.status_effect[status[0]] = statuslist[status[0]].copy()


def complexdmg(attacker, receiver, dmg, moraledmg, leaderdmg, dmgeffect, timermod):
    final_dmg = round(dmg * dmgeffect * timermod)
    final_moraledmg = round(moraledmg * dmgeffect * timermod)
    if final_dmg > receiver.unit_health:  # dmg cannot be higher than remaining health
        final_dmg = receiver.unit_health

    receiver.unit_health -= final_dmg
    health_check = 0.1
    if receiver.max_health != infinity:
        health_check = 1 - (receiver.unit_health / receiver.max_health)
    receiver.base_morale -= (final_moraledmg + attacker.bonus_morale_dmg) * receiver.mental * health_check
    receiver.stamina -= attacker.bonus_stamina_dmg

    # v Add red corner to indicate combat
    if receiver.red_border is False:
        receiver.imageblock.blit(receiver.images[11], receiver.corner_image_rect)
        receiver.red_border = True
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
    whodefence = float(attacker.meleedef * whopercent) + wholuck
    targethit = float(attacker.attack * targetpercent) + targetluck
    targetdefence = float(target.meleedef * targetpercent) + targetluck

    """33 backstabber ignore def when attack rear side, 55 Oblivious To Unexpected can't defend from rear at all"""
    if (attacker.backstab and targetside == 2) or (target.oblivious and targetside == 2) or (
            target.flanker and attackerside in (1, 3)):  # Apply only for attacker
        targetdefence = 0

    whodmg, whomoraledmg, wholeaderdmg = losscal(attacker, target, whohit, targetdefence, 0, targetside)  # get dmg by attacker
    targetdmg, targetmoraledmg, targetleaderdmg = losscal(target, attacker, targethit, whodefence, 0, attackerside)  # get dmg by defender

    timermod = combattimer / 0.5  # Since the update happen anytime more than 0.5 second, high speed that pass by longer than x1 speed will become inconsistent
    complexdmg(attacker, target, whodmg, whomoraledmg, wholeaderdmg, dmgeffect, timermod)  # Inflict dmg to defender
    complexdmg(target, attacker, targetdmg, targetmoraledmg, targetleaderdmg, targetdmgeffect, timermod)  # Inflict dmg to attacker

    # v Attack corner (side) of self with aoe attack
    if attacker.corner_atk:
        listloop = [target.nearby_subunit_list[2], target.nearby_subunit_list[5]]  # Side attack get (2) front and (5) rear nearby subunit
        if targetside in (0, 2):
            listloop = target.nearby_subunit_list[0:2]  # Front/rear attack get (0) left and (1) right nearbysubunit
        for this_subunit in listloop:
            if this_subunit != 0 and this_subunit.state != 100:
                targethit, targetdefence = float(attacker.attack * targetpercent) + targetluck, float(this_subunit.meleedef * targetpercent) + targetluck
                whodmg, whomoraledmg = losscal(attacker, this_subunit, whohit, targetdefence, 0)
                complexdmg(attacker, this_subunit, whodmg, whomoraledmg, wholeaderdmg, dmgeffect, timermod)
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
                for this_subunit in army.subunit_sprite:
                    this_subunit.base_morale -= 30

        for thisarmy in enemygroup:  # get bonus authority to the another army
            thisarmy.authority += 5

        for thisarmy in group:  # morale dmg to every subunit in army when allied parentunit destroyed
            for this_subunit in thisarmy.subunit_sprite:
                this_subunit.base_morale -= 20

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
        for this_subunit in self.nearby_subunit_list:
            if this_subunit != 0 and this_subunit.state not in checkstate and this_subunit.leader is None:
                this_subunit.leader = self.leader
                self.leader.subunit = this_subunit
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
            for index, this_subunit in enumerate(self.parentunit.subunit_sprite):
                if this_subunit.state not in checkstate and this_subunit.leader is None:
                    this_subunit.leader = self.leader
                    self.leader.subunit = this_subunit
                    this_subunit.leader.subunitpos = index
                    self.leader = None
                    if self.unit_leader:  # set leader subunit to new one
                        self.parentunit.leadersubunit = this_subunit
                        this_subunit.unit_leader = True

                    break

            if self.leader is not None and event == "die":  # Still can't find new subunit so leader disappear with chance of different result
                self.leader.state = random.randint(97, 100)  # captured, retreated, wounded, dead
                self.leader.health = 0
                self.leader.gone()

        self.unit_leader = False


def add_new_unit(gamebattle, who, addunitlist=True):
    from gamescript.tactical import unit
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

    for index, this_subunit in enumerate(who.subunit_sprite):  # reset leader subunitpos
        if this_subunit.leader is not None:
            this_subunit.leader.subunitpos = index

    who.zoom = 11 - gamebattle.camerascale
    who.new_angle = who.angle

    who.startset(gamebattle.subunit)
    who.set_target(who.front_pos)

    numberpos = (who.base_pos[0] - who.base_width_box,
                 (who.base_pos[1] + who.base_height_box))
    who.number_pos = who.rotationxy(who.base_pos, numberpos, who.radians_angle)
    who.change_pos_scale()  # find new position for troop number text

    for this_subunit in who.subunit_sprite:
        this_subunit.gamestart(this_subunit.zoom)

    if addunitlist:
        gamebattle.allunitlist.append(who)
        gamebattle.allunitindex.append(who.gameid)

    numberspite = unit.TroopNumber(gamebattle, who)
    gamebattle.troop_number_sprite.add(numberspite)


def move_leader_subunit(this_leader, oldarmysubunit, newarmysubunit, alreadypick=()):
    """oldarmysubunit is armysubunit list that the subunit currently in and need to be move out to the new one (newarmysubunit),
    alreadypick is list of position need to be skipped"""
    replace = [np.where(oldarmysubunit == this_leader.subunit.gameid)[0][0],
               np.where(oldarmysubunit == this_leader.subunit.gameid)[1][0]]  # grab old array position of subunit
    newrow = int((len(newarmysubunit) - 1) / 2)  # set up new row subunit will be place in at the middle at the start
    newplace = int((len(newarmysubunit[newrow]) - 1) / 2)  # setup new column position
    placedone = False  # finish finding slot to place yet

    while placedone is False:
        if this_leader.subunit.parentunit.armysubunit.flat[newrow * newplace] != 0:
            for this_subunit in this_leader.subunit.parentunit.subunit_sprite:
                if this_subunit.gameid == this_leader.subunit.parentunit.armysubunit.flat[newrow * newplace]:
                    if this_subunit.this_leader is not None or (newrow, newplace) in alreadypick:
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
    newarmysubunit[newrow][newplace] = this_leader.subunit.gameid
    newposition = (newplace, newrow)
    return oldarmysubunit, newarmysubunit, newposition


def splitunit(battle, who, how):
    """split parentunit either by row or column into two seperate parentunit"""  # TODO check split when moving
    from gamescript.tactical import unit, leader

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
    for this_leader in (who.leader[0], who.leader[2], who.leader[3]):  # move other leader subunit to original one if they are in new one
        if this_leader.subunit.gameid not in who.armysubunit:
            newarmysubunit, who.armysubunit, newposition = move_leader_subunit(this_leader, newarmysubunit, who.armysubunit, alreadypick)
            this_leader.subunitpos = newposition[0] * newposition[1]
            alreadypick.append(newposition)

    newleader = [who.leader[1], leader.Leader(1, 0, 1, who, battle.leader_stat), leader.Leader(1, 0, 2, who, battle.leader_stat),
                 leader.Leader(1, 0, 3, who, battle.leader_stat)]  # create new leader list for new parentunit

    who.subunit_position_list = []

    width, height = 0, 0
    subunitnum = 0  # Number of subunit based on the position in row and column
    for this_subunit in who.armysubunit.flat:
        width += who.imgsize[0]
        who.subunit_position_list.append((width, height))
        subunitnum += 1
        if subunitnum >= len(who.armysubunit[0]):  # Reach the last subunit in the row, go to the next one
            width = 0
            height += who.imgsize[1]
            subunitnum = 0

    # v Sort so the new leader subunit position match what set before
    subunitsprite = [this_subunit for this_subunit in who.subunit_sprite if this_subunit.gameid in newarmysubunit.flat]  # new list of sprite not sorted yet
    new_subunit_sprite = []
    for thisid in newarmysubunit.flat:
        for this_subunit in subunitsprite:
            if thisid == this_subunit.gameid:
                new_subunit_sprite.append(this_subunit)

    subunitsprite = [this_subunit for this_subunit in who.subunit_sprite if this_subunit.gameid in who.armysubunit.flat]
    who.subunit_sprite = []
    for thisid in who.armysubunit.flat:
        for this_subunit in subunitsprite:
            if thisid == this_subunit.gameid:
                who.subunit_sprite.append(this_subunit)
    # ^ End sort

    # v Reset position of sub-unit in inspectui for both old and new unit
    for sprite in (who.subunit_sprite, new_subunit_sprite):
        width, height = 0, 0
        subunitnum = 0
        for this_subunit in sprite:
            width += battle.squadwidth

            if subunitnum >= len(who.armysubunit[0]):
                width = 0
                width += battle.squadwidth
                height += battle.squadheight
                subunitnum = 0

            this_subunit.inspposition = (width + battle.inspectuipos[0], height + battle.inspectuipos[1])
            this_subunit.rect = this_subunit.image.get_rect(topleft=this_subunit.inspposition)
            this_subunit.pos = pygame.Vector2(this_subunit.rect.centerx, this_subunit.rect.centery)
            subunitnum += 1
    # ^ End reset position

    # v Change the original parentunit stat and sprite
    originalleader = [who.leader[0], who.leader[2], who.leader[3], gameleader.Leader(1, 0, 3, who, battle.leader_stat)]
    for index, this_leader in enumerate(originalleader):  # Also change army position of all leader in that parentunit
        this_leader.armyposition = index  # Change army position to new one
        this_leader.imgposition = this_leader.baseimgposition[this_leader.armyposition]
        this_leader.rect = this_leader.image.get_rect(center=this_leader.imgposition)
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

    newunit = unit.Unit(startposition=newpos, gameid=newgameid, squadlist=newarmysubunit, colour=who.colour,
                            control=who.control, coa=who.coa, commander=False, startangle=who.angle, team=who.team)

    whosearmy.add(newunit)
    newunit.teamcommander = teamcommander
    newunit.leader = newleader
    newunit.subunit_sprite = new_subunit_sprite

    for this_subunit in newunit.subunit_sprite:
        this_subunit.parentunit = newunit

    for index, this_leader in enumerate(newunit.leader):  # Change army position of all leader in new parentunit
        this_leader.parentunit = newunit  # Set leader parentunit to new one
        this_leader.armyposition = index  # Change army position to new one
        this_leader.imgposition = this_leader.baseimgposition[this_leader.armyposition]  # Change image pos
        this_leader.rect = this_leader.image.get_rect(center=this_leader.imgposition)
        this_leader.poschangestat(this_leader)  # Change stat based on new army position

    add_new_unit(battle, newunit)

    # ^ End making new parentunit


# Other scripts

def playgif(imageset, framespeed=100):
    """framespeed in millisecond"""
    animation = {}
    frames = ["image1.png", "image2.png"]
