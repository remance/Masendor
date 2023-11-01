<div align="center">    
    <img src="https://github.com/remance/preview/blob/main/pygamelogo.gif?raw=true" alt="Pygame Logo">
</div>

![alt text](https://github.com/remance/preview/blob/main/preview.gif?raw=true)

# Victores et Victos

## Educational and historical battle simulation made with [Pygame](https://github.com/pygame/pygame).

The development for this game is currently on hold. Minor updates and bugs fixed will still be done but expect no major progress for now. 
For any suggestions or bugs, feel free to report them in the [**Issues**](https://github.com/remance/Masendor/issues)
page.

Discord channel: [![github](https://github.com/remance/preview/blob/main/discord_logo.png?raw=true)][1]

For game update showcase video: [![github](https://github.com/remance/preview/blob/main/youtube_logo3.png?raw=true)][2]

---------------

# Contribution to development

All helps, suggestions, and issue reports are appreciated.

If you would like to help the project, feel free to join discord for a chat, open issues, commit the codes and do pull requests, or send emails to 
`masendor@proton.me`.

Some non-specific suggestions and examples of helps, including but not limited to:

- **Programming**: New features, improve current ones, code optimisation/improvement
- **Asset Creation**: UI, troop, leader, effect art, sound effect, music
- **Historical stuffs**: Battle information, writing, sources, correction, improvements
- **Quality Assurance**: Code documentation, game balancing, bugs fix, feedbacks

Note: All the new and current untested development are done on "dev" branch. The main branch is for a somewhat stable version of the game.

The repository history was cleanup from update 0.7.1.9 for the preserved history see: https://github.com/remance/Masendor-backup

---------------

# Index

- [How to run/compile](#how-to-runcompile)
    - [Run](#run)
    - [Compile](#compile)
- [Latest Update](#latest-update)
- [Key features so far](#key-features-so-far)
    - [History is told by the victor, but sometimes the words of the defeated do not fade away](#history-is-told-by-the-victor-but-sometimes-the-words-of-the-loser-do-not-fade-away)
    - [Army is led by more than just a king](#army-is-led-by-more-than-just-a-king)
    - [Complex troop Statistic System](#complex-troop-statistic-system)
    - [Custom Unit Creator](#custom-unit-creator)
    - [Extremely easy map creation](#extremely-easy-map-creation)
    - [Encyclopedia and stuff](#encyclopedia-and-stuff)
- [Future Plan](#future-plan)

---

# How to run/compile

If you want to download the release version to test the game, go
to [Release](https://github.com/remance/Masendor/releases) tags and [**
download**](https://github.com/remance/Masendor/releases/download/0.6.2.3/Dream.Decision.zip) the zip file. <br>

## Run

To start testing the game run `main.py` via Python interpreter for the source code or `main` file directly for the
release version. <br>

## System Requirements

### MINIMUM:

OS: Windows 7 (Haven't tested on Windows XP or Vista but may work), Ubuntu and macOS need further testing

Memory: 2GB RAM

Processor: Need more testing

Graphics: Need more testing

Storage: Currently 200 MB but likely around 500 MB available space in finished version.

### RECOMMEND:

OS: Windows 8, Ubuntu 22.04, macOS Monterey

Memory: 4GB RAM

Processor: Need more testing

Graphics: Need more testing

Storage: 1GB available space

## Compile

To compile the source code into an executable program, recommend using pyinstaller and `main.spec`. <br>

Check the [`requirements.txt`](requirements.txt) file for dependency requirements if running with the python source
code.<br>
Also, the game is now optimised based on the pygame-ce 2.2.1 module and python 3.11. (may have to use cython later for a
huge size battle)

---------------

# Latest Update

![alt text](https://github.com/remance/preview/blob/main/preview.png?raw=true)

[![](https://markdown-videos-api.jorgenkh.no/youtube/iHYlqnlIEOE)](https://youtu.be/iHYlqnlIEOE)

Add new game art style and system that allow player to select available styles.

---------------

# Key features so far

## History is told by the victor, but sometimes the words of the loser do not fade away

> 14th October 1066 AD, Duke William of Normandy’s force arrived at Telham Hill early in the morning, while Harold
> Godwinson’s force was already positioned at Senlac Ridge. It is believed that Harold intent to ambush William's army at
> their camp and was surprised by William's arrival at Telham Hill.

> 14th October 1066 AD, King Harold Godwinson intercepted William the Bastard’s force at Senlac Ridge, Hastings. The
> rightful king of England refused to cover in a castle before the pretender and bravely marched his army to crush the
> enemy head-on.

Have you ever found it weird that most historical games follow only a specific version of the story? Even a single battle may have more than one side of the story. 

For example, the Normans say they are the underdog in the Battle of Hastings, while the Saxons also say they are the underdog. 
Well in this game, all versions of the story are accepted and represented. 
Every preset historical map will have more than 1 source of information that dictates the story tone, army composition, size, even formation and possibly more.

![Image showing information about the Battle of Hastings](https://github.com/remance/preview/blob/main/source.gif?raw=true)

## Army is led by more than just a king
 
Troops in each army can be led by multiple leaders with chain of command and every
historical battle will have all the named people that participated in the battle.

![alt text](https://github.com/remance/preview/blob/main/leader.gif?raw=true)

[//]: # ()
[//]: # (## Custom Unit Creator)

[//]: # ()
[//]: # (Bored of a simple line formation and want to try making weird unit formation? There is a custom unit editor that)

[//]: # (provides a complete freedom unit design. The custom units can be used in custom battles.)

[//]: # ()
[//]: # (![alt text]&#40;https://github.com/remance/preview/blob/main/custom.gif?raw=true&#41;)

## Extremely easy map creation

Map creator in most games requires a degree of learning to use effectively. In this game, you just need to use MS Paint or any drawing software
([GIMP](https://www.gimp.org/), [Adobe Photoshop](https://www.adobe.com/products/photoshop.html), etc.) to create a map.<br>

Draw the image with the right colour set, and the game will convert them into a playable map. Most other map functions
are also very easy to create and modify.

[Video](https://www.youtube.com/watch?v=8Omm-o6Dy60) demonstration: https://www.youtube.com/watch?v=8Omm-o6Dy60

## Encyclopedia and stuffs

This game's encyclopedia will have more information than just from the Wikipedia website as long as they can be found
that is.

![alt text](https://github.com/remance/preview/blob/main/lore.gif?raw=true)

This function is going to be a headache to write and research. But hopefully, it will provide useful and interesting historical information to players.


## Tools

### Animation maker

Animation maker for the troop Vector-based animation in game. The tool is made with pygame and the code is compatible enough for other purposes with some modification.

![alt text](https://github.com/remance/preview/blob/main/animation%20maker.png?raw=true)

### Photo studio

Photo studio to make battle screen to your liking. Simply add subunit and effect data and the tool will render them. 

![alt text](https://github.com/remance/preview/blob/main/studio.png?raw=true)

---------------

# Credit

[//]: # (## Programming)

## Tool

### Subunit sprite viewer by coppermouse (https://github.com/coppermouse)

## Game Asset

### Graphic Art:

- Ryu Hill (Mystika Digital Media)

### Sprite:

- Prototype slash effect sprites by inogNate
- Weapon sprite by jeet

### Sound (Obtained and edited):

- Musket shot "aaronsiler_musket 3", "aaronsiler_musket 4" by aaronsiler (https://freesound.org/people/aaronsiler/)
- Assorted weapon sound from Videvo (https://www.videvo.net/)
- Cannon sound "canon" from man (https://freesound.org/people/man/)
- Cannonball sound effect "Real Cannonballs Flying By (Restored Audio)" from John Camara (https://www.youtube.com/watch?v=maVSnWIXGE8)
- Bullet sound "Bullet passbys" from Audionautics (https://freesound.org/people/Audionautics/)
- Heavy rain weather ambient sound "Heavy Rain", weapon sound "Wooshes" by lebaston100 (https://freesound.org/people/lebaston100/)
- Heavy Weapon swing by "Swinging staff whoosh (strong) 08" Nightflame (https://freesound.org/people/Nightflame/)
- Sword swing "Swosh Sword Swing" by qubodup (https://freesound.org/people/qubodup/)
- Sword swing "swordslash" by deleted_user_13668154 (https://freesound.org/people/deleted_user_13668154/)
- Spear pierce "Wooshs 01" by toyoto (https://freesound.org/people/toyoto/)
- Hammer swing "Whoosh Heavy Spear Hammer Large" by EminYILDIRIM (https://freesound.org/people/EminYILDIRIM/)
- Big warhorn "BIG-REVERB-WARHORN" by newagesoup (https://freesound.org/people/newagesoup/)
- Warhorn "Battle horn 1" by kirmm (https://pixabay.com/sound-effects/battle-horn-1-6931/)
- Bow drawing "SHOOTING_ARROW_SINGLE_ARCHERY_FOLEY_02" by JoeDinesSound (https://freesound.org/people/JoeDinesSound/)
- Bow drawing "Regular Arrow Shot distant target" by brendan89 (https://freesound.org/people/brendan89/)
- Javelin, throwing axe, stone sound effect by freeSFX (https://freesfx.co.uk/)
- Crossbow shot "bow02" by Erdie (https://freesound.org/people/Erdie/)
- Crossbow shot "Crossbow Firing and Hitting Target" by Ali_6868 (https://freesound.org/people/Ali_6868/)
- Heavy damaged "Blam" by Loghome72 (https://freesound.org/people/Loghome72/)
- Knockback "punch" by Ekokubza123 (https://freesound.org/people/Ekokubza123/)
- Damaged "punch3" by Merrick079 (https://freesound.org/people/Merrick079/)
- Test menu music"The Britons" by kmacleod (https://pixabay.com/users/kmacleod-3979860/)
- Battle music "Medieval: Battle" by RandomMind (https://www.chosic.com/free-music/all/?keyword=RandomMind&artist)
- Battle music 2 "War Drums Sound Effect - Realistic Performance - Royalty Free" by Free Audio Zone (https://www.youtube.com/watch?v=d2omr4EpjVc)


## Translation

### Ukrainian Translation:

- JerryXd

## Help with game coding and bugs fixed:

-  coppermouse (https://github.com/coppermouse)
- shawarmaje
- legotrainkid
- Hamster_Lord
- Ryu Hill (Mystika Digital Media)

---------------

# Future Plan

**Ver 0.7 Future Visionary:** custom unit and troop editor, march sound system, keybinding, loading screen,
England Campaign

**0.7 and 0.7.1:** console stick, control key binding

**0.7.2 and 0.7.3:** Companion system

**0.7.4 to 0.7.6:** custom unit editor and march sound system

**0.7.7:** custom troop editor

**0.7.8 and 0.7.9:** specific Leader command, loading screen, Minor battle: 764 Irish
abbey war

**Ver 0.8 Authentic Attraction:** In-game art, better-looking UI, add intro screen, Egypt Campaign

**0.8 and 0.8.1:** Rework ranged attack bullet system to include height calculation

**0.8.2 and 0.8.3:** Improve UI art

**Ver 0.9 Gaze of New Life:** AI and pathfinding (The most challenging step unless cut corner to the point of braindead
AI), Ottoman Campaign, final code optimisation before full 1.0

**Ver 1 Pax Paradisum:** Release version, historical battle simulation game

**Ver 1 - 1.5:** More art, sound effects and in-game music (May need to use royalty-free music but will see) + Ingame
Encyclopedia at main menu + more historical battles

**Ver 1.1:** Add dynamic terrain/feature change based on battle effect (damage) and weather

**Ver 1.2:** Urban map, Siege battle and siege equipment, Minor battle: Wolf of Paris

**Ver 1.3:** hidden stat, line of sight, raise flag/ light torch, ambush bonus

**Ver 1.6:** Commander mode, strategist and leader duel with dynamic result and event (Move from 0.2.7 as it is not the main
priority in the early battle sample yet), transfer leader, Battle of Gaixia

**Ver 1.7:** Deception, False information, scout, espionage warfare, information, Minor battle: Siege of Orleans

**Ver 1.8:** Deployable Defence (Stakes, Barrier, Camp, Wagon), dynamic squad facing position and maybe "saved"
formation that player can rotate in battle, swappable squad position

**Ver 1.9:** 

**Ver 2.0:** Multiplayer battle

**Ver 2.1:** Begin working on another module setting

**Unforeseeable future:** forced march (Moved here from 0.2.7 as this feature won't have much used until the game map
become much larger than just a single battlefield), Queue command

---------------

For those who have read this far, thank you for your interest in the game. To be honest, every single update begins with
how do I even start with this.

I start developing this game with zero knowledge in video game development let alone how to use pygame. I start learning
how to use pygame by tinkering with `alien.py` in the pygame `examples` folder and keep testing/changing it until it became
what you can see right now (I keep most video updates on YouTube which show the progress of improvement almost from the
start). All of the plans I list for the future are the same. I have no idea how to do it, the only thing I have is the
picture of what I want to make it look like. Nevertheless, it is fun figuring stuff out and don't let the lack of
knowledge stop you from making your own game :P.


[1]: https://discord.gg/q7yxz4netf

[2]: https://www.youtube.com/channel/UCgapwWog3mYhkEKIGW8VZtw

