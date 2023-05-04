import sys
import os
import pygame
import hashlib
from flask import Flask, render_template, redirect, request
from collections import defaultdict

# ---
# to get this to work on my computer I acutal has to have this (I tested using both this current directory and the actual "main" directory
# as working directory and it does not work. /coppermouse
# This appends main directory to "sys.path" which makes it possible to import engine.
file_path = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
main_dir = os.path.normpath(os.path.join(file_path, '..'))
sys.path.append(main_dir)
# ---

from engine import utility  # nopep8
from engine.game.create_troop_sprite_pool import create_troop_sprite_pool  # nopep8
from engine.game.game import Game  # nopep8
from engine.game.setup.make_faction_troop_leader_data import make_faction_troop_leader_data  # nopep8
from engine.data import datasprite  # nopep8

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
        self.data_dir = os.path.join(self.main_dir, "data")
        self.screen_scale = (1, 1)
        self.module = 0
        self.module_list = csv_read(
            self.main_dir, "module_list.csv", ("data", "module"))
        self.module_folder = str(self.module_list[self.module][0]).strip("/").lower()
        self.module_dir = os.path.join(self.data_dir, "module", self.module_folder)
        self.language = 'en'

    def change_module(self):
        """
            Minified change module-method. Removed things that otherwise wouldn't allow
            the script to be able to run.
        """

        self.troop_data, self.leader_data, self.faction_data = make_faction_troop_leader_data(self.data_dir, self.module_dir, self.screen_scale, self.language)

        self.troop_animation = datasprite.TroopAnimationData(self.data_dir, self.module_dir,
                                                             [str(self.troop_data.race_list[key]["Name"])
                                                              for key in self.troop_data.race_list], self.team_colour)

        self.unit_animation_data = self.troop_animation.unit_animation_data
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
game.change_module()

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


def get_unit_icon(unit_id, scale, icon_size=None):
    """get a icon for a specific unit"""

    md5_input = "{0}${1}${2}".format(unit_id, scale, icon_size)
    hex_hash = hashlib.md5(md5_input.encode()).hexdigest()

    unit_icon_server_path = os.path.join(main_dir, "web-wiki", "static", "{0}.png".format(hex_hash))

    if not os.path.isfile(unit_icon_server_path):

        units = (game.troop_data.troop_list | game.leader_data.leader_list)
        who_todo = {key: value for key, value in units.items() if key == unit_id}

        # make idle animation, first frame, right side (change to l_side for left), non-specific so it can make for any troops
        try:
            preview_sprite_pool, _ = create_troop_sprite_pool(game, who_todo, preview=True, specific_preview=("Idle_0", 0, "r_side", "non-specific"),
                                                              max_preview_size=scale)
        except KeyError:
            return None
        except TypeError:
            return None

        sprite = preview_sprite_pool[unit_id]["sprite"]
        icon_size = sprite.get_size() if icon_size is None else icon_size
        icon = pygame.Surface(icon_size, pygame.SRCALPHA)
        icon.blit(sprite, (0, 0))

        pygame.image.save(icon, unit_icon_server_path)

    return "/static/{0}.png".format(hex_hash)


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

    faction_data = game.faction_data.faction_list

    region_no_leaders = defaultdict(int)
    region_no_troop_types = defaultdict(int)

    for leader in game.leader_data.leader_list.values():
        for faction in leader["Faction"]:
            region_no_leaders[faction_data[faction]["Type"]] += 1

    for troop in game.troop_data.troop_list.values():
        for faction in troop["Faction"]:
            region_no_troop_types[faction_data[faction]["Type"]] += 1

    regions = [
        {
            "id": region.lower().replace(" ", "-"),  # there is not such thing as an region id (yet?) so we have
            # to rely on the name (but make it more id-like)
            "name": region,
            "no-factions": len([1 for f in game.faction_data.faction_list.values() if f["Type"] == region]),
            "no-leaders": region_no_leaders[region],
            "no-troop-types": region_no_troop_types[region],
        }
        for region in sorted(regions)
    ]

    return render_template("regions.j2", regions=regions)


@app.route("/factions")
def factions():
    factions = list()

    faction_no_leaders = defaultdict(int)
    faction_no_troop_types = defaultdict(int)

    for leader in game.leader_data.leader_list.values():
        for faction in leader["Faction"]:
            faction_no_leaders[faction] += 1

    for troop in game.troop_data.troop_list.values():
        for faction in troop["Faction"]:
            faction_no_troop_types[faction] += 1

    for k, v in game.faction_data.faction_list.items():
        if k != 0:  # skip all faction
            faction = {
                "id": k,
                "name": v["Name"],
                "icon": make_faction_icon_and_return_web_path(k),
                "strengths": v["Strengths"],
                "weaknesses": v["Weaknesses"],
                "favoured-troop": v["Favoured Troop"],
                "region": v["Type"],
                "no-leaders": faction_no_leaders[k],
                "no-troop-types": faction_no_troop_types[k],
            }
            factions.append(faction)

    factions.sort(key=lambda a: a["name"])

    return render_template("factions.j2", factions=factions)


@app.route("/weapons")
def weapons():

    # modifies the key-strings because I think it looks better in jinja template.
    weapons = list()
    for k, v in weapon_list.items():
        weapon = {k2.lower().replace(" ", "-"): v2 for k2, v2 in v.items()}
        weapons.append(weapon)

    return render_template("weapons.j2", weapons=weapons)


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

        unit_icon = get_unit_icon(k, 35, (36, 36))
        troop['icon'] = [unit_icon, k]

    return render_template("troops.j2", troops=troops)


def make_faction_icon_and_return_web_path(faction_id):
    import random
    md5_input = "faction-icon:{0}".format(faction_id)
    hex_hash = hashlib.md5(md5_input.encode()).hexdigest()

    faction_icon_server_path = os.path.join(main_dir, "web-wiki", "static", "{0}.png".format(hex_hash))

    size = 31  # size each dimension
    margin = 4  # on all sides
    extra_width = 5  # on each side

    if not os.path.isfile(faction_icon_server_path) or 1:  # or 1 in this makes it random every refresh. when there is no more random remove this 'or 1'

        coa = game.faction_data.coa_list[faction_id]
        scale = min((size/coa.get_size()[i]) for i in range(2))
        cfs = coa_fit_scaled = pygame.transform.smoothscale(coa, [c*scale for c in coa.get_size()])

        icon_surface = pygame.Surface((size+margin*2+extra_width*2, size+margin*2))

        icon_surface.fill(random.randrange(256**3))
        icon_surface.blit(cfs, (
            (size - cfs.get_size()[0])/2+margin+extra_width,
            (size - cfs.get_size()[1])/2+margin
        ))

        frame = pygame.Surface(icon_surface.get_size(), pygame.SRCALPHA)
        frame.fill((0, 0, 0, 128))
        pygame.draw.rect(frame, (0, 0, 0, 24), (1, 1, size+(extra_width+margin-1)*2, size+(margin-1)*2))
        pygame.draw.rect(frame, (0, 0, 0, 0), (2, 2, size+(extra_width+margin-2)*2, size+(margin-2)*2))
        icon_surface.blit(frame, (0, 0))
        pygame.image.save(icon_surface, faction_icon_server_path)

    return "/static/{0}.png".format(hex_hash)


@app.route("/leaders")
@app.route("/leaders/<leader_id>")
def leaders(leader_id=None):

    # single leader view
    if leader_id is not None:

        data = game.leader_data.leader_list[leader_id]
        lore = game.leader_data.leader_lore[leader_id][1:]
        image = game.leader_data.images[leader_id].convert_alpha()

        # TODO: this is temp solution, no need to save it everytime
        # and we also might alter the image somehow in the future
        leader_image_server_path = os.path.join(main_dir, "web-wiki", "static", "leader_{0}.png".format(leader_id))
        pygame.image.save(image, leader_image_server_path)

        leader_name = data["Name"]
        sprite_icon = get_unit_icon(leader_id, 140, None)

        return render_template(
            "leader.j2",
            name=leader_name,
            lore=lore,
            sprite_icon=sprite_icon,
            image="/static/leader_{0}.png".format(leader_id),
        )

    faction = request.args.get("faction")
    header = "Leaders"

    if faction is None:
        _filter = None
    else:
        _filter = {k for k, v in game.leader_data.leader_list.items() if int(faction) in v["Faction"]}
        header = "Leaders of {0}".format(game.faction_data.faction_list[int(faction)]["Name"])

    # list leaders view
    leaders = list()
    for k, v in game.leader_data.leader_list.items():

        if _filter is not None:
            if k not in _filter:
                continue

        leader = {
            "id": k,
            "name": v["Name"],
            "faction": ", ".join([faction_data["Name"] for faction_id, faction_data in game.faction_data.faction_list.items() if faction_id in v["Faction"]]),
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

        unit_icon = get_unit_icon(k, 44)
        leader['icon'] = [unit_icon, k]

    return render_template("leaders.j2", leaders=leaders, header=header)


app.run(debug=True)
