import sys
import os

import pygame
import pygame_gui
from gamescript.common import utility
from gamescript.common.game.create_troop_sprite_pool import create_troop_sprite_pool
from gamescript.game import Game
from gamescript.common.game.setup.make_faction_troop_leader_data import make_faction_troop_leader_data
from gamescript import datasprite

csv_read = utility.csv_read


def get_all_surfaces_recursive( _dict, return_container = None):
    if return_container is None: return_container = set()
    for k, v in _dict.items():        
        if isinstance( v, dict ):
            get_all_surfaces_recursive( v, return_container )
        if type(v) == pygame.Surface:
            return_container.add( v )
    return return_container
 
# this sprite view make use of the create_troop_sprite_pool method.
# that method is depended on the Game class but when making a Game instance it 
# starts the game, we do not want that, that is why we make use of a custom minified Game class
# that works better for this script.

# Credit to coppermouse (https://github.com/coppermouse)


class MinifiedGame( Game ):
    """
        Like Game but with less functionality but enough to view sprites.
    """

    def __init__( self, main_dir ):
        """
            Minified init-method. Prevents the game from starting an only setup a required state.
        """
        self.main_dir = main_dir
        self.screen_scale = (1, 1)
        self.ruleset = 0
        self.ruleset_list = csv_read(
            self.main_dir, "ruleset_list.csv", ("data", "ruleset"))
        self.ruleset_folder = str(self.ruleset_list[self.ruleset][0]).strip("/")
        self.language = 'en'


    def change_ruleset(self):
        """
            Minified init-method. Removed things that otherwise wouldn't allow
            the script to be able to run.
        """
 
        self.troop_data, self.leader_data, self.faction_data = make_faction_troop_leader_data(
            self.main_dir,self.screen_scale, self.ruleset_folder, self.language )

        self.troop_animation = datasprite.TroopAnimationData(
            self.main_dir,
            [ str(self.troop_data.race_list[key]["Name"] ) 
              for key in self.troop_data.race_list ], 
            self.team_colour)

        self.subunit_animation_data = self.troop_animation.subunit_animation_data
        self.gen_body_sprite_pool = self.troop_animation.gen_body_sprite_pool
        self.gen_armour_sprite_pool = self.troop_animation.gen_armour_sprite_pool
        self.colour_list = self.troop_animation.colour_list
        self.gen_weapon_sprite_pool = self.troop_animation.gen_weapon_sprite_pool
        self.weapon_joint_list = self.troop_animation.weapon_joint_list

current_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\") + 1]

error_log = open(os.path.join(main_dir + "/error_report.txt"), "w")

pygame.init()

SCREEN_SIZE = ( 1540, 900 )

pygame.display.set_caption('Sprite Viewer')
screen = pygame.display.set_mode( SCREEN_SIZE )
manager = pygame_gui.UIManager( SCREEN_SIZE )

clock = pygame.time.Clock()
running = True


assert type(main_dir) == str
print("main dir: {0}".format(main_dir))

game = MinifiedGame( main_dir )
game.change_ruleset()

# units are concat of both leaders and troops
units = {}
for k, v in ( game.troop_data.troop_list | game.leader_data.leader_list ).items():
    units[ str(k) + ':' + str(v['Name']) ] = {k:v}


pygame_gui.elements.UISelectionList(
    relative_rect=pygame.Rect((10, 10), (300, 350)), 
    item_list = sorted(units.keys()),
    object_id = "select-unit"
)


sprites = []
refresh = True # only refresh sprites when refresh is True, no need to re-render them every frame
while running:

     time_delta = clock.tick(60) / 1000

     for event in pygame.event.get():

         if hasattr( event, 'type' ):

            if event.type == 32877: # select
                if event.ui_object_id == 'select-unit':
                    try:
                        data = create_troop_sprite_pool( game, units[ event.text ] )[0]
                        sprites = get_all_surfaces_recursive(data)
                        displays = list( sprites )
                        refresh = True
                    except Exception as e:
                        print("some error with unit {0}".format(event.text))
                        displays = list()
                        refresh = True
                        
            if event.type == 32878: # deselect
                pass

         if event.type == pygame.QUIT:
             running = False

         manager.process_events(event)

     manager.update(time_delta)

     if refresh:
        screen.fill(0x112233)
        refresh = False
        for e, sprite in enumerate(sprites):
            x,y = e%16, e//16
            screen.blit( sprite, (400+x*48,y*48) )

     manager.draw_ui(screen)
     pygame.display.update()

