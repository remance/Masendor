![alt text](https://github.com/remance/Masendor/blob/master/pygamelogo.gif?raw=true)

![alt text](https://github.com/remance/Masendor/blob/master/preview.png?raw=true)

Historical wargame simulation made with Pygame. There is no main name for the game but rather the name will be based on major update. 
The current code structure and documentation follows no standard guideline whatsoever, so read and confuse at your own risk (until end of ver 0.5).

To start testing the game run main.py or main.exe if you use the release version.

Check the requirements.txt file for dependency requirement. Also the game is now optimised basing on pygame 2 module (much faster than 1.9.6) and python 3.7.9.

For Video update: https://www.youtube.com/channel/UCgapwWog3mYhkEKIGW8VZtw

If anyone is interested in similar game like this, there is also another interesting game by another developer: https://kaetjaatyy.github.io/devlog/

The current state of the game and code performance/readibility: ![alt text](https://github.com/remance/Masendor/blob/master/gamestate.png?raw=true)

Meaning: It's playable but it is still a bloody mess. More work to do.

Plan

Ver 0.6 Dream Decision: multiple unit selection/move logic, Battle selection(with different estimation source), preparation and result screen, custom battle, custom unit editor, improve main menu, Battle of Megiddo, Battle of Mohács

0.6: improve main.py (mainmenu) with update on code and comment, add intro screen

0.6.1: start working on Battle of Megiddo

0.6.2: battle selection screen, with team selection and battle estimation source setting

0.6.3: preparation and battle result screen, add battle situation (colour bar to compare 2 team strength) in ui somewhere

0.6.4: custom battle start working on Battle of Mohács

0.6.5: in game custom unit editor

0.6.6 and 0.6.7: random map generator

0.6.8 and 0.6.9: multiple unit selection/move, also add border to selected unit on army selector ui

Ver 0.7 Future Visionary: Fog of War(maybe), unit form, Dismount/discard, hidden stat, line of sight, battalion information based on hidden vs sight, raise flag/ light torch and recon command, ambush bonus, daynight, Battle of Walaja, Battle of Dorylaeum

Ver 0.8 Authentic Attraction: In game art, better looking UI (All hand (and mouse) drawn except for historical image), Battle of Isandlwana, Battle of Hwangsanbeol

Ver 0.9 Gaze of New Life: AI and pathfinding (The most challenging step unless cut corner to the point of braindead AI), final code optimisation before full 1.0

Ver 1 Pax Paradisum: historical battle simulation game, Battle of Waterloo, Battle of Dunsinane, Battle of Yijing, Battle of Jengland

Ver 1 - 1.5: More art, sound effect and ingame music (May need to use royalty free music since I have no experience in music) + Ingame Encyclopedia at main menu + more historical battles

Ver 1.1: Add dynamic terrain/feature change based on battle effect (damage) and weather

Ver 1.2: Siege battle, more complex unit equipment (main hand/off hand, item)

Ver 1.3: Deception, False information, scout, espionage warfare, information

Ver 1.6: Commander, strategist and leader duel with dynamic result and event (Move from 0.2.7 as it is not main priority in the early battle sample yet), transfer leader, Battle of Gaixia

ver 1.7: leader rapport and affect on authority and control mechanic including surrender and betrayal 

Ver 1.8: Deployable Defence (Stakes, Barrier, Camp, Wagon), dynamic squad facing position and maybe "saved" formation that player can rotate in battle, swapable squad position

Ver 1.9: Naval battle

Unforeseenable future: forced march (Moved here from 0.2.7 as this feature won't have much used until game map become much larger than just a single battlefield), Queue command, order dalay?

For those who have read this far, thank you for your interested in the game. To be honest, every single update begin with how do I even start with this. 
I start developing this game with zero knowledge in video game development let alone how to use pygame. I start learning how to use pygame by tinkering 
with alien.py in pygame examples folder and keep testing/changing it until it become what you can see right now (I keep most video update on youtube 
which show the progress of improvement almost from the start). All of the plan I list for the future is the same. I have no idea how to do it, the only 
thing I have is the picture of what I want to make it look like. Nevertheless, it is fun figuring stuff out and don't let the lack of knowledge stop 
you making your own game :P. 