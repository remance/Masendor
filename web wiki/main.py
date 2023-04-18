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

troop_skill_list = game.troop_data.skill_list
weapon_list = game.troop_data.weapon_list
armour_list = game.troop_data.armour_list
troop_grade_list = game.troop_data.grade_list
equipment_grade_list = game.troop_data.equipment_grade_list
mount_list = game.troop_data.mount_list
mount_grade_list = game.troop_data.mount_grade_list
mount_armour_list = game.troop_data.mount_armour_list
leader_skill_list = game.leader_data.skill_list  # leader skill list is different from troop
leader_portrait = game.leader_data.images
leader_class = game.leader_data.leader_class


def get_subunit_icon(subunit_id, scale):
    """get a icon for a specific subunit"""

    subunits = (game.troop_data.troop_list | game.leader_data.leader_list)
    who_todo = {key: value for key, value in subunits.items() if key == subunit_id}

    # make idle animation, first frame, right side (change to l_side for left), non-specific so it can make for any troops
    preview_sprite_pool, _ = create_troop_sprite_pool(game, who_todo, preview=True, specific_preview=("Idle_0", 0, "r_side", "non-specific"),
                                                      max_preview_size=scale)
    sprite = preview_sprite_pool[subunit_id]["sprite"]
    icon = pygame.Surface((36, 36), pygame.SRCALPHA)
    icon.blit(sprite, (0, 0))
    return icon


@app.route("/")
def index():
    return redirect("/leaders")


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
    troop_classes = list()
    for k, v in game.troop_data.troop_class.items():
        troop_class = {
            "name": k,
            "strengths": v["Strengths"],
            "weaknesses": v["Weaknesses"]}
        troop_classes.append(troop_class)
    return render_template("troop-classes.j2", troop_classes=troop_classes)


@app.route("/troops")
def troops():
    troops = list()
    for k, v in game.troop_data.troop_list.items():
        troop = {
            "name": v["Name"],
            "grade": troop_grade_list[v.get('Grade')]["Name"],
            "troop-class": v.get("Troop Class", "-"),
            "race": v["Race"],
            "melee-speciality": v.get('Melee Attack Scale'),
            "defence-speciality": v.get('Defence Scale'),
            "range-speciality": v.get('Ranged Attack Scale'),

            "primary-main-weapon": (
                (equipment_grade_list[v.get('Primary Main Weapon')[1]]["Name"] if
                 v.get('Primary Main Weapon') and type(v.get('Primary Main Weapon')[0]) == int
                 else "-"),
                (weapon_list[v.get("Primary Main Weapon")[0]]["Name"]
                 if v.get('Primary Main Weapon') and type(v.get('Primary Main Weapon')[0]) == int
                 else "-")
            ),

            "primary-sub-weapon": (
                (equipment_grade_list[v.get('Primary Sub Weapon')[1]]["Name"] if
                 v.get('Primary Sub Weapon') and type(v.get('Primary Sub Weapon')[0]) == int
                 else "-"),
                (weapon_list[v.get("Primary Sub Weapon")[0]]["Name"]
                 if v.get('Primary Sub Weapon') and type(v.get('Primary Sub Weapon')[0]) == int
                 else "-")
            ),

            "secondary-main-weapon": (
                (equipment_grade_list[v.get('Secondary Main Weapon')[1]]["Name"] if
                 v.get('Secondary Main Weapon') and type(v.get('Secondary Main Weapon')[0]) == int
                 else "-"),
                (weapon_list[v.get("Secondary Main Weapon")[0]]["Name"]
                 if v.get('Secondary Main Weapon') and type(v.get('Secondary Main Weapon')[0]) == int
                 else "-")
            ),

            "secondary-sub-weapon": (
                (equipment_grade_list[v.get('Secondary Sub Weapon')[1]]["Name"] if
                 v.get('Secondary Sub Weapon') and type(v.get('Secondary Sub Weapon')[0]) == int
                 else "-"),
                (weapon_list[v.get("Secondary Sub Weapon")[0]]["Name"]
                 if v.get('Secondary Sub Weapon') and type(v.get('Secondary Sub Weapon')[0]) == int
                 else "-")
            ),

            "armour": (
                (equipment_grade_list[v.get('Armour')[1]]["Name"] if
                 v.get('Armour') and type(v.get('Armour')[0]) == int
                 else "-"),
                (armour_list[v.get("Armour")[0]]["Name"]
                 if v.get('Armour') and type(v.get('Armour')[0]) == int
                 else "-")
            ),

            "mount": (
                (mount_grade_list[v.get('Mount')[1]]["Name"] if
                 v.get('Mount') and type(v.get('Mount')[0]) == int
                 else "-"),
                (mount_list[v.get("Mount")[0]]["Name"]
                 if v.get('Mount') and type(v.get('Mount')[0]) == int
                 else "-"),
                (mount_armour_list[v.get("Mount")[2]]["Name"]
                 if v.get('Mount') and type(v.get('Mount')[0]) == int
                 else "-")
            ),

            "skill": [troop_skill_list[int(v.get('Charge Skill'))]["Name"] if v.get('Charge Skill') else "-"] +
                     [troop_skill_list[item]["Name"] for item in v.get('Skill')],
            "trait": v.get('Trait'),
            "role": v.get('Role'),
        }

        troops.append(troop)

        subunit_icon_server_path = os.path.join(main_dir, "web wiki", "static", "{0}.png".format(k))
        subunit_icon_web_path = "static/{0}.png".format(k)
        troop['icon'] = [subunit_icon_web_path, k]

        if not os.path.isfile(subunit_icon_server_path):
            try:
                subunit_icon = get_subunit_icon(k, 35)
                pygame.image.save(subunit_icon, subunit_icon_server_path)
            except Exception as e:
                pass
                # raise e

    return render_template("troops.j2", troops=troops)


@app.route("/leaders")
def leaders():
    leaders = list()
    for k, v in game.leader_data.leader_list.items():
        leader = {
            "name": v["Name"],
            "strength": v.get("Strength", "-"),
            "dexterity": v.get("Dexterity"),
            "agility": v.get("Agility"),
            "constitution": v.get("Constitution"),
            "intelligence": v.get("Intelligence"),
            "wisdom": v.get("Wisdom"),
            "charisma": v.get("Charisma"),
            "troop-class": v.get("Troop Class", "-"),
            "race": v["Race"],
            "melee-speciality": v.get('Melee Speciality'),
            "range-speciality": v.get('Range Speciality'),
            "cavalry-speciality": v.get('Cavalry Speciality'),

            "social-class": (
                (leader_class[v.get('Social Class')]["Leader Social Class"]
                 if v.get('Social Class')
                 else "-")
            ),

            "primary-main-weapon": (
                (equipment_grade_list[v.get('Primary Main Weapon')[1]]["Name"] if
                 v.get('Primary Main Weapon') and type(v.get('Primary Main Weapon')[0]) == int
                 else "-"),
                (weapon_list[v.get("Primary Main Weapon")[0]]["Name"]
                 if v.get('Primary Main Weapon') and type(v.get('Primary Main Weapon')[0]) == int
                 else "-")
            ),

            "primary-sub-weapon": (
                (equipment_grade_list[v.get('Primary Sub Weapon')[1]]["Name"] if
                 v.get('Primary Sub Weapon') and type(v.get('Primary Sub Weapon')[0]) == int
                 else "-"),
                (weapon_list[v.get("Primary Sub Weapon")[0]]["Name"]
                 if v.get('Primary Sub Weapon') and type(v.get('Primary Sub Weapon')[0]) == int
                 else "-")
            ),

            "secondary-main-weapon": (
                (equipment_grade_list[v.get('Secondary Main Weapon')[1]]["Name"] if
                 v.get('Secondary Main Weapon') and type(v.get('Secondary Main Weapon')[0]) == int
                 else "-"),
                (weapon_list[v.get("Secondary Main Weapon")[0]]["Name"]
                 if v.get('Secondary Main Weapon') and type(v.get('Secondary Main Weapon')[0]) == int
                 else "-")
            ),

            "secondary-sub-weapon": (
                (equipment_grade_list[v.get('Secondary Sub Weapon')[1]]["Name"] if
                 v.get('Secondary Sub Weapon') and type(v.get('Secondary Sub Weapon')[0]) == int
                 else "-"),
                (weapon_list[v.get("Secondary Sub Weapon")[0]]["Name"]
                 if v.get('Secondary Sub Weapon') and type(v.get('Secondary Sub Weapon')[0]) == int
                 else "-")
            ),

            "armour": (
                (equipment_grade_list[v.get('Armour')[1]]["Name"] if
                 v.get('Armour') and type(v.get('Armour')[0]) == int
                 else "-"),
                (armour_list[v.get("Armour")[0]]["Name"]
                 if v.get('Armour') and type(v.get('Armour')[0]) == int
                 else "-")
            ),

            "mount": (
                (mount_grade_list[v.get('Mount')[1]]["Name"] if
                 v.get('Mount') and type(v.get('Mount')[0]) == int
                 else "-"),
                (mount_list[v.get("Mount")[0]]["Name"]
                 if v.get('Mount') and type(v.get('Mount')[0]) == int
                 else "-"),
                (mount_armour_list[v.get("Mount")[2]]["Name"]
                 if v.get('Mount') and type(v.get('Mount')[0]) == int
                 else "-")
            ),

            "skill": [troop_skill_list[int(v.get('Charge Skill'))]["Name"] if v.get('Charge Skill') else "-"] +
                     [leader_skill_list[item]["Name"] for item in v.get('Skill')],
            "trait": v.get('Trait'),
            "formations": v.get('Formation'),
            "type": v.get('Type'),
            "size": v.get('Size'),
        }

        leaders.append(leader)

        subunit_icon_server_path = os.path.join(main_dir, "web wiki", "static", "{0}.png".format(k))
        subunit_icon_web_path = "static/{0}.png".format(k)
        leader['icon'] = [subunit_icon_web_path, k]

        if not os.path.isfile(subunit_icon_server_path):
            try:
                subunit_icon = get_subunit_icon(k, 35)
                pygame.image.save(subunit_icon, subunit_icon_server_path)
            except Exception as e:
                pass
                # raise e

    return render_template("leaders.j2", leaders=leaders)

app.run(debug=True)
