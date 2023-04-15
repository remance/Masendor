import sys
import os
import pygame
from flask import Flask, render_template, redirect

# ---
# to get this to work on my computer I acutal has to have this (I tested using both this current directory and the actual "main" directory
# as working directory and it does not work. /coppermouse
# This appends main directory to "sys.path" which makes it possible to import gamescript.
file_path = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
main_dir = os.path.normpath(os.path.join(file_path, '..'))
sys.path.append(main_dir)
# ---

from gamescript.common import utility  # nopep8
from gamescript.common.game.create_troop_sprite_pool import create_troop_sprite_pool  # nopep8
from gamescript.game import Game  # nopep8
from gamescript.common.game.setup.make_faction_troop_leader_data import make_faction_troop_leader_data  # nopep8
from gamescript import datasprite  # nopep8

csv_read = utility.csv_read

# this wiki make use of the create_troop_sprite_pool method.
# that method is depended on the Game class but when making a Game instance it
# starts the game, we do not want that, that is why we make use of a custom minified Game class
# that works better for this script.


class MinifiedGame(Game):
    """
        Like Game but with less functionality but enough to view sprites.
    """

    def __init__(self, main_dir):
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
            Minified change ruleset-method. Removed things that otherwise wouldn't allow
            the script to be able to run.
        """

        self.troop_data, self.leader_data, self.faction_data = make_faction_troop_leader_data(self.main_dir, self.screen_scale, self.ruleset_folder, self.language)

        self.troop_animation = datasprite.TroopAnimationData(
            self.main_dir,
            [str(self.troop_data.race_list[key]["Name"])
             for key in self.troop_data.race_list],
            self.team_colour
        )

        self.subunit_animation_data = self.troop_animation.subunit_animation_data
        self.gen_body_sprite_pool = self.troop_animation.gen_body_sprite_pool
        self.gen_armour_sprite_pool = self.troop_animation.gen_armour_sprite_pool
        self.colour_list = self.troop_animation.colour_list
        self.gen_weapon_sprite_pool = self.troop_animation.gen_weapon_sprite_pool
        self.weapon_joint_list = self.troop_animation.weapon_joint_list


pygame.init()

screen = pygame.display.set_mode((1, 1), pygame.HIDDEN)

assert type(main_dir) == str
print("main dir: {0}".format(main_dir))

game = MinifiedGame(main_dir)
game.change_ruleset()

app = Flask(__name__)


@app.route("/")
def index():
    return redirect("/sub-units")


@app.route("/regions")
def regions():

    regions = set()
    for faction in game.faction_data.faction_list.values():
        regions.add(faction['Type'])

    # There is a "All" Region/Type found on the faction "All Factions" in faction.csv.
    # This is obviously not an actual faction nor region so I discard it from being visible.
    regions.discard("All")

    return render_template("regions.j2", regions=regions)


@app.route("/factions")
def factions():
    return render_template("factions.j2")


@app.route("/troop-classes")
def troop_classes():
    return render_template("troop-classes.j2")


@app.route("/sub-units")
def sub_units():

    sub_units = list()
    for k, v in (game.troop_data.troop_list | game.leader_data.leader_list).items():
        sub_units.append({"name": v["Name"], "troop-class": v.get("Troop Class", "-"), "race": v["Race"]})

    return render_template("sub-units.j2", sub_units=sub_units)

app.run()
