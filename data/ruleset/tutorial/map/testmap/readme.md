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

ID: game id of unit, int number

Row *number* (e.g., Row 1): sub-unit list row of any specific number of maximum row according to the genre setting, for example int,int,int,int,int,int,int,int (No space), 0 number means empty and note that whole empty row or column will be removed in game. Some genres accept string "h" as indication of leader as subunit

POS: starting position in map of the unit, int,int

Leader: Number or list of leader id number depending on genre setting, int or int,int,int,int. In case of list 0 means empty.

Leader Position: Mean different thing depending on genre mode, army position of leader. Or position of subunit that leader is attached to, do not put multiple leader into same subunit except empty leader. Leader position does not count 0 subunit in position row, for example row 1 of 1,2,5,1,0,9 position 5 will attach leader to the sixth subunit 9. 

Faction: Faction ID (not team), int number 

Angle: starting angle of the unit, int number

Start Health: int number between 1 and 100 can be outside the range but may cause issue, used as percentage

Start Stamina: int number between 1 and 100 can be outside the range but may cause issue, used as percentage

Team: Team number, int number
 
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
