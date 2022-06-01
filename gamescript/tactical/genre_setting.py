"""For keeping variable related to genre specific"""

char_select = False  # include character specific screen, tactical mode player control various unit
troop_sprite_size = (200, 200)  # troop animation sprite size
start_zoom = 1  # start with the furthest zoom
start_zoom_mode = "Free"  # rts style camera
leader_sprite = False  # leader has its own animation sprite, tactical mode use subunit sprite only
unit_size = (8, 8)  # maximum array size unit can contain subunits
time_speed_scale = 10  # how fast time fly in battle
troop_size_adjustable = False  # troop always at size 1
add_troop_number_sprite = True  # add troop number sprite
dmg_include_leader = False  # include leader in damage calculation
stat_use_troop_number = True  # calculate troop number in damage calculation

unit_behaviour_wheel = {}  # player unit behaviour control via wheel ui, not used in tactical mode as it use different control and ui

event_log_top = "page up"
event_log_bottom = "page down"
increase_game_time = "keypad plus"
decrease_game_time = "keypad minus"
pause_game_time = "p"
toggle_unit_number = "o"

up = "w"
down = "s"
left = "a"
right = "d"
command_menu = "q"
leader_skill = "r"
troop_skill = "t"
map_mode = "tab"
action_1 = "left mouse button"
action_2 = "right mouse button"
