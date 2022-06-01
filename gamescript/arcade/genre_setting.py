"""For keeping variable related to genre specific"""

char_select = True  # include character specific screen
troop_sprite_size = (250, 250)  # troop animation sprite size
start_zoom = 10  # start with the closest zoom
start_zoom_mode = "Follow"  # one character control camera
leader_sprite = True  # leader has its own animation sprite
unit_size = (5, 5)  # maximum array size unit can contain subunits
time_speed_scale = 30  # how fast time fly in battle
troop_size_adjustable = True  # troop always at size 1
add_troop_number_sprite = False  # troop number sprite not use in arcade mode
dmg_include_leader = False  # include leader in damage calculation, not used in arcade mode since leader is subunit itself
stat_use_troop_number = False  # arcade mode count one subunit as one troop

unit_behaviour_wheel = {"Main": ("Skill", "Shift Line", "Range Attack", "Behaviour",
                                 "Command", "Formation", "Equipment", "Setting"),
                        "Skill": ("Leader Skill 1", "Leader Skill 2", "Troop Skill 1", "Troop Skill 2"),
                        "Shift Line": ("Front To Back", "Left To Right", "Back To Front", "Right To Left"),
                        "Range Attack": ("Manual Aim", "Fire At Will", "Volley", "Manual Only"),
                        "Behaviour": ("Hold", "Follow", "Free", "Retreat"),
                        "Command": ("Offensive", "Defensive", "Skirmish", "Protect Me",
                                    "Follow Unit", "Free", "Hold Location", ""),
                        "Formation": ("Square", "Vert Line", "Circle", "Wedge", "Hori Line", "Original",
                                      "Melee Front", "Range Front"),
                        "Equipment": ("Equip Primary", "Equip Secondary", "Troop Primary", "Troop Secondary",
                                      "Troop Melee", "Troop Range"),
                        "Setting": ("Height Map", )}  # player unit behaviour control via wheel ui

# Default keyboard binding
up = "w"
down = "s"
left = "a"
right = "d"
command_menu = "q"
leader_skill = "r"
troop_skill = "t"
map_mode = "tab"
action_0 = "left mouse button"
action_1 = "right mouse button"

# Default controller binding
controller_up = "w"
controller_down = "s"
controller_left = "a"
controller_right = "d"
controller_command_menu = "q"
controller_leader_skill = "r"
controller_troop_skill = "t"
controller_map_mode = "tab"
controller_action_0 = ""
controller_action_1 = ""
