The map data in its folder consists of two main components as follows;

Map image (should only be in png format and 1000x1000 size)

- base: The image of base climate of the map. Do not use colour other than the designated one or use brush tool that cause colour to be uneven.  

- feature: The image of terrain feature of the map. Same as base, using colour not desinated in terrain data will cause error.

- height: The image of terrain height of the map (the colour RGB should be (255(Fixed), G (adjustable), G (same number as Green))). The darker the red colour, the higher the height.

- placename: The image of location name of the map. This image is for cosmetic purpose only but must be in full transparent base image. 

Read data\map\Mapguide.doc for more detailed information on colour combination of terrain and feature and some other recommendation

Map data

- info: Information of the map that will be shown in battle select menu, also used to find faction involve in battle as team

- source: Source list of this map, unit troop scale and description

- musicevent: the list of all music event that will occur during the battle. Empty or not existed file will play random custom map music.

Inside each map source folder

- unit_pos(with source number after, e.g. unit_pos0 or unit_pos5): List of unit the csv data structure is as follows: 

unit id | sub-unit list row 1 | row 2 | row 3 | row 4 | row 5 | row 6 | row 7 | row 8 | start position | leader | leader position according to  | faction (not team) | start angle | start health state | start stamina state | team

int	| 		int,int,int,int,int,int,int,int			    	      |    int,int     | int,int,int,int |int,int,int,int	| int     |    int	| int (0-100) 	     | int (0-100) |

no nagative | (1 = None) Note that whole empty row or column will be removed in game |	no negative    |    (1 = None)  |  Do not put multiple leader into same sub unit except none leader | leader position does not count 0 sub-unit in position row

- weather: the list of all weather event that will occur during the battle. The structure is as follows;

weatherid (see data/map/weather) | time the weather activiate and end of previous weather | weather level (0 = Light, 1 = Normal, 2 = Strong)

- eventlog: the list of all event that will appear on eventlog during the battle. Will add more detailed implementation later, still in process of development. modelist is the eventlog tabs that the event will appear (0=war,1=army(unit),2=leader,3=unit(sub-unit))

Currently only 23 types of event: t+number (e.g.t10) for event that appear at time input in time column, ld+number (ld0 for player, ld1 for enemy) for the first commander death event. wt+teamnumber (e.g.wt1 for team 1 win) for victory event.

Both activate time in both weather and eventlog can be done for multiple days battle. If the even is sparse simply add pointless event at 23:59:59 to indicate the end of the day. For examples;

Weather:

sunny 10:00:00 <- day 1

sunny 23:59:59 <- end day 1

rain 10:00:00 <- day 2

Eventlog:

"Ok bye" 10:00:00 <- day 1

"End of day 1" 23:59:59 <- end day 1

"Ok hi" 10:00:00 <- day 2
