import configparser
import glob
import os.path
import sys

# import basic pygame modules
import pygame
import pygame.freetype
from pygame.locals import *

from RTS import maingame

config = configparser.ConfigParser()
config.read_file(open('configuration.ini'))
ScreenHeight = int(config['DEFAULT']['ScreenHeight'])
ScreenWidth = int(config['DEFAULT']['ScreenWidth'])
FULLSCREEN = int(config['DEFAULT']['Fullscreen'])
SoundVolume = float(config['DEFAULT']['SoundVolume'])

SCREENRECT = Rect(0, 0, ScreenWidth, ScreenHeight)
main_dir = os.path.split(os.path.abspath(__file__))[0]

class menutext(pygame.sprite.Sprite):
    def __init__(self, images, X, Y, gamescreen,text="", size=16):
        self.X, self.Y = X, Y
        self.images = images
        self.text = text
        self.font = pygame.font.SysFont("timesnewroman", size)
        if text != "":
            # self.imagescopy = self.images
            self.textsurface = self.font.render(self.text, 1,(0,0,0))
            self.textrect = self.textsurface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(self.textsurface, self.textrect)
            self.images[1].blit(self.textsurface, self.textrect)
            self.images[2].blit(self.textsurface, self.textrect)
        self.image = self.images[0]
        self.rects = self.images[0].get_rect(center=(self.X, self.Y))
        self.event = False

    def update(self, mouse_pos, mouse_up):
        if self.rects.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                self.rects = self.images[2].get_rect(center=(self.X, self.Y))
                # print("click", self.X, self.Y)
                self.event = True
                return self.event
        else:self.mouse_over = False
        if self.mouse_over == True:
            self.rects = self.images[1].get_rect(center=(self.X, self.Y))
            self.image = self.images[1]
            # if mouse_up:
        else:
            self.rects = self.images[0].get_rect(center=(self.X, self.Y))
            self.image = self.images[0]

    def draw(self, gamescreen):
        """ Draws element onto a surface """
        gamescreen.blit(self.image, self.rects)

    def changestate(self, gamescreen, text):
        if text != "":
            img = load_image('scroll_normal.jpg', 'ui')
            img2 = img
            img3 = load_image('scroll_click.jpg', 'ui')
            self.images = [img, img2, img3]
            self.textsurface = self.font.render(text, 1,(0,0,0))
            self.textrect = self.textsurface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(self.textsurface, self.textrect)
            self.images[1].blit(self.textsurface, self.textrect)
            self.images[2].blit(self.textsurface, self.textrect)
        self.rects = self.images[0].get_rect(center=(self.X, self.Y))
        self.event = False

class menuicon(pygame.sprite.Sprite):
    def __init__(self, images, X, Y, gamescreen,text="", imageresize=0):
        self.X, self.Y = X, Y
        self.images = images
        self.image = self.images[0]
        if imageresize != 0:
            self.image = pygame.transform.scale(self.image, (imageresize, imageresize))
        self.text = text
        self.font = pygame.font.SysFont("timesnewroman", 16)
        if text != "":
            self.textsurface = self.font.render(self.text, 1,(0,0,0))
            self.textrect = self.textsurface.get_rect(center=self.image.get_rect().center)
        self.rects = self.image.get_rect(center=(self.X, self.Y))
        self.event = False

    def draw(self, gamescreen):
        """ Draws element onto a surface """
        gamescreen.blit(self.image, self.rects)

    def update(self, mouse_pos, mouse_up):
        if self.rects.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                self.rects = self.images[2].get_rect(center=(self.X, self.Y))
                self.event = True
                return self.event
        else:self.mouse_over = False
        if self.mouse_over == True:
            self.rects = self.images[1].get_rect(center=(self.X, self.Y))
            self.image = self.images[1]
            # if mouse_up:
        else:
            self.rects = self.images[0].get_rect(center=(self.X, self.Y))
            self.image = self.images[0]

class slidermenu(pygame.sprite.Sprite):
    def __init__(self, barimage, buttonimage, textimage , X, Y, gamescreen, value, text="", imageresize=0, min_value=0, max_value=100, size=16):
        self.X, self.Y = X, Y
        self.barimage = barimage
        self.buttonimagelist = buttonimage
        self.buttonimage = self.buttonimagelist[0]
        self.textimage_original = pygame.transform.scale(textimage, (int(textimage.get_size()[0]/2), int(textimage.get_size()[1]/2)))
        self.textimage = self.textimage_original.copy()
        self.min_value = self.X-100
        self.max_value = self.X+100
        self.text = text
        self.size = size
        self.font = pygame.font.SysFont("timesnewroman", self.size)
        self.event = False
        self.value = value
        self.textsurface = self.font.render(str(self.value), 1, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=self.textimage.get_rect().center)
        self.textimage.blit(self.textsurface, self.textrect)
        self.mouse_value = self.value+self.X
        self.rects = self.barimage.get_rect(center=(self.X, self.Y))
        slidersize = self.barimage.get_size()
        self.textimagerects = self.textimage_original.get_rect(center=(self.X+slidersize[0], self.Y))

    def draw(self, gamescreen):
        gamescreen.blit(self.barimage, self.rects)
        self.buttonrects = self.buttonimagelist[1].get_rect(center=(self.mouse_value, self.Y))
        gamescreen.blit(self.buttonimage, self.buttonrects)
        gamescreen.blit(self.textimage, self.textimagerects)

    def update(self, mouse_pos, mouse_up):
        if self.rects.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                self.mouse_value = mouse_pos[0]
                if self.mouse_value > self.max_value:
                    self.mouse_value = self.max_value
                if self.mouse_value <self.min_value:
                    self.mouse_value = self.min_value
                self.value = (self.mouse_value-self.min_value)/2
                self.textimage = self.textimage_original.copy()
                self.textsurface = self.font.render(str(self.value), 1, (0, 0, 0))
                self.textrect = self.textsurface.get_rect(center=self.textimage.get_rect().center)
                self.textimage.blit(self.textsurface, self.textrect)
                self.rects = self.barimage.get_rect(center=(self.X, self.Y))
                slidersize = self.barimage.get_size()
                self.textimagerects = self.textimage_original.get_rect(center=(self.X + slidersize[0], self.Y))
                self.event = True
        else:self.mouse_over = False


def load_image(file, subfolder):
    file = os.path.join(main_dir, 'data', subfolder, file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert_alpha()

def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs

def load_sound(file):
    file = os.path.join(main_dir, 'data/sound/', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)


def makebarlist(listtodo,menuimage,screen):
    barlist=[]
    number = 1.06
    # runnum=0.0005
    for bar in listtodo:
        img = load_image('bar_normal.jpg', 'ui')
        img2 = load_image('bar_mouse.jpg', 'ui')
        img3 = img2
        barimage = [img, img2, img3]
        # print(bar)
        bar = menutext(images=barimage, X=menuimage.X, Y=menuimage.Y*number, gamescreen=screen, text=bar)
        number+=0.06#-runnum
        # runnum+=0.01
        barlist.append(bar)
    return barlist

def editconfig(section, option, value, filename, config):
    config.set(section, option, value)
    with open(filename, 'w') as configfile:
        config.write(configfile)

def load_base_button():
    img = load_image('idle_button.png', 'ui')
    img2 = load_image('mouse_button.png', 'ui')
    img3 = load_image('click_button.png', 'ui')
    return [img, img2 ,img3]

def text_objects(text, font):
    textSurface = font.render(text, True, (200,200,200))
    return textSurface, textSurface.get_rect()

def game_intro(screen,clock,introoption):
    intro = introoption
    if introoption == True:
        intro = True
    timer = 0
    # quote = ["Those who fail to learn from the mistakes of their predecessors are destined to repeat them. George Santayana", "It is more important to outhink your enemy, than to outfight him, Sun Tzu"]
    while intro:
        for event in pygame.event.get():
            if event.type ==  KEYDOWN:
                intro = False
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        largeText = pygame.font.Font('freesansbold.ttf', 115)
        TextSurf, TextRect = text_objects("Test Intro", largeText)
        TextRect.center = (700,600)
        screen.blit(TextSurf, TextRect)
        pygame.display.update()
        clock.tick(60)
        timer+=1
        if timer == 1000: intro = False

# def encyclopedia(screen):
#     gamearmy.leader
#     gamearmy.weaponstat
#     gamearmy.unitstat

class mainmenu():
    def __init__(self):
        # Initialize pygame
        pygame.init()
        if pygame.mixer and not pygame.mixer.get_init():
            print ('Warning, no sound')
            pygame.mixer = None

        # Set the display mode
        self.winstyle = 0  # |FULLSCREEN
        if FULLSCREEN == 1:
            self.winstyle = pygame.FULLSCREEN
        self.bestdepth = pygame.display.mode_ok(SCREENRECT.size, self.winstyle, 32)
        self.screen = pygame.display.set_mode(SCREENRECT.size, self.winstyle | pygame.RESIZABLE, self.bestdepth)
        # run game intro
        self.clock = pygame.time.Clock()
        game_intro(self.screen,self.clock, False)
        bgdtile = load_image('background.jpg', 'ui')
        self.background = pygame.Surface(SCREENRECT.size)
        for x in range(0, SCREENRECT.width, bgdtile.get_width()):
            self.background.blit(bgdtile, (x, 0))
        self.screen.blit(self.background, (0, 0))
        imagelist = load_base_button()
        self.menubutton = menutext(images=imagelist, X=SCREENRECT.width / 2, Y=SCREENRECT.height / 2, gamescreen=self.screen, text = "START")
        imagelist = load_base_button()
        self.menubutton2 = menutext(images=imagelist, X=SCREENRECT.width / 2, Y=SCREENRECT.height / 1.2, gamescreen=self.screen, text = "QUIT")
        imagelist = load_base_button()
        self.menubutton3 = menutext(images=imagelist, X=SCREENRECT.width / 2, Y=SCREENRECT.height / 1.5, gamescreen=self.screen, text = "OPTION")
        imagelist = load_base_button()
        self.menubutton4 = menutext(images=imagelist, X=SCREENRECT.width / 2, Y=SCREENRECT.height / 1.2, gamescreen=self.screen, text = "BACK")
        img = load_image('scroll_normal.jpg', 'ui')
        img2 = img
        img3 = load_image('scroll_click.jpg', 'ui')
        imagelist = [img, img2, img3]
        self.scrollbar1 = menutext(images=imagelist, X=SCREENRECT.width / 2, Y=SCREENRECT.height / 2.3, gamescreen=self.screen, text= str(ScreenWidth) + " x " + str(ScreenHeight), size=16)
        resolutionlist = ['1920 x 1080', '1600 x 900', '1366 x 768', '1280 x 720', '1024 x 768', ]
        self.resolutionbar = makebarlist(listtodo=resolutionlist, menuimage=self.scrollbar1, screen=self.screen)
        img = load_image('resolution_icon.png', 'ui')
        self.resolutionicon = menuicon(images=[img], X=self.scrollbar1.X-150, Y=self.scrollbar1.Y, gamescreen=self.screen, imageresize=50)
        img = load_image('scroller.png', 'ui')
        img2 = load_image('scoll_button_normal.png', 'ui')
        img3 = load_image('scoll_button_click.png', 'ui')
        img4 = load_image('numbervalue_icon.jpg', 'ui')
        self.sliderbutton1 = slidermenu(barimage=img, buttonimage=[img2,img3], textimage=img4, X=SCREENRECT.width / 2, Y=SCREENRECT.height / 3, gamescreen=self.screen,value=SoundVolume,min_value=0, max_value=100)
        img = load_image('volume_icon.png', 'ui')
        self.volumeicon = menuicon(images=[img], X=self.sliderbutton1.X-150, Y=self.sliderbutton1.Y, gamescreen=self.screen,imageresize=50)
        pygame.display.set_caption('Pax Paradisum')
        pygame.mouse.set_visible(1)
        if pygame.mixer:
            self.mixervolume = float(SoundVolume/100)
            pygame.mixer.music.set_volume(self.mixervolume)
            self.SONG_END = pygame.USEREVENT + 1
            # musiclist = os.path.join(main_dir, 'data/sound/')
            self.musiclist = glob.glob(main_dir + '/data/sound/*.mp3')
            pygame.mixer.music.load(self.musiclist[0])
            pygame.mixer.music.play(-1)
        self.all = pygame.sprite.RenderUpdates()
        self.menustate = "mainmenu"
        addmorebar = "no"

    def run(self,maingamefunc):
        while True:
            self.screen.blit(self.background, (0, 0))
            #get input
            mouse_up = False
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) or self.menubutton2.event == True:
                    return
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouse_up = True
                    # print(pygame.mouse.get_pos())
                # elif event.type == MOUSEWHEEL:
                #    print(event)
            keystate = pygame.key.get_pressed()
            if self.menustate == "mainmenu":
                self.menubutton.update(pygame.mouse.get_pos(), mouse_up)
                self.menubutton.draw(self.screen)
                self.menubutton2.update(pygame.mouse.get_pos(), mouse_up)
                self.menubutton2.draw(self.screen)
                self.menubutton3.update(pygame.mouse.get_pos(), mouse_up)
                self.menubutton3.draw(self.screen)
                if self.menubutton.event == True:
                    self.battlegame = maingamefunc.battle(self.winstyle)
                    self.battlegame.rungame()
                    self.menubutton.event = False
                if self.menubutton3.event == True:
                    self.menustate = "option"
                    self.menubutton3.event = False
            elif self.menustate == "option":
                self.menubutton4.update(pygame.mouse.get_pos(), mouse_up)
                self.menubutton4.draw(self.screen)
                self.scrollbar1.update(pygame.mouse.get_pos(), mouse_up)
                self.scrollbar1.draw(self.screen)
                self.sliderbutton1.update(pygame.mouse.get_pos(), mouse_up)
                self.sliderbutton1.draw(self.screen)
                self.resolutionicon.draw(self.screen)
                self.volumeicon.draw(self.screen)
                if self.menubutton4.event == True:
                    self.menustate = "mainmenu"
                    self.menubutton4.event = False
                if self.scrollbar1.event == True:
                    for bar in self.resolutionbar:
                        bar.update(pygame.mouse.get_pos(), mouse_up)
                        bar.draw(self.screen)
                        if bar.event == True:
                            #change button value based on selected
                            self.scrollbar1.changestate(self.screen, bar.text)
                            self.scrollbar1.draw(self.screen)
                            resolutionchange = bar.text.split()
                            # print(resolutionchange)
                            self.newScreenWidth = resolutionchange[0]
                            self.newScreenHeight = resolutionchange[2]
                            editconfig('DEFAULT','ScreenWidth', self.newScreenWidth,'configuration.ini',config)
                            editconfig('DEFAULT', 'ScreenHeight', self.newScreenHeight, 'configuration.ini', config)
                            self.screen = pygame.display.set_mode(SCREENRECT.size, self.winstyle | pygame.RESIZABLE, self.bestdepth)
                            self.scrollbar1.event = False
                            bar.event = False
                if self.sliderbutton1.event == True:
                    self.mixervolume = float(self.sliderbutton1.value / 100)
                    pygame.mixer.music.set_volume(self.mixervolume)
                    editconfig('DEFAULT', 'SoundVolume', str(self.sliderbutton1.value), 'configuration.ini', config)
                    self.sliderbutton1.event = False
            # resolution_menu = (
            #     'Resolution',

            pygame.display.flip()
            self.all.clear(self.screen, self.background)
            self.all.update()
            dirty = self.all.draw(self.screen)
            pygame.display.update(dirty)
            self.clock.tick(60)

        if pygame.mixer:
            pygame.mixer.music.fadeout(1000)
        pygame.time.wait(1000)
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    runmenu = mainmenu()
    runmenu.run(maingame)

