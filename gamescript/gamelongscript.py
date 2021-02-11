import csv
import datetime
import random
import ast
import re
import numpy as np
import pygame
import pygame.freetype
import os

"""This file contains fuctions of various purposes"""

## Default game mechanic value

battlesidecal = (1, 0.5, 0.1, 0.5)  # battlesidecal is for melee combat side modifier,

## Data Loading gamescript

def load_image(file, subfolder=""):
    """loads an image, prepares it for play"""
    import main
    main_dir = main.main_dir
    thisfile = os.path.join(main_dir, 'data', subfolder, file)
    try:
        surface = pygame.image.load(thisfile).convert_alpha()
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' % (thisfile, pygame.get_error()))
    return surface.convert_alpha()

def load_images(subfolder=[], loadorder=True, returnorder=False):
    """loads all images(files) in folder using loadorder list file use only png file"""
    import main
    main_dir = main.main_dir
    imgs = []
    dirpath = os.path.join(main_dir, 'data')
    if subfolder != []:
        for folder in subfolder:
            dirpath = os.path.join(dirpath, folder)

    if loadorder: # load in the order of load_order file
        loadorderfile = open(dirpath + "/load_order.txt", "r")
        loadorderfile = ast.literal_eval(loadorderfile.read())
        for file in loadorderfile:
            imgs.append(load_image(dirpath + "/" + file))
    else: # load every file
        loadorderfile = [f for f in os.listdir(dirpath) if f.endswith('.' + "png")]  ## read all file
        loadorderfile.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r'[^0-9]|[0-9]+', var)])
        for file in loadorderfile:
            imgs.append(load_image(dirpath + "/" + file))

    if returnorder == False:
        return imgs
    else: # return order of the file as list
        loadorderfile = [int(name.replace(".png", "")) for name in loadorderfile]
        return imgs, loadorderfile

def loadgamedata(game):
    """Load various game data and encyclopedia object"""
    import main
    import csv
    from pathlib import Path

    main_dir = main.main_dir
    SCREENRECT = main.SCREENRECT
    Soundvolume = main.Soundvolume
    from gamescript import gameleader, gamemap, gamelongscript, gamelorebook, gameweather, gamefaction, \
        gameunitstat, gameui, gamefaction, gamebattalion, gamesquad, rangeattack, gamemenu, gamepopup, gamedrama, gameprepare, gameunitedit

    #v Craete feature terrain modifier
    game.featuremod = {}
    with open(main_dir + "/data/map" + '/unit_terrainbonus.csv', 'r') as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        run = 0  # for skipping the first row
        for row in rd:
            for n, i in enumerate(row):
                if run != 0:
                    if n == 12:  # effect list is at column 12
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                        elif i.isdigit():
                            row[n] = [int(i)]

                    elif n in (2, 3, 4, 5, 6, 7):  # other modifer column
                        if i != "":
                            row[n] = float(i) / 100
                        else:  # empty row assign 1.0 default
                            i = 1.0

                    elif i.isdigit() or "-" in i:  # modifer bonus (including negative) in other column
                        row[n] = int(i)

            run += 1
            game.featuremod[row[0]] = row[1:]
    unitfile.close()
    #^ End feature terrain mod

    # v Create weather related class
    game.allweather = csv_read('weather.csv', ['data', 'map', 'weather'])
    weatherlist = [item[0] for item in game.allweather.values()][2:]
    strengthlist = ['Light ', 'Normal ', 'Strong ']
    game.weatherlist = []
    for item in weatherlist:
        for strength in strengthlist:
            game.weatherlist.append(strength+item)
    game.weathermatterimgs = []

    for weather in ('0', '1', '2', '3'):  # Load weather matter sprite image
        imgs = load_images(['map', 'weather', weather], loadorder=False)
        game.weathermatterimgs.append(imgs)

    game.weathereffectimgs = []
    for weather in ('0', '1', '2', '3'):  # Load weather effect sprite image
        imgsold = load_images(['map', 'weather', 'effect', weather], loadorder=False)
        imgs = []
        for img in imgsold:
            img = pygame.transform.scale(img, (SCREENRECT.width, SCREENRECT.height))
            imgs.append(img)
        game.weathereffectimgs.append(imgs)

    imgs = load_images(['map', 'weather', 'icon'], loadorder=False)  # Load weather icon
    gameweather.Weather.images = imgs
    # ^ End weather

    #v Faction class
    gamefaction.Factiondata.main_dir = main_dir
    game.allfaction = gamefaction.Factiondata(option=game.rulesetfolder)
    imgsold = load_images(['ruleset', game.rulesetfolder.strip("/"), 'faction', 'coa'], loadorder=False)  # coa imagelist
    imgs = []
    for img in imgsold:
        imgs.append(img)
    game.coa = imgs
    game.factionlist = [item[0] for item in game.allfaction.factionlist.values()][1:]
    # ^ End faction

    # v create game map texture and their default variables
    game.featurelist = []
    with open(main_dir + "/data/map" + '/unit_terrainbonus.csv', 'r') as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        for row in rd:
            game.featurelist.append(row[1])  # get terrain feature combination name for folder
    unitfile.close()
    game.featurelist = game.featurelist[1:]

    gamemap.Mapfeature.main_dir = main_dir
    gamemap.Mapfeature.featuremod = game.featuremod
    gamemap.Beautifulmap.main_dir = main_dir

    game.battlemapbase = gamemap.Basemap(1)  # create base terrain map
    game.battlemapfeature = gamemap.Mapfeature(1)  # create terrain feature map
    game.battlemapheight = gamemap.Mapheight(1)  # create height map
    game.showmap = gamemap.Beautifulmap(1)

    img = load_image('effect.png', 'map')  # map special effect image
    gamemap.Beautifulmap.effectimage = img
    emptyimage = load_image('empty.png', 'map/texture')  # empty texture image
    maptexture = []
    loadtexturefolder = []
    for feature in game.featurelist:
        loadtexturefolder.append(feature.replace(" ", "").lower())  # convert terrain feature list to lower case with no space
    loadtexturefolder = list(set(loadtexturefolder))  # list of terrian folder to load
    loadtexturefolder = [item for item in loadtexturefolder if item != ""]  # For now remove terrain with no planned name/folder yet
    for index, texturefolder in enumerate(loadtexturefolder):
        imgs = load_images(['map', 'texture', texturefolder], loadorder=False)
        maptexture.append(imgs)
    gamemap.Beautifulmap.textureimages = maptexture
    gamemap.Beautifulmap.loadtexturelist = loadtexturefolder
    gamemap.Beautifulmap.emptyimage = emptyimage
    # ^ End game map

    #v Load map list
    mapfolder = Path(main_dir + '/data/ruleset/' + game.rulesetfolder + '/map')
    subdirectories = [x for x in mapfolder.iterdir() if x.is_dir()]

    for index, map in enumerate(subdirectories):
        if "custom" in str(map): # remove custom from this folder list to load
            subdirectories.pop(index)
            break

    game.maplist = [] # map name list for map selection list
    game.mapfoldername = [] # folder for reading later

    for map in subdirectories:
        game.mapfoldername.append(str(map).split("\\")[-1])
        with open(str(map) + '/info.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[0] != "name":
                    game.maplist.append(row[0])
        unitfile.close()
    #^ End load map list

    #v Load custom map list
    mapfolder = Path(main_dir + '/data/ruleset/' + game.rulesetfolder + '/map/custom/')
    subdirectories = [x for x in mapfolder.iterdir() if x.is_dir()]

    game.mapcustomlist = []
    game.mapcustomfoldername = []

    for map in subdirectories:
        game.mapcustomfoldername.append(str(map).split("\\")[-1])
        with open(str(map) + '/info.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[0] != "name":
                    game.mapcustomlist.append(row[0])
        unitfile.close()
    #^ End load custom map list

    game.statetext = {0: "Idle", 1: "Walking", 2: "Running", 3: "Walk(Melee)", 4: "Run(Melee)", 5: "Walk(Range)", 6: "Run(Range)",
                      7: "Forced Walk", 8: "Forced Run",
                      10: "Fighting", 11: "shooting", 65: "Sleeping", 66: "Camping", 67: "Resting", 68: "Dancing",
                      69: "Partying", 96: "Retreating", 97: "Collapse", 98: "Retreating", 99: "Broken", 100: "Destroyed"}

    # v create unit related class
    imgs = []
    imgsold = load_images(['war', 'unit_ui', 'battalion'])
    for img in imgsold:
        imgs.append(img)
    gamebattalion.Unitarmy.images = imgs

    imgsold = load_images(['war', 'unit_ui', 'weapon'])
    imgs = []
    for img in imgsold:
        x, y = img.get_width(), img.get_height()
        img = pygame.transform.scale(img, (int(x / 1.7), int(y / 1.7)))  # scale 1.7 seem to be most fitting as a placeholder
        imgs.append(img)
    game.allweapon = gameunitstat.Weaponstat(main_dir, imgs, game.ruleset)  # Create weapon class

    imgs = load_images(['war', 'unit_ui', 'armour'])
    game.allarmour = gameunitstat.Armourstat(main_dir, imgs, game.ruleset)  # Create armour class

    game.statusimgs = load_images(['ui', 'status_icon'], loadorder=False)
    game.roleimgs = load_images(['ui', 'role_icon'], loadorder=False)
    game.traitimgs = load_images(['ui', 'trait_icon'], loadorder=False)
    game.skillimgs = load_images(['ui', 'skill_icon'], loadorder=False)

    cooldown = pygame.Surface((game.skillimgs[0].get_width(), game.skillimgs[0].get_height()), pygame.SRCALPHA)
    cooldown.fill((230, 70, 80, 200))  # red colour filter for skill cooldown timer
    gameui.Skillcardicon.cooldown = cooldown

    activeskill = pygame.Surface((game.skillimgs[0].get_width(), game.skillimgs[0].get_height()), pygame.SRCALPHA)
    activeskill.fill((170, 220, 77, 200))  # green colour filter for skill active timer
    gameui.Skillcardicon.activeskill = activeskill

    game.gameunitstat = gameunitstat.Unitstat(main_dir, game.ruleset, game.rulesetfolder)

    gamebattalion.Unitarmy.statuslist = game.gameunitstat.statuslist
    gamebattalion.Unitarmy.gamemap = game.battlemapbase  # add battle map to all battalion class
    gamebattalion.Unitarmy.gamemapfeature = game.battlemapfeature  # add battle map to all battalion class
    gamebattalion.Unitarmy.gamemapheight = game.battlemapheight
    gamebattalion.Hitbox.gamecamera = game.battlecamera
    rangeattack.Rangearrow.gamemapheight = game.battlemapheight

    imgs = load_images(['war', 'unit_ui'])
    gamesquad.Unitsquad.images = imgs
    gamesquad.Unitsquad.weaponlist = game.allweapon
    gamesquad.Unitsquad.armourlist = game.allarmour
    gamesquad.Unitsquad.statlist = game.gameunitstat
    gameunitedit.Armybuildslot.images = imgs
    gameunitedit.Armybuildslot.weaponlist = game.allweapon
    gameunitedit.Armybuildslot.armourlist = game.allarmour
    gameunitedit.Armybuildslot.statlist = game.gameunitstat

    game.squadwidth, game.squadheight = imgs[0].get_width(), imgs[0].get_height()  # size of squad image at closest zoom
    #^ End unit class

    #v create leader list
    imgs, order = load_images(['ruleset', game.rulesetfolder.strip("/"), 'leader', 'portrait'], loadorder=False, returnorder=True)
    game.leaderstat = gameunitstat.Leaderstat(main_dir, imgs, order, option=game.rulesetfolder)
    #^ End leader

    # v Game Effect related class
    imgs = load_images(['effect'])
    # imgs = []
    # for img in imgsold:
    # x, y = img.get_width(), img.get_height()
    # img = pygame.transform.scale(img, (int(x ), int(y / 2)))
    # imgs.append(img)
    rangeattack.Rangearrow.images = [imgs[0]]
    # ^ End game effect

    #v Encyclopedia related objects
    gamelorebook.Lorebook.conceptstat = csv_read('concept_stat.csv', ['data', 'ruleset', game.rulesetfolder.strip("/"), 'lore'])
    gamelorebook.Lorebook.conceptlore = csv_read('concept_lore.csv', ['data', 'ruleset', game.rulesetfolder.strip("/"), 'lore'])
    gamelorebook.Lorebook.historystat = csv_read('history_stat.csv', ['data', 'ruleset', game.rulesetfolder.strip("/"), 'lore'])
    gamelorebook.Lorebook.historylore = csv_read('history_lore.csv', ['data', 'ruleset', game.rulesetfolder.strip("/"), 'lore'])

    gamelorebook.Lorebook.factionlore = game.allfaction.factionlist
    gamelorebook.Lorebook.unitstat = game.gameunitstat.unitlist
    gamelorebook.Lorebook.unitlore = game.gameunitstat.unitlore
    gamelorebook.Lorebook.armourstat = game.allarmour.armourlist
    gamelorebook.Lorebook.weaponstat = game.allweapon.weaponlist
    gamelorebook.Lorebook.mountstat = game.gameunitstat.mountlist
    gamelorebook.Lorebook.mountarmourstat = game.gameunitstat.mountarmourlist
    gamelorebook.Lorebook.statusstat = game.gameunitstat.statuslist
    gamelorebook.Lorebook.skillstat = game.gameunitstat.abilitylist
    gamelorebook.Lorebook.traitstat = game.gameunitstat.traitlist
    gamelorebook.Lorebook.leader = game.leaderstat
    gamelorebook.Lorebook.leaderlore = game.leaderstat.leaderlore
    gamelorebook.Lorebook.terrainstat = game.featuremod
    gamelorebook.Lorebook.weatherstat = game.allweather
    gamelorebook.Lorebook.landmarkstat = None
    gamelorebook.Lorebook.unitgradestat = game.gameunitstat.gradelist
    gamelorebook.Lorebook.unitclasslist = game.gameunitstat.role
    gamelorebook.Lorebook.leaderclasslist = game.leaderstat.leaderclass
    gamelorebook.Lorebook.mountgradestat = game.gameunitstat.mountgradelist
    gamelorebook.Lorebook.racelist = game.gameunitstat.racelist
    gamelorebook.Lorebook.SCREENRECT = SCREENRECT
    gamelorebook.Lorebook.main_dir = main_dir
    gamelorebook.Lorebook.statetext = game.statetext

    imgs = load_images(['ui', 'lorebook_ui'], loadorder=False)
    game.lorebook = gamelorebook.Lorebook(imgs[0])
    game.lorenamelist = gamelorebook.Subsectionlist(game.lorebook.rect.topleft, imgs[1])

    imgs = load_images(['ui', 'lorebook_ui', 'button'], loadorder=False)
    for index, img in enumerate(imgs):
        imgs[index] = pygame.transform.scale(img, (int(img.get_width() * game.widthadjust),
                                                    int(img.get_height() * game.heightadjust)))
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
                        imgs[13], 20, 13),  # previous page button
        gameui.Uibutton(game.lorebook.rect.bottomright[0] - (imgs[14].get_width()), game.lorebook.rect.bottomright[1] - imgs[14].get_height(),
                        imgs[14], 21, 13)]  # next page button
    game.pagebutton = (game.lorebuttonui[12], game.lorebuttonui[13])
    game.lorescroll = gameui.Uiscroller(game.lorenamelist.rect.topright, game.lorenamelist.image.get_height(),
                      game.lorebook.maxsubsectionshow, layer=25)  # add subsection list scroller
    #^ End encyclopedia objects

    # v Create battle game ui objects

    game.minimap = gameui.Minimap((SCREENRECT.width, SCREENRECT.height))

    #Popup Ui
    imgs = load_images(['ui', 'popup_ui', 'terraincheck'], loadorder=False)
    gamepopup.Terrainpopup.images = imgs
    gamepopup.Terrainpopup.SCREENRECT = SCREENRECT
    imgs = load_images(['ui', 'popup_ui', 'dramatext'], loadorder=False)
    gamedrama.Textdrama.images = imgs

    #Load all image of ui and icon from folder
    topimage = load_images(['ui', 'battle_ui'])
    iconimage = load_images(['ui', 'battle_ui', 'topbar_icon'])

    #Army select list ui
    game.armyselector = gameui.Armyselect((0, 0), topimage[30])
    game.selectscroll = gameui.Uiscroller(game.armyselector.rect.topright, topimage[30].get_height(),
                                          game.armyselector.maxrowshow)  # scroller for army select ui

    #Right top bar ui that show rough information of selected battalions
    game.gameui = [
        gameui.Gameui(X=SCREENRECT.width - topimage[0].get_size()[0] / 2, Y=topimage[0].get_size()[1] / 2, image=topimage[0],
                      icon=iconimage, uitype="topbar")]
    game.gameui[0].options1 = game.statetext

    #Left top command ui with leader and battalion behavious button
    iconimage = load_images(['ui', 'battle_ui', 'commandbar_icon'])
    game.gameui.append(gameui.Gameui(X=topimage[1].get_size()[0] / 2, Y=(topimage[1].get_size()[1] / 2) + game.armyselector.image.get_height(),
                                     image=topimage[1], icon=iconimage,
                                     uitype="commandbar"))

    #Squad information card ui
    game.gameui.append(
        gameui.Gameui(X=SCREENRECT.width - topimage[2].get_size()[0] / 2, Y=(topimage[0].get_size()[1] * 2.5) + topimage[5].get_size()[1],
                      image=topimage[2], icon="", uitype="unitcard"))
    game.gameui[2].featurelist = game.featurelist  # add terrain feature list name to unit card

    game.gameui.append(gameui.Gameui(X=SCREENRECT.width - topimage[5].get_size()[0] / 2, Y=topimage[0].get_size()[1] * 4,
                                     image=topimage[5], icon="", uitype="armybox"))  # inspect ui that show squad in selected battalion

    #Time bar ui
    game.timeui = gameui.Timeui(game.armyselector.rect.topright, topimage[31])
    game.timenumber = gameui.Timer(game.timeui.rect.topleft)  # time number on time ui
    game.speednumber = gameui.Speednumber((game.timeui.rect.center[0] + 40, game.timeui.rect.center[1]),
                                          1)  # game speed number on the time ui

    image = pygame.Surface((topimage[31].get_width(), 15))
    game.scaleui = gameui.Scaleui(game.timeui.rect.bottomleft, image)

    #Button related to unit card and command
    game.buttonui = [gameui.Uibutton(game.gameui[2].X - 152, game.gameui[2].Y + 10, topimage[3], 0),  # unit card description button
                     gameui.Uibutton(game.gameui[2].X - 152, game.gameui[2].Y - 70, topimage[4], 1),  # unit card stat button
                     gameui.Uibutton(game.gameui[2].X - 152, game.gameui[2].Y - 30, topimage[7], 2),  # unit card skill button
                     gameui.Uibutton(game.gameui[2].X - 152, game.gameui[2].Y + 50, topimage[22], 3),  # unit card equipment button
                     gameui.Uibutton(game.gameui[0].X - 206, game.gameui[0].Y - 1, topimage[6], 1),  # army inspect open/close button
                     gameui.Uibutton(game.gameui[1].X - 115, game.gameui[1].Y + 26, topimage[8], 0),  # split by middle coloumn button
                     gameui.Uibutton(game.gameui[1].X - 115, game.gameui[1].Y + 56, topimage[9], 1),  # split by middle row button
                     gameui.Uibutton(game.gameui[1].X + 100, game.gameui[1].Y + 56, topimage[14], 1)]  # decimation button

    #Behaviour button that once click switch to other mode for unit behaviour
    game.switchbuttonui = [gameui.Switchuibutton(game.gameui[1].X - 30, game.gameui[1].Y + 96, topimage[10:14]),  # skill condition button
                           gameui.Switchuibutton(game.gameui[1].X - 70, game.gameui[1].Y + 96, topimage[15:17]),  # fire at will button
                           gameui.Switchuibutton(game.gameui[1].X, game.gameui[1].Y + 96, topimage[17:20]),  # behaviour button
                           gameui.Switchuibutton(game.gameui[1].X + 40, game.gameui[1].Y + 96, topimage[20:22]),  # shoot range button
                           gameui.Switchuibutton(game.gameui[1].X - 115, game.gameui[1].Y + 96, topimage[35:38]),  # arcshot button
                           gameui.Switchuibutton(game.gameui[1].X + 80, game.gameui[1].Y + 96, topimage[38:40])]  # toggle run button

    game.eventlog = gameui.Eventlog(topimage[23], (0, SCREENRECT.height))

    game.logscroll = gameui.Uiscroller(game.eventlog.rect.topright, topimage[23].get_height(), game.eventlog.maxrowshow)  # event log scroller
    game.eventlog.logscroll = game.logscroll  # Link scroller to ui since it is easier to do here with the current order
    gamesquad.Unitsquad.eventlog = game.eventlog  # Assign eventlog to unit class to broadcast event to the log

    game.buttonui.append(gameui.Uibutton(game.eventlog.pos[0] + (topimage[24].get_width() / 2),
                                         game.eventlog.pos[1] - game.eventlog.image.get_height() - (topimage[24].get_height() / 2), topimage[24],
                                         0))  # war tab log button

    game.buttonui += [gameui.Uibutton(game.buttonui[8].pos[0] + topimage[24].get_width(), game.buttonui[8].pos[1], topimage[25], 1),
                      # army tab log button
                      gameui.Uibutton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 2), game.buttonui[8].pos[1], topimage[26], 2),
                      # leader tab log button
                      gameui.Uibutton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 3), game.buttonui[8].pos[1], topimage[27], 3),
                      # unit tab log button
                      gameui.Uibutton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 5), game.buttonui[8].pos[1], topimage[28], 4),
                      # delete current tab log button
                      gameui.Uibutton(game.buttonui[8].pos[0] + (topimage[24].get_width() * 6), game.buttonui[8].pos[1], topimage[29], 5),
                      # delete all log button
                      gameui.Uibutton(game.timeui.rect.center[0] - 30, game.timeui.rect.center[1], topimage[32], 0),  # time pause button
                      gameui.Uibutton(game.timeui.rect.center[0], game.timeui.rect.center[1], topimage[33], 1),  # time decrease button
                      gameui.Uibutton(game.timeui.rect.midright[0] - 60, game.timeui.rect.center[1], topimage[34], 2)]  # time increase button

    game.screenbuttonlist = game.buttonui[8:17]
    game.unitcardbutton = game.buttonui[0:4]
    game.inspectbutton = game.buttonui[4]
    game.colsplitbutton = game.buttonui[5]  # battalion split by column button
    game.rowsplitbutton = game.buttonui[6]  # battalion split by row button

    game.timebutton = game.buttonui[14:17]
    game.battleui.add(game.buttonui[8:17])
    game.battleui.add(game.logscroll, game.selectscroll)

    gameui.Selectedsquad.image = topimage[-1]
    game.squadselectedborder = gameui.Selectedsquad((15000,15000)) #yellow border on selected squad in inspect ui
    game.mainui.remove(game.squadselectedborder) #remove squad border sprite from main menu drawer
    game.terraincheck = gamepopup.Terrainpopup() #popup box that show terrain information when right click on map
    game.buttonnamepopup = gamepopup.Onelinepopup() #popup box that show button name when mouse over
    game.leaderpopup = gamepopup.Onelinepopup() #popup box that show leader name when mouse over
    game.effectpopup = gamepopup.Effecticonpopup() #popup box that show skill/trait/status name when mouse over

    gamedrama.Textdrama.SCREENRECT = SCREENRECT
    game.textdrama = gamedrama.Textdrama() #messege at the top of screen that show up for important event

    game.fpscount = gameui.FPScount() #FPS number counter
    # ^ End game ui

    # v Esc menu related objects
    imgs = load_images(['ui', 'battlemenu_ui'], loadorder=False)
    gamemenu.Escbox.images = imgs  # Create ESC Menu box
    gamemenu.Escbox.SCREENRECT = SCREENRECT
    game.battlemenu = gamemenu.Escbox()

    buttonimage = load_images(['ui', 'battlemenu_ui', 'button'], loadorder=False)
    menurectcenter0 = game.battlemenu.rect.center[0]
    menurectcenter1 = game.battlemenu.rect.center[1]

    game.battlemenubutton = [
        gamemenu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 - 100), text="Resume", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 - 50), text="Encyclopedia", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1), text="Option", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 + 50), text="Main Menu", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0, menurectcenter1 + 100), text="Desktop", size=14)]

    game.escoptionmenubutton = [
        gamemenu.Escbutton(buttonimage, (menurectcenter0 - 50, menurectcenter1 + 70), text="Confirm", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0 + 50, menurectcenter1 + 70), text="Apply", size=14),
        gamemenu.Escbutton(buttonimage, (menurectcenter0 + 150, menurectcenter1 + 70), text="Cancel", size=14)]

    sliderimage = load_images(['ui', 'battlemenu_ui', 'slider'], loadorder=False)
    game.escslidermenu = [
        gamemenu.Escslidermenu(sliderimage[0], sliderimage[1:3], (menurectcenter0 * 1.1, menurectcenter1), Soundvolume,
                               0)]
    game.escvaluebox = [gamemenu.Escvaluebox(sliderimage[3], (game.battlemenu.rect.topright[0] * 1.2, menurectcenter1), Soundvolume)]
    # ^ End esc menu objects

def createtroopstat(self, team, stat, unitscale, starthp, startstamina):
    """Setup squad troop stat"""
    self.name = stat[0]  # name according to the preset
    self.unitclass = stat[1]  # used to determine whether to use melee or range weapon as icon
    self.grade = stat[2]  # training level/class grade
    self.race = stat[3]  # creature race
    self.trait = stat[4]  # trait list from preset
    self.trait = self.trait + self.statlist.gradelist[self.grade][-1]  # add trait from grade
    skill = stat[5]  # skill list according to the preset
    self.skillcooldown = {}
    self.cost = stat[6]
    self.baseattack = round(stat[8] + int(self.statlist.gradelist[self.grade][1]), 0)  # base melee attack with grade bonus
    self.basemeleedef = round(stat[9] + int(self.statlist.gradelist[self.grade][2]), 0)  # base melee defence with grade bonus
    self.baserangedef = round(stat[10] + int(self.statlist.gradelist[self.grade][2]), 0)  # base range defence with grade bonus
    self.armourgear = stat[11]  # armour equipement
    self.basearmour = self.armourlist.armourlist[self.armourgear[0]][1] \
                      * self.armourlist.quality[self.armourgear[1]]  # Armour stat is cal from based armour * quality
    self.baseaccuracy = stat[12] + int(self.statlist.gradelist[self.grade][4])
    self.basesight = stat[13]  # base sight range
    self.ammo = stat[14]  # amount of ammunition
    self.basereload = stat[15] + int(self.statlist.gradelist[self.grade][5])
    self.reloadtime = 0  # Unit can only refill magazine when reloadtime is equal or more than reload stat
    self.basecharge = stat[16]
    self.basechargedef = 10  # All infantry unit has default 10 charge defence
    self.chargeskill = stat[17]  # For easier reference to check what charge skill this unit has
    self.charging = False  # For checking if battalion in charging state or not for using charge skill
    skill = [self.chargeskill] + skill  # Add charge skill as first item in the list
    self.skill = {x: self.statlist.abilitylist[x].copy() for x in skill if x != 0 and x in self.statlist.abilitylist}  # grab skill stat into dict
    self.troophealth = round(stat[18] * self.statlist.gradelist[self.grade][7])  # Health of each troop
    self.stamina = int(stat[19] * self.statlist.gradelist[self.grade][8] * (startstamina / 100))  # starting stamina with grade
    self.mana = stat[20]  # Resource for magic skill

    # v Weapon stat
    self.meleeweapon = stat[21]  # melee weapon equipment
    self.rangeweapon = stat[22]  # range weapon equipment
    self.dmg = self.weaponlist.weaponlist[self.meleeweapon[0]][1] * self.weaponlist.quality[self.meleeweapon[1]]  # damage for melee
    self.penetrate = 1 - (self.weaponlist.weaponlist[self.meleeweapon[0]][2] * self.weaponlist.quality[
        self.meleeweapon[1]] / 100)  # the lower the number the less effectiveness of enemy armour
    if self.penetrate > 1:
        self.penetrate = 1  # melee penetrate cannot be higher than 1
    elif self.penetrate < 0:
        self.penetrate = 0  # melee penetrate cannot be lower than 0
    self.rangedmg = self.weaponlist.weaponlist[self.rangeweapon[0]][1] * self.weaponlist.quality[self.rangeweapon[1]]  # damage for range
    self.rangepenetrate = 1 - (self.weaponlist.weaponlist[self.rangeweapon[0]][2] * self.weaponlist.quality[self.rangeweapon[1]] / 100)
    self.magazinesize = self.weaponlist.weaponlist[self.rangeweapon[0]][6] # can shoot how many time before have to reload
    self.baserange = int(self.weaponlist.weaponlist[self.rangeweapon[0]][7] * self.weaponlist.quality[self.rangeweapon[1]]) # base weapon range depend on weapon range stat and quality
    self.trait = self.trait + self.weaponlist.weaponlist[self.meleeweapon[0]][4]  # apply trait from range weapon
    self.trait = self.trait + self.weaponlist.weaponlist[self.rangeweapon[0]][4]  # apply trait from melee weapon
    if self.rangepenetrate > 1:
        self.rangepenetrate = 1  # range penetrate cannot be higher than 1
    elif self.rangepenetrate < 0:
        self.rangepenetrate = 0  # range penetrate cannot be lower than 0
    # ^ End weapon stat

    self.basemorale = int(stat[23] + int(self.statlist.gradelist[self.grade][9]))  # morale with grade bonus
    self.basediscipline = int(stat[24] + int(self.statlist.gradelist[self.grade][10]))  # discilpline with grade bonus
    self.mental = stat[25] + int(self.statlist.gradelist[self.grade][11]) # mental resistance from morale damage and mental status effect
    self.troopnumber = int(stat[27] * unitscale[team - 1] * starthp / 100)  # number of starting troop, team -1 to become list index
    self.basespeed = 50  # All infantry has base speed at 50
    self.unittype = stat[28] - 1  # 0 is melee infantry and 1 is range for command buff
    self.featuremod = 1  # the starting column in unit_terrainbonus of infantry

    # v Mount stat
    self.mount = self.statlist.mountlist[stat[29][0]]  # mount this squad use
    self.mountgrade = self.statlist.mountgradelist[stat[29][1]]
    self.mountarmour = self.statlist.mountarmourlist[stat[29][2]]
    if stat[29][0] != 1:  # have mount, add mount stat with its grade to unit stat
        self.basechargedef = 5  # charge defence only 5 for cav
        self.basespeed = (self.mount[1] + self.mountgrade[1])  # use mount base speed instead
        self.troophealth += (self.mount[2] * self.mountgrade[3]) + self.mountarmour[1]  # Add mount health to the troop health
        self.basecharge += (self.mount[3] + self.mountgrade[2])  # Add charge power of mount to troop
        self.stamina += self.mount[4]
        self.trait = self.trait + self.mount[6]  # Apply mount trait to unit
        self.unittype = 2  # If unit has mount, count as cav for command buff
        self.featuremod = 4  # the starting column in unit_terrainbonus of cavalry
    # ^ End mount stat

    self.weight = self.weaponlist.weaponlist[stat[21][0]][3] + self.weaponlist.weaponlist[stat[22][0]][3] + \
                  self.armourlist.armourlist[stat[11][0]][2] + self.mountarmour[2]  # Weight from both melee and range weapon and armour
    self.trait = self.trait + self.armourlist.armourlist[stat[11][0]][4]  # Apply armour trait to unit
    self.basespeed = round((self.basespeed * ((100 - self.weight) / 100)) + int(self.statlist.gradelist[self.grade][3]),
                           0)  # finalise base speed with weight and grade bonus
    self.description = stat[-1]  # squad description for inspect ui
    # if self.hidden

    # v Elemental stat
    self.baseelemmelee = 0  # start with physical element for melee weapon
    self.baseelemrange = 0  # start with physical for range weapon
    self.elemcount = [0, 0, 0, 0, 0]  # Elemental threshold count in this order fire,water,air,earth,poison
    self.tempcount = 0  # Temperature threshold count
    fireres = 0  # resistance to fire, will be combine into list
    waterres = 0  # resistance to water, will be combine into list
    airres = 0  # resistance to air, will be combine into list
    earthres = 0  # resistance to earth, will be combine into list
    self.magicres = 0  # Resistance to any magic
    self.heatres = 0  # Resistance to heat temperature
    self.coldres = 0  # Resistance to cold temperature
    poisonres = 0  # resistance to poison, will be combine into list
    # ^ End elemental

    self.criteffect = 1  # critical extra modifier
    self.frontdmgeffect = 1  # Some skill affect only frontal combat damage
    self.sidedmgeffect = 1  # Some skill affect damage for side combat as well (AOE)
    self.corneratk = False  # Check if squad can attack corner enemy or not
    self.flankbonus = 1  # Combat bonus when flanking
    self.baseauthpenalty = 0.1  # penalty to authority when bad event happen
    self.bonusmoraledmg = 0  # extra morale damage
    self.bonusstaminadmg = 0  # extra stamina damage
    self.authpenalty = 0.1  # authority penalty for certain activities/order
    self.basehpregen = 0  # hp regeneration modifier, will not resurrect dead troop by default
    self.basestaminaregen = 2  # stamina regeneration modifier
    self.moraleregen = 2  # morale regeneration modifier
    self.statuseffect = {}  # list of current status effect
    self.skilleffect = {}  # list of activate skill effect
    self.baseinflictstatus = {}  # list of status that this squad will inflict to enemy when attack
    self.specialstatus = []

    # v Set up trait variable
    self.arcshot = False
    self.antiinf = False
    self.anticav = False
    self.shootmove = False
    self.agileaim = False
    self.norangepenal = False
    self.longrangeacc = False
    self.ignorechargedef = False
    self.ignoredef = False
    self.fulldef = False
    self.tempfulldef = False
    self.backstab = False
    self.oblivious = False
    self.flanker = False
    self.unbreakable = False
    self.tempunbraekable = False
    self.stationplace = False
    # ^ End setup trait variable

    # v Add trait to base stat
    self.trait = list(set([trait for trait in self.trait if trait != 0]))
    if len(self.trait) > 0:
        self.trait = {x: self.statlist.traitlist[x] for x in self.trait if
                      x in self.statlist.traitlist}  # Any trait not available in ruleset will be ignored
        for trait in self.trait.values():  # add trait modifier to base stat
            self.baseattack *= trait[3]
            self.basemeleedef *= trait[4]
            self.baserangedef *= trait[5]
            self.basearmour += trait[6]
            self.basespeed *= trait[7]
            self.baseaccuracy *= trait[8]
            self.baserange *= trait[9]
            self.basereload *= trait[10]
            self.basecharge *= trait[11]
            self.basechargedef += trait[12]
            self.basehpregen += trait[13]
            self.basestaminaregen += trait[14]
            self.basemorale += trait[15]
            self.basediscipline += trait[16]
            self.criteffect += trait[17]
            fireres += (trait[21] / 100)  # percentage, 1 mean perfect resistance, 0 mean none
            waterres += (trait[22] / 100)
            airres += (trait[23] / 100)
            earthres += (trait[24] / 100)
            self.magicres += (trait[25] / 100)
            self.heatres += (trait[26] / 100)
            self.coldres += (trait[27] / 100)
            poisonres += (trait[28] / 100)
            self.mental += trait[31]
            if trait[32] != [0]:
                for effect in trait[32]:
                    self.baseinflictstatus[effect] = trait[1]
            # self.baseelemmelee =
            # self.baseelemrange =

        if 3 in self.trait:  # Varied training
            self.baseattack *= (random.randint(80, 120) / 100)
            self.basemeleedef *= (random.randint(80, 120) / 100)
            self.baserangedef *= (random.randint(80, 120) / 100)
            # self.basearmour *= (random.randint(80, 120) / 100)
            self.basespeed *= (random.randint(80, 120) / 100)
            self.baseaccuracy *= (random.randint(80, 120) / 100)
            # self.baserange *= (random.randint(80, 120) / 100)
            self.basereload *= (random.randint(80, 120) / 100)
            self.basecharge *= (random.randint(80, 120) / 100)
            self.basechargedef *= (random.randint(80, 120) / 100)
            self.basemorale += random.randint(-10, 10)
            self.basediscipline += random.randint(-10, 10)
            self.mental += random.randint(-10, 10)

        if 149 in self.trait:  # Impetuous
            self.baseauthpenalty += 0.5

        # v Change trait variable
        if 16 in self.trait: self.arcshot = True  # can shoot in arc
        if 17 in self.trait: self.agileaim = True  # gain bonus accuracy when shoot while moving
        if 18 in self.trait: self.shootmove = True  # can shoot and move at same time
        if 29 in self.trait: self.ignorechargedef = True  # ignore charge defence completely
        if 30 in self.trait: self.ignoredef = True  # ignore defence completely
        if 34 in self.trait: self.fulldef = True  # full effective defence for all side
        if 33 in self.trait: self.backstab = True  # bonus on rear attack
        if 47 in self.trait: self.flanker = True  # bonus on flank attack
        if 55 in self.trait: self.oblivious = True  # more penalty on flank/rear defend
        if 73 in self.trait: self.norangepenal = True  # no range penalty
        if 74 in self.trait: self.longrangeacc = True  # less range penalty

        if 111 in self.trait:
            self.unbreakable = True  # always unbreakable
            self.tempunbraekable = True
        # ^ End change trait variable
    # ^ End add trait to stat

    # self.loyalty
    self.elemresist = (fireres, waterres, airres, earthres, poisonres)  # list of elemental resistance
    self.maxstamina, self.stamina75, self.stamina50, self.stamina25, = self.stamina, round(self.stamina * 0.75), round(
        self.stamina * 0.5), round(self.stamina * 0.25)
    self.unithealth = self.troophealth * self.troopnumber  # Total health of unit from all troop
    self.lasthealthstate = 4  # state start at full
    self.laststaminastate = 4

    self.basereload = self.weaponlist.weaponlist[self.rangeweapon[0]][5] + \
                      ((self.basereload - 50) * self.weaponlist.weaponlist[self.rangeweapon[0]][5] / 100) # final reload speed from weapon and skill

    # v Stat variable after receive modifier effect from various sources, used for activity and effect calculation
    self.maxmorale = self.basemorale
    self.attack = self.baseattack
    self.meleedef = self.basemeleedef
    self.rangedef = self.baserangedef
    self.armour = self.basearmour
    self.speed = self.basespeed
    self.accuracy = self.baseaccuracy
    self.reload = self.basereload
    self.morale = self.basemorale
    self.discipline = self.basediscipline
    self.shootrange = self.baserange
    self.charge = self.basecharge
    self.chargedef = self.basechargedef
    # ^ End stat for status effect

    if self.mental < 0: # cannot be negative
        self.mental = 0
    elif self.mental > 200: # cannot exceed 100
        self.mental = 200
    self.mentaltext = int(self.mental - 100)
    self.mental = (200 - self.mental) / 100 # convert to percentage

    self.elemmelee = self.baseelemmelee
    self.elemrange = self.baseelemrange
    self.maxhealth, self.health75, self.health50, self.health25, = self.unithealth, round(self.unithealth * 0.75), round(
        self.unithealth * 0.5), round(self.unithealth * 0.25)  # health percentage
    self.oldlasthealth, self.oldlaststamina = self.unithealth, self.stamina  # save previous health and stamina in previous update
    self.maxtroop = self.troopnumber  # max number of troop at the start
    self.moralestate = round((self.basemorale * 100) / self.maxmorale)  # turn into percentage
    self.staminastate = round((self.stamina * 100) / self.maxstamina)  # turn into percentage
    self.staminastatecal = self.staminastate / 100  # for using as modifer on stat
    self.moralestatecal = self.moralestate / 100  # for using as modifer on stat


def csv_read(file, subfolder=[], outputtype=0, defaultmaindir=True):
    """output type 0 = dict, 1 = list"""
    import main
    main_dir = ""
    if defaultmaindir:
        main_dir = main.main_dir
    returnoutput = {}
    if outputtype == 1: returnoutput = []

    folderlist = ""
    for folder in subfolder:
        folderlist += "/" + folder
    folderlist += "/" + file
    with open(main_dir + folderlist, 'r') as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit() or ("-" in i and re.search('[a-zA-Z]', i) is None):
                    row[n] = int(i)
            if outputtype == 0:
                returnoutput[row[0]] = row[1:]
            elif outputtype == 1:
                returnoutput.append(row)
        unitfile.close()
    return returnoutput


def load_sound(file):
    import main
    main_dir = main.main_dir
    file = os.path.join(main_dir, "data/sound/", file)
    sound = pygame.mixer.Sound(file)
    return sound

def editconfig(section, option, value, filename, config):
    config.set(section, option, value)
    with open(filename, 'w') as configfile:
        config.write(configfile)

## mainmenu related script


## Other battle gamescript

def convertweathertime(weatherevent):
    for index, item in enumerate(weatherevent):
        newtime = datetime.datetime.strptime(item[1], '%H:%M:%S').time()
        newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
        weatherevent[index] = [item[0], newtime, item[2]]

def traitskillblit(self):
    from gamescript import gameui
    import main
    SCREENRECT = main.SCREENRECT

    """For blitting skill and trait icon into squad info ui"""
    position = self.gameui[2].rect.topleft
    position = [position[0] + 70, position[1] + 60] # start position
    startrow = position[0]

    for icon in self.skillicon.sprites():
        icon.kill()

    for trait in self.gameui[2].value2[0]:
        self.skillicon.add(gameui.Skillcardicon(self.traitimgs[0], (position[0], position[1]), 0, id=trait))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow

    position = self.gameui[2].rect.topleft
    position = [position[0] + 70, position[1] + 100]
    startrow = position[0]

    for skill in self.gameui[2].value2[1]:
        self.skillicon.add(gameui.Skillcardicon(self.skillimgs[0], (position[0], position[1]), 1, id=skill))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow

def effecticonblit(self):
    """For blitting all status effect icon"""
    position = self.gameui[2].rect.topleft
    position = [position[0] + 70, position[1] + 140]
    startrow = position[0]

    for icon in self.effecticon.sprites():
        icon.kill()

    for status in self.gameui[2].value2[4]:
        self.effecticon.add(gameui.Skillcardicon(self.statusimgs[0], (position[0], position[1]), 4, id=status))
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow

def countdownskillicon(self):
    """count down timer on skill icon for activate and cooldown time"""
    for skill in self.skillicon:
        if skill.type == 1: # only do skill icon not trait
            cd = 0
            activetime = 0
            if skill.gameid in self.gameui[2].value2[2]:
                cd = int(self.gameui[2].value2[2][skill.gameid])
            if skill.gameid in self.gameui[2].value2[3]:
                activetime = int(self.gameui[2].value2[3][skill.gameid][3])
            skill.iconchange(cd, activetime)
    # for effect in self.effecticon:
    #     cd = 0
    #     if effect.id in self.gameui[2].value2[4]:
    #         cd = int(self.gameui[2].value2[4][effect.id][3])
    #     effect.iconchange(cd, 0)

## Battle Start related gamescript

def addarmy(squadlist, position, gameid, colour, imagesize, leader, leaderstat, unitstat, control, coa, command, startangle,starthp,startstamina,team):
    """Create batalion object into the battle, also add hitbox and leader of the battalion"""
    from gamescript import gamebattalion, gameleader
    oldsquadlist = squadlist[~np.all(squadlist == 0, axis=1)] # remove whole empty column in squad list
    squadlist = oldsquadlist[:, ~np.all(oldsquadlist == 0, axis=0)] # remove whole empty row in squad list
    army = gamebattalion.Unitarmy(position, gameid, squadlist, imagesize, colour, control, coa, command, abs(360 - startangle),starthp,startstamina,team)

    # add hitbox for all four sides
    army.hitbox = [gamebattalion.Hitbox(army, 0, army.rect.width - int(army.rect.width * 0.2), 10),
                   gamebattalion.Hitbox(army, 1, 10, army.rect.height - int(army.rect.height * 0.2)),
                   gamebattalion.Hitbox(army, 2, 10, army.rect.height - int(army.rect.height * 0.2)),
                   gamebattalion.Hitbox(army, 3, army.rect.width - int(army.rect.width * 0.2), 10)]

    # add leader
    army.leader = [gameleader.Leader(leader[0], leader[4], 0, army, leaderstat),
                   gameleader.Leader(leader[1], leader[5], 1, army, leaderstat),
                   gameleader.Leader(leader[2], leader[6], 2, army, leaderstat),
                   gameleader.Leader(leader[3], leader[7], 3, army, leaderstat)]
    return army


def unitsetup(maingame):
    """read battalion from unit_pos(source) file and create object with addarmy function"""
    import main
    main_dir = main.main_dir
    from gamescript import gamesquad
    ## defaultarmy = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
                             # [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
    letterboard = ("a", "b", "c", "d", "e", "f", "g", "h") # letter according to squad position in inspect ui similar to chess board
    numberboard = ("8", "7", "6", "5", "4", "3", "2", "1") # same as above
    boardpos = []
    for dd in numberboard:
        for ll in letterboard:
            boardpos.append(ll + dd)
    squadindexlist = [] # squadindexlist is list of every squad index in the game for indexing the squad group
    squadindex = 0 #  squadindex is list index for all squad group
    squadgameid = 10000
    teamstart = [0, 0, 0]
    teamcolour = maingame.teamcolour
    teamarmy = (maingame.team0army, maingame.team1army, maingame.team2army)

    with open(main_dir + "/data/ruleset" + maingame.rulesetfolder + "/map/" + maingame.mapselected + "/unit_pos" + maingame.source + ".csv", 'r') as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit():
                    row[n] = int(i)
                if n in range(1, 12):
                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
            control = False

            if maingame.playerteam == row[16] or maingame.enactment: # player can control only his team or both in enactment mode
                control = True
            colour =  teamcolour[row[16]]
            teamstart[row[16]] += 1
            whicharmy = teamarmy[row[16]]

            command = False # Not commander battalion by default
            if len(whicharmy) == 0: # First battalion is commander
                command = True
            coa = pygame.transform.scale(maingame.coa[row[12]], (60, 60)) # get coa image and scale smaller to fit ui

            army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                           colour, (maingame.squadwidth, maingame.squadheight), row[10] + row[11], maingame.leaderstat, maingame.gameunitstat, control,
                           coa, command, row[13], row[14], row[15], row[16])
            whicharmy.add(army)
            armysquadindex = 0 # armysquadindex is list index for squad list in a specific army

            #v Setup squad in army to squad group
            for squadnum in np.nditer(army.armysquad, op_flags=['readwrite'], order='C'):
                if squadnum != 0:
                    addsquad = gamesquad.Unitsquad(squadnum, squadgameid, army, army.squadpositionlist[armysquadindex],
                                                   maingame.inspectuipos, army.starthp, army.startstamina, maingame.unitscale)
                    maingame.squad.add(addsquad)
                    addsquad.boardpos = boardpos[armysquadindex]
                    squadnum[...] = squadgameid
                    army.squadsprite.append(addsquad)
                    squadindexlist.append(squadgameid)
                    squadgameid += 1
                    squadindex += 1
                armysquadindex += 1
            #^ End squad setup

    unitfile.close()

## Battle related gamescript

def squadcombatcal(who, target, whoside, targetside, sortindex = (3,4,2,5,1,6,0,7)):
    """calculate squad engagement using information after battalionengage who is attacker, target is defender battalion"""
    squadtargetside = [2 if targetside == 3 else 3 if targetside == 2 else targetside][0]
    whofrontline = who.frontlineobject[whoside]
    # """only calculate if the attack is attack with the front side"""
    if whoside == 0:
        # print(whoside, targetside, target.frontline[targetside])
        sortmidfront = [whofrontline[3], whofrontline[4], whofrontline[2], whofrontline[5],
                        whofrontline[1], whofrontline[6], whofrontline[0], whofrontline[7]]
    # else: sortmidfront = whofrontline

        combatpositioncal(sortmidfront, sortindex, target, whoside, targetside, squadtargetside)

def combatpositioncal(sortmidfront, sortindex, receiver, attackerside, receiverside, squadside):
    """Find enemy squad to fight starting at the front of attacker, then either right or left side on the frontline array"""
    for position, attackersquad in enumerate(sortmidfront):
        if attackersquad != 0 and (attackersquad.battleside[squadside] is None or attackersquad.battleside[squadside].state == 100): # only pick new target if not fighting or target already dead
            receiversquad = receiver.frontlineobject[receiverside][sortindex[position]]
            if any(battle > 0 for battle in attackersquad.battlesideid) == False: # check if squad not already fighting if true skip picking new enemy
                if receiversquad != 0: # found front target
                    receiversquad = receiver.frontlineobject[receiverside][sortindex[position]] # get front of another battalion frontline to assign front combat
                    if receiversquad.battlesideid[squadside] == 0: # only attack if the side is already free else just wait until it free
                        attackersquad.battleside[attackerside] = receiversquad
                        attackersquad.battlesideid[attackerside] = receiversquad.gameid

                        receiversquad.battleside[squadside] = attackersquad
                        receiversquad.battlesideid[squadside] = attackersquad.gameid

                else:  # pick flank attack instead if no front target to fight
                    chance = random.randint(0, 1) # attack left array side of the squad if get random 0, right if 1
                    secondpick = 0 # if the first side search result in no target to fight pick another one
                    if chance == 0: secondpick = 1
                    truetargetside = changecombatside(chance, receiverside) # find combatside according to the battalion combat side
                    receiversquad = squadselectside(receiver.frontlineobject[receiverside], chance, sortindex[position])
                    if receiversquad != 0: # attack if the found defender at that side if not check another side
                        if receiversquad.battlesideid[truetargetside] == 0:
                            attackersquad.battleside[attackerside] = receiversquad
                            attackersquad.battlesideid[attackerside] = receiversquad.gameid

                            receiversquad.battleside[truetargetside] = attackersquad
                            receiversquad.battlesideid[truetargetside] = attackersquad.gameid

                    else: # Switch to another side if the first chosen side not found enemy to fight
                        truetargetside = changecombatside(secondpick, receiverside)
                        receiversquad = squadselectside(receiver.frontlineobject[receiverside], secondpick, sortindex[position])
                        if receiversquad != 0:
                            if receiversquad.battlesideid[truetargetside] == 0:
                                attackersquad.battleside[attackerside] = receiversquad
                                attackersquad.battlesideid[attackerside] = receiversquad.gameid

                                receiversquad.battleside[truetargetside] = attackersquad
                                receiversquad.battlesideid[truetargetside] = attackersquad.gameid
                        else: # simply no enemy to fight
                            attackersquad.battleside[attackerside] = None
                            attackersquad.battlesideid[attackerside] = 0

def squadselectside(targetside, side, position):
    """Search squad from selected side to attack from nearby to furthest"""
    thisposition = position
    if side == 0: # left side
        max = 0 # keep searching to the the left until reach the first squad
        while targetside[thisposition] == 0 and thisposition != max: # keep searching until found or it reach max
            thisposition -= 1
    else: # 1 right side
        max = 7 # keep searching to the the right until reach the last squad
        while targetside[thisposition] == 0 and thisposition != max:
            thisposition += 1
    fronttarget = 0
    if targetside[thisposition] != 0:
        fronttarget = targetside[thisposition]
    return fronttarget

def changecombatside(side, position):
    """position is attacker position against defender 0 = front 1 = left 2 = rear 3 = right
    side is side of attack for rotating to find the correct side the defender got attack accordingly (e.g. left attack on right side is front)
        0               0                               front
    1       2  to   1       3   for side index      left     right
        3               2                                rear
    this will make rotation with number easier, - is rotate clockwise and + is rotate anticlockwise
    """
    subposition = position
    if subposition == 2:
        subposition = 3
    elif subposition == 3:
        subposition = 2

    changepos = 1
    if subposition == 2:
        changepos = -1

    finalposition = subposition + changepos  # rotate clockwise (right)
    if side == 0:
        finalposition = subposition - changepos  # rotate anticlockwise

    if finalposition == -1: # - clockwise from front to right (0 to 3)
        finalposition = 3
    elif finalposition == 4: # + anticlockwise from right to front (3 to 0)
        finalposition = 0
    return finalposition

def losscal(attacker, defender, hit, defense, type, defside = None):
    """Calculate damage"""
    who = attacker
    target = defender

    heightadventage = who.battalion.height - target.battalion.height
    if type == 1: heightadventage = int(heightadventage / 2) # Range attack use less height advantage
    hit += heightadventage

    if defense < 0 or who.ignoredef: # Ignore def trait
        defense = 0

    hitchance = hit - defense
    if hitchance < 0: hitchance = 0
    elif hitchance > 80: # Critical hit
        hitchance *= who.criteffect # modify with crit effect further
        if hitchance > 200:
            hitchance = 200

    combatscore = round(hitchance / 50, 1)
    if combatscore == 0 and random.randint(0, 10) > 9:  # Final chence to not miss
        combatscore = 0.1

    leaderdmgbonus = 0
    if who.leader is not None:
        leaderdmgbonus = who.leader.combat # Get extra damage from leader combat ability

    if type == 0:  # Melee damage
        dmg = who.dmg
        if who.charging: # Include charge in dmg if charging
            if who.ignorechargedef == False: # Ignore charge defense if have ignore trait
                sidecal = battlesidecal[defside]
                if target.fulldef or target.tempfulldef: # Defense all side
                    sidecal = 1
                dmg = dmg + (who.charge / 10) - (target.chargedef * sidecal / 10)
            else:
                dmg = dmg + (who.charge / 10)

        if target.charging and target.ignorechargedef == False: # Also include chargedef in dmg if enemy charging
            chargedefcal = who.chargedef - target.charge
            if chargedefcal < 0:
                chargedefcal = 0
            dmg = dmg + (chargedefcal) # if charge def is higher than enemy charge then deal back addtional dmg

        dmg = dmg * ((100 - (target.armour * who.penetrate)) / 100) * combatscore

        if target.state == 10: dmg = dmg / 4 # More dmg against enemy not fighting
    elif type == 1:  # Range Damage
        dmg = who.rangedmg * ((100 - (target.armour * who.rangepenetrate)) / 100) * combatscore

    leaderdmg = dmg
    unitdmg = (dmg * who.troopnumber) + leaderdmgbonus # damage on unit is dmg multiply by troop number with addition from leader combat
    if (who.antiinf and target.type in (1, 2)) or (who.anticav and target.type in (4, 5, 6, 7)):  # Anti trait dmg bonus
        unitdmg = unitdmg * 1.25
    if type == 0: # melee do less damage per hit because the combat happen more frequently than range
        unitdmg = unitdmg / 10

    moraledmg = dmg / 20

    if unitdmg < 0: # Damage cannot be negative (it would heal instead), same for morale and leader damage
        unitdmg = 0
    if leaderdmg < 0:
        leaderdmg = 0
    if moraledmg < 0:
        moraledmg = 0

    return unitdmg, moraledmg, leaderdmg


def applystatustoenemy(statuslist, inflictstatus, receiver, attackerside, receiverside):
    """apply aoe status effect to enemy squads"""
    for status in inflictstatus.items():
        if status[1] == 1 and attackerside == 0: # only front enemy
            receiver.statuseffect[status[0]] = statuslist[status[0]].copy()
        elif status[1] in (2, 3): # aoe effect to side only (2), to also corner enemy (3)
            receiver.statuseffect[status[0]] = statuslist[status[0]].copy()
            if status[1] == 3: # apply to corner enemy squad (left and right of self front enemy squad)
                cornerenemyapply = receiver.nearbysquadlist[0:2]
                if receiverside in (1,2): # attack on left/right side means corner enemy would be from front and rear side of the enemy
                    cornerenemyapply = [receiver.nearbysquadlist[2],receiver.nearbysquadlist[5]]
                for squad in cornerenemyapply:
                    if squad != 0:
                        squad.statuseffect[status[0]] = statuslist[status[0]].copy()
        elif status[1] == 4: # whole battalion aoe
            for squad in receiver.battalion.spritearray.flat:
                if squad.state != 100:
                    squad.statuseffect[status[0]] = statuslist[status[0]].copy()

def complexdmg(attacker, receiver, dmg, moraledmg, leaderdmg, dmgeffect, timermod):
    finaldmg = round(dmg * dmgeffect * timermod)
    finalmoraledmg = round(moraledmg * dmgeffect * timermod)
    if finaldmg > receiver.unithealth: # damage cannot be higher than remaining health
        finaldmg = receiver.unithealth

    receiver.unithealth -= finaldmg
    receiver.basemorale -= (finalmoraledmg + attacker.bonusmoraledmg) * receiver.mental
    receiver.stamina -= attacker.bonusstaminadmg

    if attacker.elemmelee not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
        receiver.elemcount[attacker.elemmelee - 1] += round(finaldmg * (100 - receiver.elemresist[attacker.elemmelee - 1] / 100))

    attacker.basemorale += round((finalmoraledmg / 5)) # recover some morale when deal morale dmg to enemy

    if receiver.leader is not None and receiver.leader.health > 0 and random.randint(0, 10) > 9:  # dmg on squad leader, only 10% chance
        finalleaderdmg = round(leaderdmg - (leaderdmg * receiver.leader.combat/101) * timermod)
        if finalleaderdmg > receiver.leader.health:
            finalleaderdmg = receiver.leader.health
        receiver.leader.health -= finalleaderdmg


def dmgcal(who, target, whoside, targetside, statuslist, combattimer):
    """target position 0 = Front, 1 = Side, 3 = Rear, whoside and targetside is the side attacking and defending respectively"""
    wholuck = random.randint(-50, 50) # attacker luck
    targetluck = random.randint(-50, 50) # defender luck
    whopercent = battlesidecal[whoside] # attacker attack side modifier

    """34 battlemaster fulldef or 91 allrounddef status = no flanked penalty"""
    if who.fulldef or 91 in who.statuseffect:
        whopercent = 1
    targetpercent = battlesidecal[targetside] # defender defend side

    if target.fulldef or 91 in target.statuseffect:
        targetpercent = 1

    dmgeffect = who.frontdmgeffect
    targetdmgeffect = target.frontdmgeffect

    if whoside != 0 and whopercent != 1:  # if attack or defend from side will use discipline to help reduce penalty a bit
        whopercent = battlesidecal[whoside] + (who.discipline / 300)
        dmgeffect = who.sidedmgeffect # use side dmg effect as some skill boost only front dmg
        if whopercent > 1: whopercent = 1

    if targetside != 0 and targetpercent != 1: # same for the target defender
        targetpercent = battlesidecal[targetside] + (target.discipline / 300)
        targetdmgeffect = target.sidedmgeffect
        if targetpercent > 1: targetpercent = 1

    whohit = float(who.attack * whopercent) + wholuck
    whodefense =  float(who.meleedef * whopercent) + wholuck
    targethit = float(who.attack * targetpercent) + targetluck
    targetdefense = float(target.meleedef * targetpercent) + targetluck

    """33 backstabber ignore def when attack rear side, 55 Oblivious To Unexpected can't defend from rear at all"""
    if (who.backstab and targetside == 2) or (target.oblivious and targetside == 2) or (
            target.flanker and whoside in (1, 3)): # Apply only for attacker
        targetdefense = 0

    whodmg, whomoraledmg, wholeaderdmg = losscal(who, target, whohit, targetdefense, 0, targetside) # get dmg by attacker
    targetdmg, targetmoraledmg, targetleaderdmg = losscal(target, who, targethit, whodefense, 0, whoside) # get dmg by defender

    timermod = combattimer / 0.5 # Since the update happen anytime more than 0.5 second, high speed that pass by longer than x1 speed will become inconsistent
    complexdmg(who, target, whodmg, whomoraledmg, wholeaderdmg, dmgeffect, timermod) # Inflict dmg to defender
    complexdmg(target, who, targetdmg, targetmoraledmg, targetleaderdmg, targetdmgeffect, timermod) # Inflict dmg to attacker

    #v Attack corner (side) of self with aoe attack
    if who.corneratk:
        listloop = [target.nearbysquadlist[2], target.nearbysquadlist[5]] # Side attack get (2) front and (5) rear nearby squad
        if targetside in (0, 2): listloop = target.nearbysquadlist[0:2] # Front/rear attack get (0) left and (1) right nearbysquad
        for squad in listloop:
            if squad != 0 and squad.state != 100:
                targethit, targetdefense = float(who.attack * targetpercent) + targetluck, float(squad.meleedef * targetpercent) + targetluck
                whodmg, whomoraledmg = losscal(who, squad, whohit, targetdefense, 0)
                complexdmg(who, squad, whodmg, whomoraledmg, wholeaderdmg, dmgeffect, timermod)
    #^ End attack corner

    #v inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy unit, 4 entire battalion
    if who.inflictstatus != {}:
        applystatustoenemy(statuslist, who.inflictstatus, target, whoside, targetside)
    if target.inflictstatus != {}:
        applystatustoenemy(statuslist, target.inflictstatus, who, targetside, whoside)
    #^ End inflict status


def die(who, battle, group, enemygroup):
    """remove battalion,hitbox when it dies"""
    if who.team == 1:
        battle.team1poslist.pop(who.gameid)
    else:
        battle.team2poslist.pop(who.gameid)

    if who.commander:  # more morale penalty if the battalion is a command battalion
        for army in group:
            for squad in army.squadsprite:
                squad.basemorale -= 30

    for leader in who.leader:
        if leader.state not in (96,97,98,99,100):
            leader.state = 96
            leader.gone()

    for hitbox in who.hitbox: # delete hitbox
        battle.battlecamera.remove(hitbox)
        battle.hitboxes.remove(hitbox)
        hitbox.kill()

    battle.allunitlist.remove(who)
    battle.allunitindex.remove(who.gameid)
    group.remove(who)
    battle.deadunit.add(who)
    battle.battlecamera.change_layer(sprite=who, new_layer=1)
    who.gotkilled = True

    for thisarmy in enemygroup:  # get bonus authority to the another army
        thisarmy.authority += 5

    for thisarmy in group:  # morale dmg to every squad in army when allied battalion destroyed
        for squad in thisarmy.squadsprite:
            squad.basemorale -= 20

def moveleadersquad(leader, oldarmysquad, newarmysquad, alreadypick=[]):
    """oldarmysquad is armysquad list that the squad currently in and need to be move out to the new one (newarmysquad), alreadypick is list of position need to be skipped"""
    replace = [np.where(oldarmysquad == leader.squad.gameid)[0][0],
                     np.where(oldarmysquad == leader.squad.gameid)[1][0]] # grab old array position of squad
    replaceflat = np.where(oldarmysquad.flat == leader.squad.gameid)[0] # grab old flat array pos
    newrow = int(len(newarmysquad) / 2) # set up new row squad will be place in at the middle at the start
    newplace = int(len(newarmysquad[newrow]) / 2) # setup new column position
    placedone = False # finish finding slot to place yet
    newarmysquadlen = len(newarmysquad[newrow]) # get size of row in new armysquad

    while placedone == False:
        if leader.squad.battalion.armysquad.flat[(newrow * newarmysquadlen) + newplace] != 0:
            for squad in leader.squad.battalion.squadsprite:
                if squad.gameid == leader.squad.battalion.armysquad.flat[(newrow * newarmysquadlen) + newplace]:
                    if squad.leader is not None or (newrow,newplace) in alreadypick:
                        newplace += 1
                        if newplace > len(newarmysquad[newrow])-1: # find new column
                            newplace = 0
                        elif newplace == int(len(newarmysquad[newrow]) / 2): # find in new row when loop back to the first one
                            newrow += 1
                        placedone = False
                    else: # found slot to replace
                        placedone = True
                        break
        else:  # fill in the squad if the slot is empty
            placedone = True

    oldarmysquad[replace[0]][replace[1]] = newarmysquad[newrow][newplace]
    newarmysquad[newrow][newplace] = leader.squad.gameid
    return replace, replaceflat, newplace, newrow

def splitunit(battle, who, how):
    """split battalion either by row or column into two seperate battalion"""
    from gamescript import gamebattalion, gameleader

    if how == 0:  # split by row
        newarmysquad = np.array_split(who.armysquad, 2)[1]
        who.armysquad = np.array_split(who.armysquad, 2)[0]
        who.squadalive = np.array_split(who.squadalive, 2)[0]
        newpos = who.allsidepos[3] - ((who.allsidepos[3] - who.basepos) / 2) # position of new battalion when split
        who.basepos = who.allsidepos[0] - ((who.allsidepos[0] - who.basepos) / 2) # position of original battalion

    else:  # split by column
        newarmysquad = np.array_split(who.armysquad, 2, axis=1)[1]
        who.armysquad = np.array_split(who.armysquad, 2, axis=1)[0]
        who.squadalive = np.array_split(who.squadalive, 2, axis=1)[0]
        newpos = who.allsidepos[2] - ((who.allsidepos[2] - who.basepos) / 2)
        who.basepos = who.allsidepos[1] - ((who.allsidepos[1] - who.basepos) / 2)

    if who.leader[1].squad.gameid not in newarmysquad:  # move leader if squad not in new one
        replace, replaceflat, newplace, newrow = moveleadersquad(who.leader[1], who.armysquad, newarmysquad)
        who.squadalive[replace[0]][replace[1]] = \
            [0 if who.armysquad[replace[0]][replace[1]] == 0 or who.squadsprite[replaceflat[0]].state == 100 else 1][0]

    alreadypick = []
    for leader in (who.leader[0], who.leader[2], who.leader[3]):
        if leader.squad.gameid not in who.armysquad:
            replace, replaceflat, newplace, newrow = moveleadersquad(leader, newarmysquad, who.armysquad, alreadypick)
            alreadypick.append((newrow,newplace))
            who.squadalive[replace[0]][replace[1]] = \
                [0 if who.armysquad[replace[0]][replace[1]] == 0 or who.squadsprite[replaceflat[0]].state == 100 else 1][0]
            leader.squadpos = newplace + (newrow * 8)

    squadsprite = [squad for squad in who.squadsprite if squad.gameid in newarmysquad]  # list of sprite not sorted yet
    newsquadsprite = []

    #v Sort so the new leader squad position match what set before
    for squadindex in newarmysquad.flat:
        for squad in squadsprite:
            if squad.gameid == squadindex:
                newsquadsprite.append(squad)
                break
    who.squadsprite = [squad for squad in who.squadsprite if squad.gameid in who.armysquad]
    #^ End sort

    #v Reset position in inspectui for both battalion
    for sprite in (who.squadsprite, newsquadsprite):
        width, height = 0, 0
        squadnum = 0
        for squad in sprite:
            width += battle.squadwidth

            if squadnum >= len(who.armysquad[0]):
                width = 0
                width += battle.squadwidth
                height += battle.squadheight
                squadnum = 0

            squad.inspposition = (width + battle.inspectuipos[0], height + battle.inspectuipos[1])
            squad.rect = squad.image.get_rect(topleft=squad.inspposition)
            squad.pos = pygame.Vector2(squad.rect.centerx, squad.rect.centery)
            squadnum += 1
    #^ End reset position

    newleader = [who.leader[1], gameleader.Leader(1, 0, 1, who, battle.leaderstat), gameleader.Leader(1, 0, 2, who, battle.leaderstat),
                 gameleader.Leader(1, 0, 3, who, battle.leaderstat)] # create new leader list for new battalion

    #v Change the original battalion stat and sprite
    who.leader = [who.leader[0], who.leader[2], who.leader[3], gameleader.Leader(1, 0, 3, who, battle.leaderstat)]
    for index, leader in enumerate(who.leader):  # Also change army position of all leader in that battalion
        leader.armyposition = index  # Change army position to new one
        leader.imgposition = leader.baseimgposition[leader.armyposition]
        leader.rect = leader.image.get_rect(center=leader.imgposition)

    coa = who.coa
    who.recreatesprite()
    who.makeallsidepos()
    who.setupfrontline()
    who.viewmode = battle.camerascale
    who.viewmodechange()
    who.height = who.gamemapheight.getheight(who.basepos)

    for thishitbox in who.hitbox: thishitbox.kill() # remove previous hitbox before create new one
    who.hitbox = [gamebattalion.Hitbox(who, 0, who.rect.width - int(who.rect.width * 0.2), 10),
                  gamebattalion.Hitbox(who, 1, 10, who.rect.height - int(who.rect.height * 0.2)),
                  gamebattalion.Hitbox(who, 2, 10, who.rect.height - int(who.rect.height * 0.2)),
                  gamebattalion.Hitbox(who, 3, who.rect.width - int(who.rect.width * 0.2), 10)]

    who.rotate()
    who.newangle = who.angle
    #^ End change original

    #v need to recalculate max stat again for the original battalion
    maxhealth = []
    maxstamina = []
    maxmorale = []

    for squad in who.squadsprite:
        maxhealth.append(squad.maxtroop)
        maxstamina.append(squad.maxstamina)
        maxmorale.append(squad.maxmorale)

    maxhealth = sum(maxhealth)
    maxstamina = sum(maxstamina) / len(maxstamina)
    maxmorale = sum(maxmorale) / len(maxmorale)

    who.maxhealth, who.health75, who.health50, who.health25, = maxhealth, round(maxhealth * 0.75), round(
        maxhealth * 0.50), round(maxhealth * 0.25)
    who.maxstamina, who.stamina75, who.stamina50, who.stamina25, = maxstamina, round(maxstamina * 0.75), round(
        maxstamina * 0.50), round(maxstamina * 0.25)
    who.maxmorale = maxmorale
    who.ammo75, who.ammo50, who.ammo25 = round(who.ammo * 0.75), round(who.ammo * 0.50), round(who.ammo * 0.25)
    #^ end recal max stat

    #v start making new battalion
    if who.team == 1:
        playercommand = True #TODO change when player can select team
        whosearmy = battle.team1army
        colour = (144, 167, 255)
    else:
        playercommand = battle.enactment
        whosearmy= battle.team2army
        colour = (255, 114, 114)
    newgameid = battle.allunitlist[-1].gameid + 1

    army = gamebattalion.Unitarmy(startposition=newpos, gameid=newgameid,
                                  squadlist=newarmysquad, imgsize=(battle.squadwidth, battle.squadheight),
                                  colour=colour, control=playercommand, coa=coa, commander=False, startangle=who.angle, team=who.team)

    whosearmy.add(army)
    army.leader = newleader
    army.squadsprite = newsquadsprite

    for squad in army.squadsprite:
        squad.battalion = army

    for index, leader in enumerate(army.leader):  # Change army position of all leader in new battalion
        if how == 0:
            if leader.name != "None":
                leader.squadpos -= newarmysquad.size  # Just minus the row gone to find new position
            else: leader.squadpos = 0
        else:
            if leader.name != "None":
                for spriteindex, squad in enumerate(army.squadsprite):  # Loop to find new squad pos based on new squadsprite list
                    if squad.gameid == leader.squad.gameid:
                        leader.squadpos = spriteindex
                        break
            else: leader.squadpos = 0
        leader.battalion = army  # Set leader battalion to new one
        leader.armyposition = index  # Change army position to new one
        leader.imgposition = leader.baseimgposition[leader.armyposition]  # Change image pos
        leader.rect = leader.image.get_rect(center=leader.imgposition)
        leader.poschangestat(leader)  # Change stat based on new army position

    army.teamcommander = who.teamcommander
    army.commandbuff = [(army.leader[0].meleecommand - 5) * 0.1, (army.leader[0].rangecommand - 5) * 0.1, (army.leader[0].cavcommand - 5) * 0.1]
    army.leadersocial = army.leader[0].social
    army.authrecal()
    battle.allunitlist.append(army)
    battle.allunitindex.append(army.gameid)
    battle.lastselected = who
    for hitbox in battle.lastselected.hitbox:
        hitbox.clicked()
    army.viewmode = battle.camerascale

    #v Remake sprite to match the current varible (angle, zoom level, position)
    army.recreatesprite()
    army.makeallsidepos()
    army.viewmodechange()
    army.angle = army.angle
    army.rotate()
    #^ End remake sprite

    army.terrain, army.feature = army.getfeature(army.basepos, army.gamemap)

    army.sidefeature = [army.getfeature(army.allsidepos[0], army.gamemap), army.getfeature(army.allsidepos[1], army.gamemap),
                        army.getfeature(army.allsidepos[2], army.gamemap), army.getfeature(army.allsidepos[3], army.gamemap)]
    army.hitbox = [gamebattalion.Hitbox(army, 0, army.rect.width - int(army.rect.width * 0.2), 10), # add hitbox for all four sides
                   gamebattalion.Hitbox(army, 1, 10, army.rect.height - int(army.rect.height * 0.2)),
                   gamebattalion.Hitbox(army, 2, 10, army.rect.height - int(army.rect.height * 0.2)),
                   gamebattalion.Hitbox(army, 3, army.rect.width - int(army.rect.width * 0.2), 10)]
    army.autosquadplace = False
    #^ End making new battalion

## Other scripts

def playgif(imageset, framespeed = 100):
    """framespeed in millisecond"""
    animation = {}
    frames = ["image1.png","image2.png"]
