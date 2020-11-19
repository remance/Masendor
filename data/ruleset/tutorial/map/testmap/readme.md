The map data in its folder consists of two main components as follows;

Map image (should only be in png format and 1000x1000 size)

- base: The image of base climate of the map. Do not use colour other than the designated one or use brush tool that cause colour to be uneven.  

- feature: The image of terrain feature of the map. Same as base, using colour not desinated in terrain data will cause error.

- height: The image of terrain height of the map (the colour RGB should be (255(Fixed), G (adjustable), G (same number as Green))). The darker the red colour, the higher the height.

- placename: The image of location name of the map. This data is for cosmetic purpose only but must be in full transparent base image. 


Read Mapguide.doc for more detailed information


Map data

- info: Information of the map that will be shown in battle select menu

- unitpos: List of unit the csv data structure is as follows: 

unit id | sub-unit list row 1 | row 2 | row 3 | row 4 | row 5 | row 6 | row 7 | row 8 | start position | leader | leader position according to  | faction | start angle |

int	| 			int,int,int,int,int,int,int,int		      	      |    int,int     | int,int,int,int |int,int,int,int	| int     |    int	|

0+ = player  | (1 = None) Note that whole empty row or column will be removed in game |	no negative    |    (1 = None)  |  Do not put multiple leader into same sub unit except none leader |

2000+ = enemy |

- weather: 

- eventlog: 

