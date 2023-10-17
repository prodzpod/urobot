from dataclasses import dataclass, field
from collections import deque
import sys
import random
import datetime
# simple brute force algorithm to find the longest map chain / deepest world

# DATA CLASSES

@dataclass
class Map:
    name: str
    required: set[str] = field(default_factory=set) # list of effect that are REQUIRED TO ENTER
    effect: set[str] = field(default_factory=set) # list of effects that CAN BE GOTTEN
    luck_based: bool = False
    anti_required: set[str] = field(default_factory=set) # list of "effects" that MUST NOT BE GOTTEN

@dataclass
class Connections:
    game_name: str
    player_name: str # also default player name
    fast_effect: str
    start_point: int
    simple_effects: dict[str]
    maps: dict[Map]

@dataclass
class Player:
    current_map: str
    effect: set[str] = field(default_factory=set)
    path: list[str] = field(default_factory=list)
    point: int = 0 # the target
    def __hash__(self):
        return hash((self.current_map, frozenset(self.effect), tuple(self.path), self.point))

def Maps(*maps):
    return list(map(lambda s: Map(s), maps))

# DATA

CONNECTIONS = {
    "yume": Connections("Yume Nikki", "Madotsuki", "Bicycle", -1, {}, {}),
    "2kki": Connections("Yume 2kki", "Urotsuki", "Bike", -3, {}, {
    "Urotsuki's Room": [Map("Urotsuki's Dream Balcony"), Map("Developer Room", {"Ending #1", "Ending #2", "Ending #3", "Ending #4"})],
    "Developer Room": [Map("Urotsuki's Room")],
    "Urotsuki's Dream Balcony": [Map("Urotsuki's Dream Room", set(), {"Summer"}), Map("Urotsuki's Dream Room", set(), {"Autumn"}), Map("Urotsuki's Dream Room", set(), {"Winter"})],
    "Urotsuki's Dream Room": Maps("Urotsuki's Dream Balcony", "The Nexus") + [Map("Mirror Room", set(), set(), True)],
    "Mirror Room": [Map("Old Train Station B", {"Fairy"}), Map("Old Train Station B", {"Child"})],
    "Sofa Room": Maps("Mirror Room"), 
    "The Nexus": Maps("Pudding World", "Urotsuki's Dream Room", "Purple World", "Red Streetlight World", "Library", "Marijuana Goddess World", "Mushroom World", "Toy World", "Shield Owl World", "Cipher Keyboard", "Rock World", "Bacteria World", "Lamp Puddle World", "Ornamental Plains", "Deep Red Wilds") + [Map("Trophy Room", {"Trophy Room"}), Map("Oil Puddle World", {"Ending #1"}), Map("Blue Eyes World", {"Glasses"}), Map("Forest World", set(), {"Lantern"}), Map("Garden World", set(), {"Bike"}), Map("Heart World", set(), {"Crossing"}), Map("Graveyard World", set(), {"Gravestone"}), Map("Geometry World", set(), {"Boy"}), Map("Portrait Purgatory", set(), {"Bike"}), Map("Urotsuki's Dream Apartments", set(), {"Penguin"})],
    "Purple World": Maps("The Nexus", "Highway", "The Hand Hub", "Red Monastery") + [Map("Onyx Tile World", set(), {"Drum"}), Map("Garden World", set(), {"Bike"}), Map("Black Building", set(), {"Fairy"})],
    "Red Streetlight World": Maps("The Nexus", "Gray Road", "Red City", "Monochrome Street", "Magnet Room", "Bridged Swamp Islands", "Red Rock Caves", "Bleeding Heads Garden", "Amorphous Maroon Space", "Hot Air Balloon World", "Dark Bunker", "Knife World", "Ephemeral Barrens", "Port City", "Reef Maze"),
    "Library": Maps("The Nexus", "Word World", "Maiden Outlook") + [Map("Apartments", {"UFO"}), Map("Character Plains", set(), set(), True), Map("Eyeball Archives", {"Glasses"}, {"Bunny Ears"}), Map("Tricolor Room", set(), {"Picture Book", "Yellow Note"})],
    "Marijuana Goddess World": Maps("The Nexus", "Color Cubes World", "Maiden Outlook", "Rainbow Hell") + [Map("Lotus Park", {"Twintails"}), Map("Dark Room", set(), {"Telephone"})],
    "Urotsuki's Dream Apartments": Maps("The Nexus", "Trophy Room", "Dressing Room", "Simple Street", "Magnet Room", "Unending River") + [Map("Tricolor Room", set(), {"Yellow Note"}), Map("Portrait Collection", set(), set(), True), Map("Stone Maze", set(), {"From Dream Apartments"}), Map("Silent Sewers", {"Silent Sewers"}), Map("Solstice Forest", {"Rainbow Ruins"})],
    "Forest World": Maps("The Nexus", "Underground TV Complex", "Astral World") + [Map("Chocolate World", {"Cake"}, {"Chocolate World"}), Map("Chocolate World")],
    "Garden World": Maps("The Nexus", "Snowy Apartments", "Blue Forest", "Inu-san's Psyche", "Blue Sanctuary") + [Map("The Hand Hub", set(), set(), True), Map("Art Gallery", set(), set(), True), Map("Board Game Islands", {"Child"}, set(), True), Map("Hospital", set(), {"Chainsaw"})],
    "Mushroom World": Maps("The Nexus", "Elvis Masada's Place", "Bug Maze", "Forlorn Beach House", "Ice Cream Dream", "Vibrant Mushroom World") + [Map("White Fern World", set(), {"Tissue"})],
    "Heart World": Maps("The Nexus", "Valentine Land", "Spherical Space Labyrinth") + [Map("The Deciding Street", set(), {"Twintails"}), Map("Tricolor Passage", set(), {"Red Path"}), Map("Cipher Fog World", {"Crossing", "Dream Park"})],
    "Geometry World": Maps("The Nexus", "Saturated Eyeball Zone", "Mossy Stone Area", "Vibrant Mushroom World", "Stone World", "Intestines Maze") + [Map("Broken Faces Area", set(), {"Marginal"}), Map("Dark Museum", set(), {"Glasses"}), Map("Sound Saws World", {"Boy", "Dream Park"})],
    "Graveyard World": Maps("The Nexus", "Red Lily Lake") + [Map("Hospital", set(), {"Chainsaw"}), Map("Dream Park", {"Chainsaw", "Child", "Spring"}, {"Dream Park"})],
    "Toy World": Maps("The Nexus", "Day and Night Towers", "Red Brick Maze", "Wooden Block World", "Art Gallery", "Mini-Town") + [Map("Zodiac Fortress", {"Cake"})],
    "Shield Owl World": Maps("The Nexus", "Flooded Baths", "Clawtree Forest", "Water Lantern World", "The Pansy Path") + [Map("Bodacious Rotation Station", set(), {"Stretch"}), Map("Acerola World", set(), {"Dice"}), Map("NES Glitch Tunnel", {"Chainsaw"})],
    "Pudding World": Maps("The Nexus", "Orange Badlands", "Pillar Ark"),
    "Portrait Purgatory": Maps("The Nexus", "Pop Revoir", "Poseidon Plaza", "Sakura Forest", "Reverie Book Piles", "Basement of Oddities"),
    "Cipher Keyboard": Maps("The Nexus", "Despair Road", "Dream Bank", "Spaceship", "Void", "Amoeba Woods"),
    "Rock World": Maps("The Nexus", "Rainbow Tiles Maze", "Entomophobia Realm", "Sanctuary", "Vermilion Bamboo Forest") + [Map("Theatre World", set(), {"Rainbow"}), Map("Visine Spacecraft", {"Spacesuit"}, set(), True), Map("Starfield Garden", {"Glasses"})],
    "Bacteria World": Maps("The Nexus", "Microbiome World", "Color Capital"),
    "Lamp Puddle World": Maps("The Nexus", "Under-Around"),
    "Trophy Room": Maps("The Nexus"),
    "Oil Puddle World": Maps("The Nexus", "Digital Forest"),
    "Ornamental Plains": Maps("The Nexus", "Drains Theater") + [Map("Birch Forest", set(), {"Red Riding Hood"})],
    "Blue Eyes World": Maps("Flowerpot Outlands", "Restored Character World") + [Map("The Nexus", {"Glasses"})],
    "Deep Red Wilds": Maps("The Nexus", "Mask Folks Hideout", "Bleeding Mushroom Garden"),
    "Highway": Maps("Purple World", "Downfall Garden A", "Gray Road", "Neon Highway", "River Complex", "City Limits", "Dream Beach", "TV Room") + [Map("RGB Passage", {"Chainsaw"}, set(), True)],
    "Onyx Tile World": Maps("Downfall Garden B", "Fused Faces World", "White Black World"),
    "Black Building": Maps("Purple World") + [Map("Town Maze", {"Forest Pier"}), Map("Highway", set(), set(), True)],
    "The Hand Hub": Maps("Christmas World", "Bug Maze", "Shape World", "Dark Bunker") + [Map("Dizzy Spirals World", set(), set(), True), Map("Forlorn Beach House", set(), set(), True), Map("Maple Shrine", set(), set(), True), Map("Garden World", set(), {"Bike"}), Map("The Baddies Bar", {"Chainsaw"}, {"Trombone"}, True), Map("The Baddies Bar", {"Lantern"}, {"Trombone"}, True), Map("The Baddies Bar", {"Rainbow"}, {"Trombone"}, True), Map("The Baddies Bar", set(), set(), True), Map("Shinto Shrine", set(), {"Maiko"})],
    "Red Monastery": Maps("Purple World", "T-Folk World"),
    "Gray Road": Maps("Red Streetlight World", "Dark Forest", "Boogie Street", "Train Tracks", "Grass World", "Highway", "French Street", "Florist", "GALAXY Town", "Serene Docks") + [Map("Techno Condominium", {"Teru Teru Bozu"}), Map("Techno Condominium", set(), set(), True)],
    "Red City": Maps("Red Streetlight World", "Intestines Maze", "Head Wasteland"),
    "Monochrome Street": Maps("Red Streetlight World", "Mask Shop") + [Map("Red Brick Maze", {"Chainsaw"}), Map("Shinto Shrine", set(), {"Maiko"})],
    "Magnet Room": Maps("Red Streetlight World", "Intestines Maze") + [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})],
    "Bridged Swamp Islands": Maps("Red Streetlight World", "Cultivated Lands", "Rapeseed Fields") + [Map("Heian Era Village", {"Chainsaw"})],
    "Red Rock Caves": Maps("Red Streetlight World"),
    "Bleeding Heads Garden": Maps("Red Streetlight World", "Alien Valley"),
    "Amorphous Maroon Space": Maps("Red Streetlight World", "Unending River", "Black Sphere World"),
    "Hot Air Balloon World": Maps("Red Streetlight World", "Ninja Town") + [Map("Drowsy Forest", {"Ending #1"})],
    "Dark Bunker": Maps("Red Streetlight World", "The Hand Hub", "Spear Tribe World", "Blue Palm Road"),
    "Knife World": Maps("Red Streetlight World", "Server Hub"),
    "Ephemeral Barrens": Maps("Red Streetlight World"),
    "Port City": Maps("Red Streetlight World"),
    "Reef Maze": Maps("Red Streetlight World", "Lost Forest", "Halls"),
    "Word World": Maps("Library") + [Map("Integer World", {"Polygon"})],
    "Eyeball Archives": Maps("Library"),
    "Tricolor Room": [Map("Urotsuki's Dream Apartments", set(), {"Penguin"}, False, {"Picture Book"}), Map("Cloud Tops", set(), {"Crepuscule"}, False, {"Picture Book"}), Map("Silkworm Forest", {"Innocent Dream"}, set(), False, {"Picture Book"}), Map("Cloud Floor", {"Innocent Dream", "???"}, set(), False, {"Picture Book"}), Map("Library", {"Picture Book"}), Map("Fountain World", {"Chainsaw"}, set(), True), Map("Snowy Pipe Organ", {"Chainsaw"}, set(), True), Map("Elvis Masada's Place", {"Chainsaw"}, set(), True), Map("The Slums", {"Chainsaw", "Spring", "Glasses"}, set(), True)],  
    "Marijuana Goddess World": Maps("The Nexus", "Color Cubes World", "Maiden Outlook", "Rainbow Hell") + [Map("Lotus Park", {"Twintails"}), Map("Dark Room", set(), {"Telephone"})], 
    "Dark Room": Maps("Marijuana Goddess World", "Snowy Pipe Organ", "Sewers", "Snowy Forest", "Art Gallery") + [Map("Tribe Settlement", {"Rainbow", "Teru Teru Bozu"}, {"Bat"}), Map("Tribe Settlement"), Map("Chocolate World", {"Cake"}, {"Chocolate World"}), Map("Chocolate World")], 
    "Color Cubes World": Maps("FC Caverns C"), 
    "Lotus Park": [Map("Marijuana Goddess World", {"Twintails"})], 
    "Rainbow Hell": Maps("Marijuana Goddess World"), 
    "Dressing Room": Maps("Fabric World") + [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})], 
    "Simple Street": [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})], 
    "Unending River": Maps("Amorphous Maroon Space") + [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})], 
    "Silent Sewers": Maps("Seaside Village", "Ruined Garden", "Dreary Drains"), 
    "Solstice Forest": Maps("Bright Forest", "Winter Valley", "Opal Ruins A"), 
    "Forest Pier": Maps("Abandoned Factory") + [Map("Hidden Shoal", {"Fairy", "Spacesuit", "Chainsaw"})], 
    "Portrait Collection": [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})], 
    "Stone Maze": [Map("Chocolate World", {"Cake"}, {"Chocolate World"}, {"From Dream Apartments"}), Map("Chocolate World", set(), set(), {"From Dream Apartments"}), Map("Blood World", set(), set(), {"From Dream Apartments"}), Map("Bowling Zone", set(), set(), {"From Dream Apartments"}), Map("Spelling Room", set(), set(), {"From Dream Apartments"}), Map("Magnet Room", {"From Dream Apartments"}), Map("Urotsuki's Dream Apartments", {"From Dream Apartments"}, {"Penguin"})],         
    "Forest World": Maps("The Nexus", "Underground TV Complex", "Astral World") + [Map("Chocolate World", {"Cake"}, {"Chocolate World"}), Map("Chocolate World")], 
    "Underground TV Complex": Maps("Mailbox", "TVLand") + [Map("Jigsaw Puzzle World", {"Bat", "Spring"}), Map("Forest World", set(), {"Lantern"})], 
    "Chocolate World": Maps("Stone Maze", "Green Tea Graveyard", "Violet Galaxy") + [Map("Highway", {"Bunny Ears"}), Map("Flying Fish World", {"Bunny Ears"}, {"Spacesuit"}), Map("Day and Night Towers", {"Bunny Ears"}), Map("Jigsaw Puzzle World", {"Bunny Ears"}), Map("Butter Rain World", {"Chocolate World", "Dream Park"}), Map("Forest World", set(), {"Lantern"}), Map("Dark Room", set(), {"Telephone"})], 
    "Mare Tranquillitatis": [Map("Forest World", {"Crossing"}, {"Lantern"})], 
    "Astral World": Maps("Obentou World", "Frozen Glade") + [Map("Forest World", set(), {"Lantern"})], 
    "Hospital": Maps("Intestines Maze") + [Map("Landolt Ring World", {"Glasses"}), Map("Graffiti Maze", set(), {"Stretch"}), Map("Graveyard World", set(), {"Gravestone"}), Map("Garden World", set(), {"Bike"})], 
    "Snowy Apartments": Maps("Underground Garage") + [Map("Garden World", set(), {"Bike"})], 
    "Blue Forest": Maps("Art Gallery", "Exhibition", "School") + [Map("Garden World", set(), {"Bike"})], 
    "Art Gallery": Maps("Blue Forest", "Visine World", "Sky Kingdom", "Toy World", "Flooded Baths") + [Map("Cloud Tops", set(), {"Day"}), Map("Dizzy Spirals World", set(), set(), True), Map("Garden World", set(), {"Bike"}, True), Map("The Baddies Bar", {"Chainsaw"}, {"Trombone"}, True), Map("The Baddies Bar", {"Lantern"}, {"Trombone"}, True), Map("The Baddies Bar", {"Rainbow"}, {"Trombone"}, True), Map("The Baddies Bar", set(), set(), True), Map("Forlorn Beach House", set(), set(), True), Map("Dream Park", {"Child"}, {"Dream Park"}), Map("Graffiti Maze", {"Glasses"}, {"Stretch"}), Map("Underwater Amusement Park", set(), {"!"}), Map("Monochrome Feudal Japan", set(), {"School Boy"})], 
    "Inu-san's Psyche": [Map("Garden World", set(), {"Bike"})], 
    "Blue Sanctuary": Maps("Candlelit Factory") + [Map("Garden World", set(), {"Bike"})], 
    "Board Game Islands": Maps("Domino Maze"),         
    "Elvis Masada's Place": Maps("Mushroom World", "Valentine Land", "Apartments", "Forlorn Beach House") + [Map("Power Plant", {"Fairy"})], 
    "Bug Maze": Maps("The Hand Hub", "Sign World", "Mushroom World") + [Map("Scenic Outlook", set(), {"Insect"})], 
    "White Fern World": Maps("Apartments", "Mushroom World"), 
    "Forlorn Beach House": Maps("Ecstasy World", "Realistic Beach", "Mushroom World") + [Map("Fairy Tale Woods", {"UFO"}, {"Red Riding Hood"}), Map("Fairy Tale Woods", set(), {"Red Riding Hood"}, True), Map("Apartments", set(), set(), True), Map("Art Gallery", set(), set(), True), Map("The Hand Hub", set(), set(), True)], 
    "Ice Cream Dream": Maps("Mushroom World"), 
    "Vibrant Mushroom World": Maps("Mushroom World") + [Map("Monochrome Ranch", {"Chainsaw"}), Map("Geometry World", set(), {"Boy"})], 
    "The Deciding Street": Maps("Dizzy Spirals World", "Netherworld") + [Map("Heart World", set(), {"Crossing"})], 
    "Valentine Land": Maps("Elvis Masada's Place", "Sign World", "Cyber Maze") + [Map("Heart World", set(), {"Crossing"})], 
    "Spherical Space Labyrinth": Maps("Miraculous Waters") + [Map("Heart World", set(), {"Crossing"})], 
    "Tricolor Passage": Maps("Mask Folks Hideout") + [Map("Cactus Desert", {"Yellow Path"}), Map("Pastel Sky Park", {"Wolf", "Blue Path"}), Map("Snowman World", {"Wolf", "Blue Path"}), Map("Heart World", set(), {"Crossing", "Red Path"})], 
    "Cipher Fog World": [Map("Heart World", set(), {"Crossing"})],         
    "Dark Museum": [Map("Japan Town", set(), {"Plaster Cast"}), Map("Urotsuki's Dream Apartments", set(), {"Penguin"}), Map("Geometry World", set(), {"Boy"}), Map("Flying Fish World", set(), {"Spacesuit"}), Map("Museum", {"Glasses"})], 
    "Saturated Eyeball Zone": Maps("Spelling Room", "Sky Kingdom", "Netherworld") + [Map("Geometry World", set(), {"Boy"})], 
    "Mossy Stone Area": Maps("Desolate Park") + [Map("Geometry World", set(), {"Boy"})], 
    "Vibrant Mushroom World": Maps("Mushroom World") + [Map("Monochrome Ranch", {"Chainsaw"}), Map("Geometry World", set(), {"Boy"})], 
    "Stone World": Maps("Monochrome GB World", "Digital Hand Hub"), 
    "Broken Faces Area": Maps("Floating Red Tiles World", "Laboratory", "Despair Road", "Vase World", "Apartments") + [Map("Forlorn Beach House", set(), {"UFO"}), Map("The Baddies Bar", {"Chainsaw"}, {"Trombone"}), Map("The Baddies Bar", {"Lantern"}, {"Trombone"}), Map("The Baddies Bar", {"Rainbow"}, {"Trombone"}), Map("The Baddies Bar", set(), set())], 
    "Intestines Maze": Maps("Guts World", "Red City", "Netherworld", "Ecstasy World", "Soldier Row", "Flesh Paths World", "Hand Fields", "DNA Room", "Blood World", "Dessert Fields", "Valentine Mail", "The Pansy Path") + [Map("Hospital", set(), {"Chainsaw"})], 
    "Sound Saws World": [Map("Geometry World", set(), {"Boy"})], 
    "Red Lily Lake": [Map("Graveyard World", set(), {"Gravestone"}), Map("Red Sky Cliff", {"Yellow Note"}, {"White Note"}), Map("Candy World", {"Child"}), Map("Red Sky Cliff", {"Chainsaw"}), Map("Butterfly Forest", {"??"})], 
    "Dream Park": Maps("Art Gallery", "Shadowy Caves") + [Map("Sixth Terminal", {"Spacesuit"}), Map("Theatre World", {"Bat"}), Map("Guts World", {"Marginal"}), Map("Dizzy Spirals World", set(), set(), True), Map("Guardians' Temple", {"Child", "Guardian's Realm"}, {"Guardian's Temple"}), Map("Scrambled Egg Zone", {"Child", "Guardian's Temple"}), Map("Birthday Tower", {"Cake"}), Map("Dice World", {"Tissue"}), Map("Guardians' Realm", set(), {"Guardian's Realm"}), Map("Underground Passage", {"Stone Towers"})], 
    "Red Sky Cliff": [Map("Red Lily Lake", set(), set(), False, {"White Note"}), Map("Constellation World", {"White Note"}, {"Blue Note"})],         
    "Day and Night Towers": Maps("Toy World", "Red Brick Maze", "Othello Board") + [Map("Mini-Maze", set(), {"Eyeball Bomb"})], 
    "Red Brick Maze": Maps("Toy World", "French Street"), 
    "Wooden Block World": Maps("Toy World", "Pancake World", "Chicken World"), 
    "Zodiac Fortress": Maps("Toy World", "Symbolon", "FC Caverns B"), 
    "Mini-Town": Maps("Gray Road"),         
    "Flooded Baths": Maps("Shield Owl World", "Art Gallery") + [Map("Atlantis", {"Fairy"}), Map("Atlantis", {"Spacesuit"}), Map("Atlantis", {"Penguin"})], 
    "Clawtree Forest": Maps("Shield Owl World", "Downfall Garden A", "River Road"), 
    "Water Lantern World": Maps("Shield Owl World"), 
    "Acerola World": Maps("Shield Owl World"), 
    "The Pansy Path": Maps("Shield Owl World", "Intestines Maze"), 
    "Bodacious Rotation Station": Maps("Shield Owl World", "Floating Stones World", "French Street"), 
    "NES Glitch Tunnel": Maps("Shield Owl World"),         
    "Orange Badlands": Maps("Pudding World", "Donut Hole World"), 
    "Pillar Ark": Maps("Pudding World", "Nefarious Chessboard", "Blood Red Beach"), 
    "Pop Revoir": Maps("Pin Cushion Vineyard") + [Map("Rotten Sea", {"Ending #1"}), Map("Portrait Purgatory", set(), {"Bike"})], 
    "Poseidon Plaza": [Map("Portrait Purgatory", set(), {"Bike"})], 
    "Sakura Forest": Maps("Butterfly Garden") + [Map("Portrait Purgatory", set(), {"Bike"}), Map("Shinto Shrine", set(), {"Maiko"})], 
    "Reverie Book Piles": Maps("Illusive Forest") + [Map("Portrait Purgatory", set(), {"Bike"})], 
    "Basement of Oddities": [Map("Portrait Purgatory", set(), {"Bike"})], 
    "Despair Road": Maps("Cipher Keyboard") + [Map("Broken Faces Area", set(), {"Marginal"})], 
    "Dream Bank": Maps("Cipher Keyboard"), 
    "Spaceship": Maps("Cipher Keyboard", "Pastel Pools"), 
    "Void": Maps("Cipher Keyboard", "Black Ink World", "Cosmic Cube World"), 
    "Amoeba Woods": Maps("Cipher Keyboard", "Sandy Cavern", "Magenta Village"),         
    "Rainbow Tiles Maze": Maps("Rock World", "Tangerine Prairie", "Golden Pyramid Path", "Jumbotron Hub", "Clover Ponds", "Visine Velvet Corridors", "Silver Mansion", "Blood Chamber"), 
    "Entomophobia Realm": Maps("Rock World", "Hollows", "Spore Forest", "Spiders' Nest"), 
    "Sanctuary": Maps("Rock World", "Gentle Sea") + [Map("Silver Mansion", {"Penguin"}, set(), True)], 
    "Visine Spacecraft": Maps("Golden Pyramid Path", "Rock World"), 
    "Theatre World": Maps("Nail World", "Galactic Park", "Dojo", "Cyan Relic World", "Neon Candle World", "Donut Hole World", "Rock World", "Hat World") + [Map("Cutlery World", set(), {"Cake"})], 
    "Vermilion Bamboo Forest": Maps("Rock World") + [Map("White Scarlet Exhibition", {"Grave"})], 
    "Starfield Garden": Maps("Forgotten Town"), 
    "Microbiome World": Maps("Bacteria World", "Blood Red House", "Hat World"), 
    "Color Capital": Maps("Bacteria World", "Haunted Head World", "Dark Forest"), 
    "Under-Around": Maps("Lamp Puddle World"), 
    "Digital Forest": Maps("Oil Puddle World") + [Map("Finger Candle World", {"Lantern"}), Map("Fluorescent Halls", {"Fluorescent Halls"})], 
    "Drains Theater": Maps("Ornamental Plains", "Negative Space", "Serene Docks", "Underwater Forest"), 
    "Birch Forest": Maps("Ornamental Plains", "Sign World", "Oriental Lake", "Magnet Room"), 
    "Flowerpot Outlands": Maps("Blue Eyes World", "Gray Memory", "Planter Passage"), 
    "Restored Character World": Maps("Blue Eyes World"), 
    "Mask Folks Hideout": Maps("Deep Red Wilds") + [Map("Tricolor Passage", set(), {"Red Path", "Blue Path", "Yellow Path"})], 
    "Bleeding Mushroom Garden": Maps("Deep Red Wilds", "Rapeseed Fields", "Primary Estate"), 
    "Downfall Garden A": Maps("Clawtree Forest", "Highway", "RGB Passage"), 
    "Clawtree Forest": Maps("Shield Owl World", "Downfall Garden A") + [Map("River Road", set(), {"!"})], 
    "RGB Passage": Maps("Downfall Garden A") + [Map("Highway", set(), set(), True)],         
    "Neon Highway": [Map("Downfall Garden B", {"Rainbow", "Polygon"})], 
    "Downfall Garden B": [], 
    "River Complex": Maps("River Road", "Christmas World", "Highway", "Smiling Trees World") + [Map("Virtual City", {"Telephone"})], 
    "River Road": Maps("Square-Square World", "The Docks", "River Complex"), 
    "Christmas World": Maps("The Hand Hub", "Exhibition", "River Complex") + [Map("Sherbet Snowfield", {"Dream Park"})], 
    "Smiling Trees World": Maps("River Complex"), 
    "Exhibition": Maps("Christmas World", "Farm World", "Netherworld", "Blue Forest", "Sandy Plains", "Cyber Maze", "Astronomical Gallery"), 
    "Square-Square World": Maps("River Road", "Neon City") + [Map("Theatre World", set(), {"Rainbow"}), Map("Flying Fish World", set(), {"Spacesuit"})], 
    "The Docks": Maps("Apartments", "Ocean Floor", "Realistic Beach", "Teddy Bear Land", "River Road"),         
    "Teddy Bear Land": Maps("Floating Red Tiles World", "The Docks", "School", "Chimney Pillars"), 
    "Realistic Beach": Maps("Forlorn Beach House", "The Docks") + [Map("Atlantis", {"Penguin"}), Map("Teleport Maze", set(), {"Wolf"})], 
    "Ocean Floor": Maps("The Docks") + [Map("Hourglass Desert", set(), {"Child"})], 
    "Floating Red Tiles World": Maps("Teddy Bear Land") + [Map("Broken Faces Area", set(), {"Marginal"}), Map("Farm World", set(), {"!"})], 
    "School": Maps("Urotsuki's Dream Apartments", "Dream Beach", "Blue Forest", "Teddy Bear Land", "Hat World"), 
    "Chimney Pillars": Maps("Valentine Mail", "Teddy Bear Land"), 
    "Valentine Mail": Maps("Intestines Maze", "Chimney Pillars"), 
    "Intestines Maze": Maps("Guts World", "Red City", "Hospital", "Netherworld", "Ecstasy World", "Soldier Row", "Flesh Paths World", "Hand Fields", "DNA Room", "Blood World", "Dessert Fields", "Valentine Mail", "The Pansy Path") + [Map("Floating Tiled Islands", {"Visit Floating Tiled Islands"})], 
    "Dream Beach": Maps("School", "Highway"), 
    "Farm World": Maps("Rough Ash World", "Floating Red Tiles World", "Exhibition"), 
    "Rough Ash World": Maps("Sewers", "Farm World", "Broken City", "Glacier Maze"), 
    "Sewers": Maps("Rough Ash World") + [Map("Japan Town", set(), {"Plaster Cast"}), Map("Dark Room", set(), {"Telephone"}), Map("Monochrome Feudal Japan", set(), {"School Boy"})], 
    "Broken City": Maps("Rough Ash World") + [Map("Cloudy World", {"Grave"})], 
    "Glacier Maze": Maps("Rough Ash World", "Frigid Meadow"), 
    "Cloudy World": [], 
    "Frigid Meadow": Maps("Concrete World", "Psychedelic Stone Path", "Cliffside Woods", "Glacier Maze"), 
    "Cliffside Woods": Maps("Frigid Meadow", "Spiked Fence Garden"), 
    "Spiked Fence Garden": Maps("Spore Forest", "Cliffside Woods", "Haniwa Ruins"), 
    "Spore Forest": Maps("Entomophobia Realm", "Spiked Fence Garden"), 
    "Entomophobia Realm": Maps("Rock World", "Hollows", "Spore Forest", "Spiders' Nest"), 
    "Haniwa Ruins": Maps("Spiked Fence Garden") + [Map("Labyrinth of Dread", {"Haniwa"})], 
    "Labyrinth of Dread": [], 
    "Psychedelic Stone Path": Maps("Frigid Meadow", "Aquamarine Cave") + [Map("Warehouse", set(), {"Polygon"})], 
    "Aquamarine Cave": Maps("Sandy Plains", "Psychedelic Stone Path", "Underground Lake"), 
    "Sandy Plains": Maps("Aquamarine Cave", "Exhibition"), 
    "Underground Lake": Maps("Aquamarine Cave", "Blue Restaurant"), 
    "Blue Restaurant": Maps("Blue House Road", "Underground Lake", "Experimentation Building"), 
    "Warehouse": Maps("Grass World", "Nail World", "Binary World", "Psychedelic Stone Path"), 
    "Grass World": Maps("Gray Road", "Green Neon World", "Floating Stones World", "Dream Venus") + [Map("Warehouse", set(), {"Polygon"})], 
    "Nail World": Maps("Window Room", "Pencil World") + [Map("Theatre World", set(), {"Rainbow"}), Map("Warehouse", set(), {"Polygon"})], 
    "Pencil World": Maps("Nail World"), 
    "Window Room": Maps("Nail World", "Teddy Bear Land", "Hourglass Desert"), 
    "Binary World": [Map("Circuit Board", {"Child", "Polygon"}), Map("Cyber Bar", {"Polygon", "Rainbow"})], 
    "Circuit Board": Maps("Shogi Board"), 
    "Shogi Board": Maps("Othello Board"), 
    "Othello Board": Maps("Day and Night Towers"), 
    "Cyber Bar": Maps("Binary World"), 
    "Concrete World": Maps("Museum", "Frigid Meadow"), 
    "Animated Hub": Maps("Concrete World", "Stony Buildings") + [Map("Flying Fish World", set(), {"Spacesuit"})], 
    "Museum": Maps("Concrete World"), 
    "Hollows": Maps("Entomophobia Realm") + [Map("Subterranean Research Center", {"Fairy"}), Map("Subterranean Research Center", {"Child"}), Map("Subterranean Research Center", {"Dice"})], 
    "Subterranean Research Center": Maps("Hollows", "Spear Tribe World") + [Map("Rainbow Towers", {"Spring"})], 
    "Spear Tribe World": Maps("Subterranean Research Center", "Dark Bunker"), 
    "Dark Bunker": Maps("Red Streetlight World", "The Hand Hub", "Spear Tribe World", "Blue Palm Road"), 
    "Blue Palm Road": Maps("Dark Bunker"), 
    "Restored Vantablack World": Maps("Monochrome School"), 
    "Rainbow Towers": Maps("Subterranean Research Center", "Chaos Exhibition"), 
    "Chaos Exhibition": Maps("Burial Desert", "Buried City", "Dark Warehouse", "Industrial Towers", "Mare Tranquillitatis"), 
    "Industrial Towers": [], 
    "Dark Warehouse": Maps("Seaside Village", "Chaos Exhibition", "Container Forest") + [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})], 
    "Buried City": Maps("Sunken City", "Chaos Exhibition"), 
    "Sunken City": Maps("Monochrome GB World", "Atlantis", "Buried City"), 
    "Monochrome GB World": Maps("Apartments", "Sunken City", "Nail World", "Handheld Game Pond", "Topdown Dungeon"), 
    "Atlantis": Maps("Snowy Pipe Organ", "Realistic Beach", "Botanical Garden") + [Map("Tapir-San's Place", {"City"}), Map("Underwater Amusement Park", {"City"}), Map("Tapir-San's Place", {"Fairy"}), Map("Underwater Amusement Park", {"Fairy"}), Map("Tapir-San's Place", {"Child"}), Map("Underwater Amusement Park", {"Child"}), Map("Flooded Baths", {"Spacesuit"}), Map("Flooded Baths", {"Fairy"}), Map("Flooded Baths", {"Penguin"}), Map("Star Ocean", {"Penguin"}), Map("Scorched Wasteland", {"Spacesuit"}), Map("Scorched Wasteland", {"Fairy"}), Map("Scorched Wasteland", {"Penguin"})], 
    "Burial Desert": Maps("Vase World", "Chaos Exhibition", "Industrial Towers"), 
    "Vase World": [Map("Hand Fields", {"Bat", "Chainsaw"}), Map("Burial Desert", {"Eyeball Bomb", "Chainsaw"}), Map("Broken Faces Area", set(), {"Marginal"})], 
    "Hand Fields": Maps("Intestines Maze", "Fountain World") + [Map("Vase World", {"Bat"})], 
    "Entomophobia Realm": Maps("Rock World", "Hollows", "Spore Forest", "Spiders' Nest"), 
    "Spiders' Nest": Maps("Entomophobia Realm"),         
    "Monochrome School": Maps("Monochrome Mansion", "Restored Vantablack World", "Neon Suburbs"), 
    "Neon Suburbs": Maps("Monochrome School"), 
    "Monochrome Mansion": Maps("Ghost Town", "Monochrome Wastelands", "Monochrome School"), 
    "Monochrome Wastelands": Maps("Monochrome Mansion", "Rough Ash World"), 
    "Ghost Town": Maps("Chalkboard Playground", "Monochrome Mansion", "Misty Bridges"), 
    "Misty Bridges": Maps("Ghost Town", "Parasite Laboratory", "Grand Scientific Museum", "Snowy Village"), 
    "Chalkboard Playground": Maps("Ghost Town") + [Map("Graffiti City", {"Fairy"}), Map("Graffiti City", {"Child"})], 
    "Parasite Laboratory": Maps("Misty Bridges"), 
    "Grand Scientific Museum": Maps("Misty Bridges"), 
    "Maiden Outlook": [], 
    "Character Plains": Maps("Library"), 
    "City Limits": Maps("Escalator", "Ocean Storehouse", "Highway") + [Map("Cloud Tops", {"Bat"}, {"Dusk"}), Map("Cloud Tops", {"Fairy"}, {"Dusk"}), Map("Cloud Tops", {"Spacesuit"}, {"Dusk"}), Map("Cloud Tops", set(), {"Dusk", "!"})], 
    "Escalator": Maps("Cyan Relic World", "City Limits"), 
    "Cyan Relic World": Maps("Escalator") + [Map("Theatre World", set(), {"Rainbow"})], 
    "Ocean Storehouse": Maps("City Limits", "Water Reclamation Facility"), 
    "Water Reclamation Facility": Maps("Ocean Storehouse") + [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})],     
    "TV Room": Maps("Highway"), 
    "Shinto Shrine": Maps("Monochrome Street", "The Circus", "The Hand Hub", "Netherworld", "Sakura Forest") + [Map("Maple Shrine", set(), set(), True)],         
    "Netherworld": Maps("The Deciding Street", "Exhibition", "Shinto Shrine", "Intestines Maze") + [Map("Tatami Room", {"Child"}), Map("Tatami Room", {"Fairy"})], 
    "Tatami Room": Maps("Netherworld"), 
    "The Circus": Maps("Shinto Shrine"), 
    "Maple Shrine": Maps("The Hand Hub"),         
    "Shape World": Maps("The Hand Hub") + [Map("Obstacle Course", {"Bike"})], 
    "Obstacle Course": Maps("Shape World", "Snow White Field"), 
    "Snow White Field": Maps("Obstacle Course", "Shape World", "Cherryblossom Fields"), 
    "Cherryblossom Fields": Maps("Snow White Field", "Private Rooms") + [Map("Chaotic Scribble World", {"Chainsaw"})], 
    "Private Rooms": Maps("Lit Tile Path"), 
    "Lit Tile Path": [Map("Obstacle Course 2", {"Bike"})], 
    "Obstacle Course 2": Maps("Lit Tile Path"), 
    "Chaotic Scribble World": Maps("Shunned Street"), 
    "Shunned Street": Maps("Chaotic Scribble World"),          
    "Dizzy Spirals World": Maps("Robotic Slaves Tunnel") + [Map("The Deciding Street", set(), {"Twintails"}), Map("Art Gallery", set(), set(), True), Map("The Hand Hub", set(), set(), True)], 
    "Robotic Slaves Tunnel": Maps("Dizzy Spirals World", "Handheld Game Pond"), 
    "Handheld Game Pond": Maps("Robotic Slaves Tunnel", "Monochrome GB World") + [Map("Crystal Star Tower", {"Drum"})], 
    "Crystal Star Tower": [],     
    "Apartments": Maps("The Docks", "Forlorn Beach House", "Underground Garage", "School") + [Map("Urotsuki's Dream Apartments", set(), {"Spring", "Penguin"}), Map("White Fern World", {"Chainsaw"}, {"Tissue"}), Map("Sky Kingdom", {"Chainsaw"}), Map("Sky Kingdom", set(), {"!"}), Map("Monochrome GB World", {"Child"}), Map("Monochrome GB World", {"Fairy"}), Map("Dream Park", {"Chainsaw", "Child", "Penguin"}, {"Dream Park"})], 
    "Topdown Dungeon": Maps("Realm of Dice", "Nefarious Chessboard", "Monochrome GB World", "FC Basement"), 
    "Realm of Dice": Maps("Topdown Dungeon"), 
    "Nefarious Chessboard": Maps("Pillar Ark", "Apple Prison", "Topdown Dungeon", "Checkered Towers"), 
    "Apple Prison": Maps("Nefarious Chessboard"), 
    "Checkered Towers": Maps("Nefarious Chessboard", "TVLand", "Retro Cartridge Game"), 
    "TVLand": Maps("Underground TV Complex", "Checkered Towers"), 
    "Retro Cartridge Game": Maps("Blue Streetlight World", "Thrift Shop"), 
    "Thrift Shop": Maps("Retro Cartridge Game", "Foggy Remnants") + [Map("Omurice Labyrinth", {"Twintails"})], 
    "Foggy Remnants": Maps("Thrift Shop", "Blue Streetlight World"), 
    "Blue Streetlight World": Maps("Retro Cartridge Game", "Foggy Remnants", "Worksite") + [Map("Red Streetlight World", set(), set(), True)], 
    "Worksite": Maps("Blue Streetlight World"), 
    "FC Basement": Maps("Topdown Dungeon") + [Map("Tribe Settlement", {"Rainbow", "Teru Teru Bozu"}, {"Bat"}), Map("Tribe Settlement", {"Invisible"}, {"Bat"}), Map("Tribe Settlement"), Map("Monochrome Feudal Japan", set(), {"School Boy"}), Map("Mini-Maze", set(), {"Eyeball Bomb"})], 
    "Tribe Settlement": Maps("FC Basement") + [Map("Dream Park", {"Twintails"}, {"Dream Park"}), Map("Dark Room", set(), {"Telephone"})], 
    "Azure Depths": Maps("Laundromat", "Maple Forest", "Nazca Valley"), 
    "Blackjack Manor": Maps("French Street", "Scrapyard"), 
    "Bread World": Maps("Omurice Labyrinth"), 
    "Checkered Postal Path": Maps("Everblue City", "Windswept Fields"), 
    "Cherry Blossom Park": Maps("Golden Mechanical Tower", "Four Seasons Forest"), 
    "Chicken World": Maps("Wooden Block World", "Lemon World", "Nazca Valley"), 
    "Cigarette World": Maps("Playing Card Dungeon", "Scrapyard"), 
    "Cinder Statue Heaven": Maps("Graffiti Sector") + [Map("Stalker Alley", {"Penguin"})], 
    "Corridor of Eyes": Maps("Rice Dumpling Plateau", "Scrapyard"), 
    "Crystal Lake": Maps("Egyptian Rave Dungeon", "Restored Sky Kingdom"), 
    "Cyber Prison": [], 
    "Dark Cheese Hell": Maps("Mole Mine", "Floating Beer Isle", "Refrigerator Tower", "Serum Laboratory", "Industrial Hotel"), 
    "Deep Blue Graveyard": Maps("Funeral Prison", "Sunset Sky Slums"), 
    "Deserted Center": Maps("Maple Forest"), 
    "Digital Alley": Maps("Nazca Valley"), 
    "Digital Heart Space": [], 
    "Dream Easter Island": Maps("Egyptian Rave Dungeon", "Funeral Prison"), 
    "Egyptian Rave Dungeon": Maps("Mackerel Desert", "Dream Easter Island", "Crystal Lake"), 
    "Elemental Caves": Maps("Nazca Valley"), 
    "Energy Complex": Maps("Honeybee Laboratory", "Serum Laboratory"), 
    "Everblue City": Maps("Totem Hotel", "Checkered Postal Path"), 
    "Evil Cube Zone": Maps("Tomato World"), 
    "Faces Zone": Maps("Nazca Valley"), 
    "Floating Beer Isle": Maps("Wine Cellar", "Sushi World", "Dark Cheese Hell"), 
    "Floating Brain World": [], 
    "Forest Cavern": Maps("Nazca Valley"), 
    "Forest of Reflections": Maps("Nazca Valley", "Sky Cactus Zone", "Junk From Anywhere"), 
    "Fossil Mines": Maps("Rainbow Pottery Zone", "Serpentine Pyramid"), 
    "Four Seasons Forest": Maps("Oriental Dojo", "Restored Sky Kingdom", "Sushi World", "Cherry Blossom Park") + [Map("Maple Forest", set(), {"From Four Seasons"})], 
    "Funeral Prison": Maps("Dream Easter Island", "Deep Blue Graveyard"), 
    "Golden Mechanical Tower": Maps("Windswept Fields", "Tomato World", "Cherry Blossom Park"), 
    "Graffiti Sector": Maps("Tarnished Ship", "Cinder Statue Heaven"), 
    "Grand Beach": Maps("Silhouette Complex", "Wounded Turtle World"), 
    "Greenhouse": Maps("Florist", "Toxic Chemical World"), 
    "Hatred Palace": Maps("Scrapyard") + [Map("Digital Heart Space", {"Penguin", "Teru Teru Bōzu", "Winter"})], 
    "Honeybee Laboratory": Maps("Nazca Valley", "Lingering Sewers", "Toxic Chemical World", "Honeycomb World", "Pink Honeycomb", "Honeybee Residence") + [Map("Energy Complex", {"Summer"})], 
    "Honeybee Residence": Maps("Honeybee Laboratory"), 
    "Industrial Hotel": Maps("Dark Cheese Hell"), 
    "Junk From Anywhere": Maps("Forest of Reflections"), 
    "Laundromat": Maps("Wine Cellar", "Azure Depths") + [Map("Oil Drum World", {"Drum"})], 
    "Lemon World": Maps("Chicken World", "Totem Hotel"), 
    "Libra Palace": Maps("Maroon Gravehouse", "Moonview Lane") + [Map("Constellation World", {"Autumn"})], 
    "Lingering Sewers": Maps("Stalker Alley", "Totem Hotel", "Honeybee Laboratory"), 
    "Litter Heaven": Maps("Love Lodge"), 
    "Love Lodge": Maps("Nazca Valley", "Litter Heaven", "Refrigerator Tower") + [Map("Cyber Prison", {"Fairy"}), Map("Cyber Prison", {"Child"})], 
    "Mackerel Desert": Maps("Pancake World", "Egyptian Rave Dungeon", "Nazca Valley"), 
    "Maple Forest": [Map("Stalker Alley", set(), set(), False, {"From Four Seasons"}), Map("Azure Depths", set(), set(), False, {"From Four Seasons"}), Map("Star Hub", set(), set(), False, {"From Four Seasons"}), Map("Playing Card Dungeon", set(), set(), False, {"From Four Seasons"}), Map("Four Seasons Forest", {"From Four Seasons"}), Map("Deserted Center", {"From Four Seasons"})], 
    "Maroon Gravehouse": Maps("Trophy Animal Land", "Libra Palace"), 
    "Mole Mine": Maps("Stained Glass Cosmo", "Dark Cheese Hell"), 
    "Moonview Lane": Maps("Libra Palace"), 
    "Mystery Library": Maps("Oil Drum World"), 
    "Nazca Valley": Maps("Mackerel Desert", "Azure Depths", "Forest Cavern", "Elemental Caves", "Love Lodge", "Honeybee Laboratory", "Digital Alley", "Rainbow Pottery Zone", "Forest of Reflections", "Chicken World", "Pumpkin City", "Oriental Dojo", "Wooden Cubes Playground", "Faces Zone", "Soy Sauce World") + [Map("Sky Cactus Zone", {"Haniwa", "Cake"}), Map("Snowy Suburbs", {"Lantern"})], 
    "Nightmare Inn": [], 
    "Oil Drum World": Maps("Mystery Library"), 
    "Omurice Labyrinth": Maps("Totem Hotel", "Rotten Fish Lake", "Tomato World", "Bread World"), 
    "Oriental Dojo": Maps("Nazca Valley", "Four Seasons Forest"), 
    "Pancake World": Maps("Wooden Block World", "Mackerel Desert"), 
    "Playing Card Dungeon": Maps("Maple Forest", "Cigarette World", "Realm of Dice"), 
    "Pufferfish Extraction Funland": Maps("Toxic Chemical World"), 
    "Pumpkin City": Maps("Nazca Valley"), 
    "Rainbow Pottery Zone": Maps("Nazca Valley", "Fossil Mines") + [Map("Constellation World", {"Summer"})], 
    "Refrigerator Tower": Maps("Love Lodge", "Dark Cheese Hell"), 
    "Restored Sky Kingdom": Maps("Crystal Lake", "Four Seasons Forest"), 
    "Rice Dumpling Plateau": Maps("Wooden Cubes Playground", "Corridor of Eyes"), 
    "Rotten Fish Lake": Maps("Omurice Labyrinth", "Trophy Animal Land"), 
    "Scrapyard": Maps("Blackjack Manor", "Cigarette World", "Hatred Palace", "Corridor of Eyes"), 
    "Serpentine Pyramid": Maps("Fossil Mines"), 
    "Serum Laboratory": Maps("Dark Cheese Hell", "Energy Complex"), 
    "Silhouette Complex": Maps("Trophy Animal Land"), 
    "Sky Cactus Zone": Maps("Forest of Reflections") + [Map("Nazca Valley", {"Haniwa", "Cake"})], 
    "Snowy Suburbs": Maps("Nazca Valley"), 
    "Soy Sauce World": Maps("Tomato World", "Nazca Valley"), 
    "Spike Alley": Maps("Voxel Island"), 
    "Stained Glass Cosmo": Maps("Wine Cellar", "Tarnished Ship", "Mole Mine"), 
    "Stalker Alley": Maps("Cinder Statue Heaven", "Maple Forest", "Lingering Sewers"), 
    "Star Hub": Maps("Maple Forest"), 
    "Sunken Treehouse": [], 
    "Sunset School": [], 
    "Sunset Sky Slums": Maps("Deep Blue Graveyard"), 
    "Sushi World": Maps("Floating Beer Isle", "Four Seasons Forest"), 
    "Tarnished Ship": Maps("Stained Glass Cosmo", "Graffiti Sector", "Toxic Chemical World"), 
    "Tomato World": Maps("Omurice Labyrinth", "Golden Mechanical Tower", "Evil Cube Zone", "Soy Sauce World"), 
    "Totem Hotel": Maps("Lingering Sewers", "Omurice Labyrinth", "Everblue City", "Lemon World", "Coffee Cup World"), 
    "Toxic Chemical World": Maps("Tarnished Ship", "Honeybee Laboratory", "Greenhouse", "Pufferfish Extraction Funland"), 
    "Trophy Animal Land": Maps("Rotten Fish Lake", "Maroon Gravehouse") + [Map("Silhouette Complex", {"Drum"})], 
    "Voxel Island": [], 
    "Windswept Fields": Maps("Checkered Postal Path", "Golden Mechanical Tower"), 
    "Wine Cellar": Maps("Laundromat", "Stained Glass Cosmo", "Floating Beer Isle"), 
    "Wooden Cubes Playground": Maps("Nazca Valley", "Rice Dumpling Plateau"), 
    "Wounded Turtle World": Maps("Floating Brain World"), 
    "The Baddies Bar": Maps("Bowling Zone", "The Hand Hub", "Art Gallery", "French Street") + [Map("The Slums", {"Stretch", "Spring", "Glasses"}), Map("Broken Faces Area", set(), {"Marginal"})], 
    "The Slums": [Map("The Baddies Bar", {"Chainsaw"}, {"Trombone"}), Map("The Baddies Bar", {"Lantern"}, {"Trombone"}), Map("The Baddies Bar", {"Rainbow"}, {"Trombone"}), Map("The Baddies Bar")], 
    "French Street": Maps("Gray Road", "Red Brick Maze", "Blackjack Manor") + [Map("Bodacious Rotation Station", set(), {"Stretch"}), Map("The Baddies Bar", {"Chainsaw"}, {"Trombone"}), Map("The Baddies Bar", {"Lantern"}, {"Trombone"}), Map("The Baddies Bar", {"Rainbow"}, {"Trombone"}), Map("The Baddies Bar")], 
    "Bodacious Rotation Station": Maps("Shield Owl World", "Floating Stones World", "French Street"), 
    "Floating Stones World": Maps("Grass World", "Scorched Wasteland") + [Map("Bodacious Rotation Station", set(), {"Stretch"}), Map("Dark Alleys", set(), {"Teru Teru Bozu"})], 
    "Dark Alleys": Maps("Floating Stones World"), 
    "Scorched Wasteland": Maps("Floating Stones World", "Paradise", "Salsa Desert") + [Map("Mangrove Forest", {"Teru Teru Bozu"})], 
    "Salsa Desert": Maps("Scorched Wasteland"), 
    "Paradise": Maps("Ice Floe World"), 
    "Ice Floe World": Maps("Paradise", "Mangrove Forest"), 
    "Mangrove Forest": Maps("Ice Floe World", "Scorched Wasteland"), 
    "Bowling Zone": Maps("Stone Maze", "Never-Ending Hallway") + [Map("The Invisible Maze", {"Chainsaw"}, {"Invisible"})], 
    "The Invisible Maze": Maps("Bowling Zone"), 
    "Never-Ending Hallway": Maps("Art Gallery"), 
    "Spelling Room": Maps("Stone Maze", "Sepia Clouds World", "Saturated Eyeball Zone", "Forlorn Beach House", "Nail World", "Visine World", "Octagonal Grid Hub") + [Map("Theatre World", set(), {"Rainbow"}), Map("Flying Fish World", set(), {"Spacesuit"}), Map("Japan Town", set(), {"Plaster Cast"})],         
    "T-Folk World": Maps("Red Monastery", "Giant Desktop") + [Map("Horror Maze", {"?"})], 
    "Giant Desktop": Maps("T-Folk World"), 
    "Horror Maze": Maps("T-Folk World"), 
    "Fused Faces World": Maps("Onyx Tile World", "Crazed Faces Maze"), 
    "Crazed Faces Maze": Maps("Fused Faces World", "Experimentation Building", "Blue House Road"), 
    "Experimentation Building": Maps("Crazed Faces Maze", "Blizzard Plains", "Blue Restaurant"), 
    "Blizzard Plains": [], 
    "Blue House Road": Maps("Blue Restaurant"), 
    "White Black World": Maps("Color Cubes World", "Cultivated Lands", "Onyx Tile World") + [Map("Visine World", {"Chainsaw"})], 
    "Visine World": Maps("Art Gallery", "Guts World"), 
    "Guts World": Maps("Intestines Maze", "Visine World"), 
    "Cultivated Lands": Maps("Bridged Swamp Islands", "The Ceiling", "White Black World"), 
    "The Ceiling": Maps("Heian Era Village", "Cultivated Lands", "Lotus Waters"), 
    "Lotus Waters": Maps("The Ceiling", "Seaside Village", "Dream Mars"), 
    "Dream Mars": Maps("Lotus Waters", "Dream Venus"), 
    "Dream Venus": Maps("Grass World", "Dream Mars", "Spaceship"), 
    "Seaside Village": Maps("Rapeseed Fields", "Heian Era Village", "Lotus Waters", "Dark Warehouse", "Silent Sewers"), 
    "Rapeseed Fields": Maps("Bridged Swamp Islands", "Seaside Village", "Bleeding Mushroom Garden"), 
    "Heian Era Village": [Map("Bridged Swamp Islands", {"Chainsaw"}), Map("Seaside Village", {"Lantern"}), Map("The Ceiling", {"Glasses"})], 
    "Dark Forest": Maps("Gray Road", "Forest Carnival", "Color Capital"), 
    "Haunted Head World": Maps("Color Capital"), 
    "Forest Carnival": Maps("Laboratory") + [Map("Abandoned Chinatown", {"Chainsaw"})], 
    "Abandoned Chinatown": Maps("Forest Carnival", "Laboratory"), 
    "Laboratory": Maps("Soldier Row", "Negative Space", "Mailbox", "Abandoned Chinatown") + [Map("Broken Faces Area", set(), {"Marginal"})], 
    "Soldier Row": Maps("Intestines Maze"), 
    "Mailbox": Maps("Underground TV Complex", "Laboratory"), 
    "Negative Space": Maps("Laboratory", "Drains Theater", "Rocky Cavern", "Crimson Labyrinth"), 
    "Crimson Labyrinth": Maps("Negative Space", "Ancient Crypt"), 
    "Ancient Crypt": Maps("Crimson Labyrinth", "Radiant Stones Pathway") + [Map("Entropy Dungeon", {"Glasses"})], 
    "Radiant Stones Pathway": Maps("Ancient Crypt", "Flooded Buildings"), 
    "Flooded Buildings": Maps("Radiant Stones Pathway"), 
    "Entropy Dungeon": Maps("Aureate Clockworks", "Ancient Crypt"), 
    "Aureate Clockworks": Maps("Monolith Jungle", "Entropy Dungeon"), 
    "Rocky Cavern": Maps("Negative Space", "Clay Statue World"), 
    "Clay Statue World": Maps("Rocky Cavern", "Oriental Lake"), 
    "Oriental Lake": Maps("Clay Statue World", "Emerald Cave") + [Map("Birch Forest", set(), {"Red Riding Hood"})], 
    "Emerald Cave": Maps("Oriental Lake", "Mountainous Badlands"), 
    "Mountainous Badlands": Maps("Emerald Cave", "Indigo Pathway"), 
    "Indigo Pathway": Maps("Mountainous Badlands", "Streetlight Garden"), 
    "Streetlight Garden": Maps("Indigo Pathway"), 
    "Drains Theater": Maps("Ornamental Plains", "Negative Space", "Serene Docks", "Underwater Forest"), 
    "Serene Docks": Maps("Drains Theater", "Gray Road", "Underwater Forest"), 
    "Underwater Forest": Maps("Drains Theater", "Serene Docks", "Stony Buildings"), 
    "Stony Buildings": Maps("Underwater Forest", "Animated Hub", "Sugar Road"),         
    "Boogie Street": Maps("Gray Road", "Fountain World") + [Map("House Over the Rainbow", {"Rainbow"})], 
    "House Over the Rainbow": Maps("Boogie Street", "High-rise Building"), 
    "High-rise Building": Maps("House Over the Rainbow", "Head World", "Chocolate World"), 
    "Head World": Maps("High-rise Building"), 
    "Fountain World": Maps("Boogie Street", "Hand Fields"), 
    "Hand Fields": Maps("Intestines Maze", "Fountain World") + [Map("Vase World", {"Bat"})],     
    "Train Tracks": Maps("Gray Road", "Closet Pinwheel Path", "Underwater Amusement Park"), 
    "Closet Pinwheel Path": Maps("Train Tracks", "Netherworld") + [Map("Japan Town", set(), {"Plaster Cast"})], 
    "Underwater Amusement Park": Maps("Train Tracks", "Art Gallery") + [Map("Atlantis", set(), {"City"})], 
    "Florist": Maps("Gray Road", "Shop Ruins", "Greenhouse"), 
    "Shop Ruins": Maps("Cocktail Lounge", "Halloween Zone", "Florist", "Realm of Gluttony"), 
    "Realm of Gluttony": Maps("Shop Ruins", "Pink Honeycomb"), 
    "Pink Honeycomb": Maps("Honeybee Laboratory", "Realm of Gluttony", "Strawberry Milk Sea"), 
    "Strawberry Milk Sea": Maps("Pink Honeycomb", "Celestial Night"), 
    "Celestial Night": Maps("Strawberry Milk Sea"), 
    "Frozen Disco": Maps("Celestial Night"), 
    "Rainy Town": Maps("Halloween Zone") + [Map("Frozen Disco", {"Chainsaw"})], 
    "Halloween Zone": Maps("Shop Ruins", "Rainy Town") + [Map("Cocktail Lounge", {"Glasses"})], 
    "Cocktail Lounge": Maps("Cyber Maze", "Shop Ruins", "Florist") + [Map("Halloween Zone", {"Glasses"})], 
    "Cyber Maze": Maps("Valentine Land", "Exhibition", "GALAXY Town", "Cocktail Lounge", "Dream Mexico", "Sea Lily World", "Oriental Pub", "Smiling Trees World"), 
    "Dream Mexico": Maps("Cyber Maze", "Ancient Hydrangea City"), 
    "Ancient Hydrangea City": Maps("Dream Mexico"), 
    "GALAXY Town": Maps("Gray Road", "Cyber Maze", "Sugar World"), 
    "Sugar World": Maps("GALAXY Town", "False Shoal", "Valentine Land"), 
    "False Shoal": Maps("Ahogeko's House"), 
    "Ahogeko's House": Maps("False Shoal", "3D Structures Path"), 
    "3D Structures Path": [],         
    "Snowy Forest": Maps("Techno Condominium", "Alien Cellar") + [Map("Dark Room", set(), {"Telephone"})], 
    "Techno Condominium": Maps("Snowy Forest", "FC Caverns A", "Gray Road", "Cotton Candy Haven") + [Map("Art Gallery", {"Rainbow"})], 
    "FC Caverns A": Maps("Techno Condominium") + [Map("Flooded Dungeon", {"Rainbow"}), Map("Flooded Dungeon", {"Stretch"}), Map("Flooded Dungeon", {"Fairy"})], 
    "Alien Cellar": Maps("Snowy Forest"), 
    "Static Noise Hell": Maps("Infinite Library", "Snowy Forest"), 
    "Infinite Library": Maps("Cotton Candy Haven", "Static Noise Hell", "Erratic Pillar Lands", "Library"), 
    "Erratic Pillar Lands": Maps("Ocean Subsurface"), 
    "Ocean Subsurface": Maps("Erratic Pillar Lands", "Aquatic Cube City"), 
    "Aquatic Cube City": Maps("Ocean Subsurface", "Surgical Scissors World") + [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})], 
    "Surgical Scissors World": Maps("Aquatic Cube City", "Neon Caves"), 
    "Neon Caves": Maps("Surgical Scissors World", "Static Labyrinth"), 
    "Static Labyrinth": Maps("Neon Caves", "Windswept Scarlet Sands"), 
    "Windswept Scarlet Sands": Maps("Static Labyrinth"), 
    "Cotton Candy Haven": [Map("Infinite Library", {"Boy", "Crossing", "Chainsaw"}), Map("Wooden Polycube Ruins", {"Teru Teru Bozu"})], 
    "Wooden Polycube Ruins": Maps("Cotton Candy Haven", "Nocturnal Grove"), 
    "Nocturnal Grove": Maps("Flooded Dungeon", "Lost Creek"), 
    "Lost Creek": Maps("Cloaked Pillar World"), 
    "Cloaked Pillar World": Maps("Viridescent Temple"), 
    "Viridescent Temple": Maps("Cloaked Pillar World", "Floating Catacombs"), 
    "Floating Catacombs": Maps("Viridescent Temple", "Fossil Lake"), 
    "Fossil Lake": Maps("Floating Catacombs", "Subterranean Plant") + [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})], 
    "Subterranean Plant": Maps("Fossil Lake", "Aurora Lake"), 
    "Aurora Lake": Maps("Subterranean Plant", "Rainfall Ruins"), 
    "Rainfall Ruins": Maps("Aurora Lake", "Lavender Waters"), 
    "Lavender Waters": [],         
    "Head Wasteland": Maps("Red City", "Wilderness"), 
    "Wilderness": Maps("Head Wasteland", "Hourglass Desert"), 
    "Hourglass Desert": Maps("Wilderness") + [Map("Dark Room", set(), {"Telephone"})], 
    "Mask Shop": Maps("Monochrome Street"),         
    "Alien Valley": Maps("Bleeding Heads Garden", "Butterfly Passage"), 
    "Butterfly Passage": Maps("Alien Valley", "Whipped Cream World"), 
    "Whipped Cream World": Maps("Butterfly Passage", "Monkey Mansion", "Overgrown Condominium"), 
    "Monkey Mansion": Maps("Whipped Cream World", "Chess World") + [Map("Aquatic Cafe", set(), {"!"})], 
    "Chess World": Maps("Monkey Mansion"), 
    "Overgrown Condominium": Maps("Whipped Cream World", "Sugar Road") + [Map("Container Forest", {"Twintails"})], 
    "Container Forest": Maps("Dark Warehouse", "Wastewater Treatment Plant", "Overgrown Condominium"), 
    "Dark Warehouse": Maps("Seaside Village", "Chaos Exhibition", "Container Forest") + [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})], 
    "Wastewater Treatment Plant": Maps("Container Forest", "Scarlet Corridors", "Isometry World"), 
    "Isometry World": Maps("Wastewater Treatment Plant"), 
    "Scarlet Corridors": Maps("Wastewater Treatment Plant"), 
    "Black Sphere World": [],         
    "Ninja Town": Maps("Hot Air Balloon World") + [Map("Green Pattern World", {"Penguin"})], 
    "Green Pattern World": Maps("Ninja Town", "Domino Constructions"), 
    "Domino Constructions": Maps("Green Pattern World", "Roadside Forest"), 
    "Roadside Forest": Maps("Domino Constructions", "Checkerboard Clubhouse"), 
    "Checkerboard Clubhouse": [],     
    "Server Hub": [], 
    "Lost Forest": [], 
    "Halls": [],         
    "FC Caverns C": Maps("Color Cubes World") + [Map("Home Within Nowhere", set(), {"Shimako"})], 
    "Home Within Nowhere": Maps("Pure White Lands"), 
    "Pure White Lands": Maps("Home Within Nowhere", "Lamplit Stones"), 
    "Lamplit Stones": Maps("Pure White Lands", "Field of Cosmos", "Adabana Gardens"), 
    "Field of Cosmos": Maps("Lamplit Stones", "Adabana Gardens", "Bubble World"), 
    "Adabana Gardens": Maps("Lamplit Stones", "Field of Cosmos", "Bubble World"), 
    "Bubble World": Maps("Adabana Gardens", "Field of Cosmos", "Red Sewers"), 
    "Red Sewers": Maps("Marshmallow Shallows", "Wooded Lakeside", "Bubble World"), 
    "Marshmallow Shallows": Maps("Red Sewers", "3D Underworld"), 
    "3D Underworld": Maps("Marshmallow Shallows", "Kaleidoscope World", "Streetlight Docks", "Oblique Hell"), 
    "Kaleidoscope World": Maps("3D Underworld", "Glowing Tree Path"), 
    "Glowing Tree Path": Maps("Kaleidoscope World", "Oblique Hell"), 
    "Oblique Hell": Maps("Wooded Lakeside", "Glitched Butterfly Sector", "3D Underworld", "Streetlight Docks", "Glowing Tree Path"), 
    "Streetlight Docks": Maps("3D Underworld", "Marshmallow Shallows", "Oblique Hell"), 
    "Wooded Lakeside": Maps("Red Sewers", "Oblique Hell", "Home Within Nowhere"), 
    "Glitched Butterfly Sector": Maps("Oblique Hell") + [Map("Sierpinski Maze", {"Shimako"})], 
    "Sierpinski Maze": Maps("Glitched Butterfly Sector", "Virtual City"), 
    "Virtual City": [Map("Rainy Apartments", {"Shimako"}), Map("River Complex", {"Telephone"})], 
    "Reflecting Electron Zone": Maps("Virtual City"), 
    "Rainy Apartments": Maps("Virtual City"), 
    "Snowy Pipe Organ": [Map("Dark Room", set(), {"Telephone"}), Map("Atlantis", {"Boy"}), Map("Atlantis", {"Wolf"}), Map("Atlantis", {"School Boy"}), Map("Atlantis", {"Bat"}), Map("Atlantis", {"Chainsaw"})], 
    "Scenic Outlook": Maps("Bug Maze", "Fairy Tale Woods"), 
    "Fairy Tale Woods": [Map("Scenic Outlook", set(), {"Insect"}), Map("Jigsaw Puzzle World", {"Red Riding Hood", "Bat"}), Map("Broken Faces Area", {"Red Riding Hood"}, {"Marginal"})],         
    "Jigsaw Puzzle World": Maps("Fairy Tale Woods", "Underground TV Complex", "Daily Toy Box", "Lorn Tower", "Dream Beach"), 
    "Daily Toy Box": Maps("Jigsaw Puzzle World"), 
    "Lorn Tower": Maps("Dream Beach"),         
    "Sign World": Maps("Bug Maze", "Power Plant", "Valentine Land") + [Map("Birch Forest", set(), {"Red Riding Hood"}), Map("Teleport Maze", set(), {"Wolf"}), Map("Haniwa Temple", set(), {"Haniwa"})], 
    "Haniwa Temple": Maps("Sign World") + [Map("Dream Park", {"Haniwa"}, {"Dream Park"})], 
    "Power Plant": Maps("Sign World") + [Map("White Fern World", set(), {"Tissue"}), Map("Elvis Masada's Place", {"Fairy"}), Map("Elvis Masada's Place", {"Spacesuit"})], 
    "Teleport Maze": Maps("Sign World", "Realistic Beach"), 
    "Ecstasy World": Maps("Sky Kingdom", "Forlorn Beach House", "Intestines Maze"),     
    "Mini-Maze": Maps("Day and Night Towers", "FC Basement", "Bathhouse"), 
    "Bathhouse": [Map("Mini-Maze", set(), {"Eyeball Bomb"})], 
    "Sky Kingdom": Maps("Art Gallery", "Ecstasy World"), 
    "Cloud Tops": Maps("Art Gallery") + [Map("Constellation World", {"Night"}), Map("Tricolor Room", {"Crepuscule"}), Map("Neon Candle World", {"Dusk"}), Map("City Limits", {"Dusk", "Bat"}), Map("City Limits", {"Dusk", "Fairy"}), Map("City Limits", {"Dusk", "Spacesuit"}), Map("School", {"Day"}, set(), True), Map("Geometry World", {"Night"}, {"Boy"}, True), Map("Restored Sky Kingdom", {"Day"}, set(), True)], 
    "Neon Candle World": Maps("Theatre World") + [Map("Cloud Tops", set(), {"Dusk"})], 
    "Constellation World": Maps("Candy World") + [Map("Rainbow Pottery Zone", {"Summer"}), Map("Cloud Tops", set(), {"Night"}), Map("Innocent Dream", {"Blue Note"}), Map("Lapine Forest", {"Bunny Ears"}), Map("Spacey Retreat", {"Bunny Ears"}), Map("Spacey Retreat", {"Spring"})], 
    "Candy World": Maps("Red Lily Lake", "Constellation World", "Coffee Cup World"), 
    "Coffee Cup World": Maps("Candy World") + [Map("Honeycomb World", {"Insect"})], 
    "Innocent Dream": Maps("Tricolor Room"), 
    "Lapine Forest": [Map("Constellation World", {"Bunny Ears"})], 
    "Butterfly Forest": Maps("Tricolor Room", "Red Lily Lake", "Constellation World", "Blue Orb World"), 
    "Blue Orb World": Maps("Butterfly Forest") + [Map("Fruit Cake World", {"??"})], 
    "Fruit Cake World": Maps("Blue Orb World", "Chaos World", "Tricolor Room"), 
    "Chaos World": Maps("Fruit Cake World", "Butterfly Forest"), 
    "Red Lily Lake": Maps("Graveyard World") + [Map("Candy World", {"Child"}), Map("Red Sky Cliff", {"Chainsaw"}), Map("Butterfly Forest", {"??"})], 
    "Spacey Retreat": Maps("Astronomical Gallery", "Coral Shoal") + [Map("Constellation World", {"Bunny Ears"}), Map("Constellation World", {"Spring"})], 
    "Coral Shoal": Maps("Gemstone Cave"), 
    "Gemstone Cave": Maps("Coral Shoal"), 
    "Astronomical Gallery": Maps("Butterfly Garden", "Exhibition", "Blooming Blue Lagoon", "Spacey Retreat"), 
    "Blooming Blue Lagoon": Maps("Lamp Passage", "Decrepit Village", "Astronomical Gallery"), 
    "Decrepit Village": Maps("Twisted Thickets", "Shadow Lady Estate") + [Map("Carnivorous Pit", {"Chainsaw"})], 
    "Shadow Lady Estate": Maps("Decrepit Village"), 
    "Carnivorous Pit": Maps("Decrepit Village", "Guts World"), 
    "Twisted Thickets": Maps("Decrepit Village") + [Map("Opal Archives", {"Fairy"})], 
    "Opal Archives": Maps("Cocktail Lounge"), 
    "Lamp Passage": Maps("Sea of Clouds", "Tan Desert", "Fantasy Isle", "Blooming Blue Lagoon"), 
    "Sea of Clouds": Maps("Lamp Passage") + [Map("Sepia Clouds World", {"Child"}), Map("Sepia Clouds World", {"Fairy"}), Map("Sepia Clouds World", {"Dice"}), Map("Sepia Clouds World", {"Grave"})], 
    "Sepia Clouds World": Maps("Spelling Room") + [Map("Sea of Clouds", {"Child"}), Map("Sea of Clouds", {"Fairy"}), Map("Sea of Clouds", {"Dice"}), Map("Sea of Clouds", {"Grave"})], 
    "Flesh Paths World": Maps("Intestines Maze", "Sea of Clouds", "Downfall Garden A", "Nostalgic House") + [Map("Broken Faces Area", {"Chainsaw"}, {"Marginal"})], 
    "Nostalgic House": [], 
    "Tan Desert": Maps("Lamp Passage", "Evergreen Woods"), 
    "Evergreen Woods": Maps("Spirit Capital"), 
    "Spirit Capital": Maps("Evergreen Woods"), 
    "Fantasy Isle": Maps("Lamp Passage", "Graffiti City", "Animal Heaven"), 
    "Animal Heaven": Maps("Pastel Pools"), 
    "Pastel Pools": Maps("Animal Heaven", "Spaceship"),         
    "Monochrome Feudal Japan": Maps("Art Gallery", "Sewers", "FC Basement", "FC Caverns B", "Duality Wilds", "Bishop Cathedral"), 
    "FC Caverns B": Maps("Zodiac Fortress") + [Map("Hidden Garage", {"Grave"}), Map("Monochrome Feudal Japan", set(), {"School Boy"})], 
    "Hidden Garage": Maps("FC Caverns B", "Travel Hotel"), 
    "Travel Hotel": [], 
    "Duality Wilds": [Map("Monochrome Feudal Japan", {"Child"}, {"School Boy"}), Map("Monochrome Feudal Japan", {"Fairy"}, {"School Boy"})], 
    "Bishop Cathedral": Maps("Monochrome Feudal Japan") + [Map("Board Game Islands", {"Child"}, set(), True)], 
    "Donut Hole World": Maps("Orange Badlands") + [Map("Theatre World", set(), {"Rainbow"})], 
    "Blood Red Beach": Maps("Pillar Ark"),     
    "Black Ink World": Maps("Void"), 
    "Cosmic Cube World": Maps("Void"), 
    "Sandy Cavern": Maps("Amoeba Woods"), 
    "Magenta Village": Maps("Amoeba Woods"),         
    "Tangerine Prairie": Maps("Rainbow Tiles Maze", "Flower Scent World"), 
    "Flower Scent World": Maps("Tangerine Prairie", "Petal Hotel"), 
    "Petal Hotel": Maps("Flower Scent World"), 
    "Golden Pyramid Path": Maps("Rainbow Tiles Maze") + [Map("Visine Spacecraft", set(), set(), True)], 
    "Jumbotron Hub": Maps("Rainbow Tiles Maze", "Forgotten Town", "Floral Crossroads", "Ghostly Inn", "Dreamscape Villa"), 
    "Forgotten Town": Maps("Jumbotron Hub", "Starfield Garden", "Enigmatic World"), 
    "Enigmatic World": Maps("Forgotten Town"), 
    "Starfield Garden": Maps("Forgotten Town"), 
    "Floral Crossroads": Maps("Jumbotron Hub", "Metallic Plate World", "Strawberry Fields"), 
    "Strawberry Fields": Maps("Floral Crossroads"), 
    "Metallic Plate World": Maps("Floral Crossroads", "Avian Statue World"), 
    "Avian Statue World": Maps("Metallic Plate World"), 
    "Ghostly Inn": Maps("Jumbotron Hub", "White Scarlet Exhibition"), 
    "White Scarlet Exhibition": [], 
    "Dreamscape Villa": Maps("Jumbotron Hub"), 
    "Clover Ponds": Maps("Rainbow Tiles Maze", "Shell Lake"), 
    "Shell Lake": Maps("Clover Ponds"), 
    "Visine Velvet Corridors": Maps("Rainbow Tiles Maze"), 
    "Silver Mansion": Maps("Rainbow Tiles Maze", "Electromagnetic Terminal"), 
    "Electromagnetic Terminal": Maps("Silver Mansion", "Ghastly Dumpsite", "Haunted Village"), 
    "Haunted Village": Maps("Electromagnetic Terminal"), 
    "Ghastly Dumpsite": Maps("Electromagnetic Terminal"), 
    "Blood Chamber": Maps("Rainbow Tiles Maze"), 
    "Gentle Sea": Maps("Sanctuary"),        
    "Galactic Park": Maps("Jade Sky Hamlet") + [Map("Theatre World", set(), {"Rainbow"})], 
    "Jade Sky Hamlet": Maps("Galactic Park"),         
    "Dojo": Maps("Beetle Forest") + [Map("Theatre World", set(), {"Rainbow"})], 
    "Beetle Forest": Maps("Dojo"),         
    "Hat World": Maps("Theatre World", "Alazan Domain", "School", "Microbiome World") + [Map("Rainbow Road", {"Rainbow"})], 
    "Alazan Domain": Maps("Hat World", "Parking Zone", "Forest of Strange Faces"), 
    "Forest of Strange Faces": Maps("Alazan Domain", "Blood Red House"), 
    "Blood Red House": Maps("Forest of Strange Faces", "Microbiome World"), 
    "Parking Zone": Maps("Alazan Domain", "Glitched Purgatory") + [Map("Urotsuki's Dream Apartments", set(), {"Penguin"}), Map("Deep Cold Path", {"Winter"})], 
    "Deep Cold Path": Maps("Christmas World"),
    "Glitched Purgatory": [], 
    "Glitch Hell": Maps("Underground Burial Site"), 
    "Ice Block World": [Map("Glitch Hell", set(), {"Glitch Hell"})], 
    "Witch Heaven": Maps("Ice Block World"), 
    "Pink Life World": Maps("Warzone", "Witch Heaven"), 
    "Warzone": Maps("Video Game Graveyard", "Pink Life World"), 
    "Video Game Graveyard": [Map("Warzone", {"Polygon"}), Map("Underground Burial Site", {"Glitch Hell"})], 
    "Underground Burial Site": [Map("Sushi Belt World", {"Haniwa"})], 
    "Sushi Belt World": [], 
    "Rainbow Road": Maps("Hat World") + [Map("Video Game Graveyard", {"Spring", "Grave"})], 
    "Cutlery World": [Map("Theatre World", set(), {"Rainbow"})], 
    "Primary Estate": Maps("Bleeding Mushroom Garden"), 
    "Obentou World": Maps("Astral World", "Crystal Star Tower", "Fish World"), 
    "Fish World": Maps("Dessert Fields", "Obentou World"), 
    "Dessert Fields": Maps("Intestines Maze", "Fish World"), 
    "Frozen Glade": Maps("Astral World", "Glowing Stars World"), 
    "Glowing Stars World": Maps("Frozen Glade", "Sandstone Brick Maze"), 
    "Sandstone Brick Maze": Maps("Glowing Stars World", "Pin Cushion Vineyard"), 
    "Pin Cushion Vineyard": Maps("Pop Revoir", "Sandstone Brick Maze"), 
    "Green Tea Graveyard": Maps("Chocolate World"), 
    "Violet Galaxy": [],
    "Butter Rain World": Maps("Chocolate World", "Sixth Terminal"), 
    "Sixth Terminal": Maps("Sacred Crypt") + [Map("Dream Park", {"Spacesuit"})], 
    "Sacred Crypt": [], 
    "Underground Garage": Maps("Apartments", "Snowy Apartments", "Vending Machine Factory") + [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})], 
    "Vending Machine Factory": Maps("Underground Garage", "Snack Gallery"), 
    "Snack Gallery": Maps("Vending Machine Factory"), 
    "Candlelit Factory": Maps("Wooden Block World") + [Map("Cloud Tops", set(), {"Night"}), Map("Flamelit Wasteland", {"Chainsaw"}), Map("Fish Person Shoal", {"Spacesuit"}), Map("Fish Person Shoal", {"Fairy"})], 
    "Fish Person Shoal": Maps("Expanded Corridors"), 
    "Expanded Corridors": Maps("Fish Person Shoal", "Chaos Exhibition"), 
    "Flamelit Wasteland": Maps("Fish Person Shoal"), 
    "Graffiti Maze": Maps("Hospital", "Art Gallery"),
    "Miraculous Waters": Maps("Robotic Institution", "Erythrocyte Maze") + [Map("Herbarium", {"Glasses"}), Map("Cube of Sweets", {"Cake"}), Map("Broken Faces Area", set(), {"Marginal"})], 
    "Cube of Sweets": Maps("Miraculous Waters", "Chocolate Tower"), 
    "Chocolate Tower": Maps("Cube of Sweets"), 
    "Herbarium": Maps("Miraculous Waters"), 
    "Erythrocyte Maze": Maps("Miraculous Waters", "Intestines Maze", "Visceral Cavern") + [Map("Blood Cell Sea", {"Crossing"})], 
    "Visceral Cavern": Maps("Erythrocyte Maze", "Tartaric Abyss"), 
    "Tartaric Abyss": Maps("Visceral Cavern"), 
    "Blood Cell Sea": Maps("Stuffed Dullahan World") + [Map("Erythrocyte Maze", {"Crossing"})], 
    "Stuffed Dullahan World": Maps("Blood Cell Sea"), 
    "Robotic Institution": Maps("Miraculous Waters", "Calcarina Sea"), 
    "Clandestine Research Laboratory": Maps("Robotic Institution", "Phosphorus World"), 
    "Phosphorus World": Maps("Clandestine Research Laboratory") + [Map("Forest Interlude", {"Fairy"}), Map("Forest Interlude", {"Spacesuit"})], 
    "Forest Interlude": Maps("Miraculous Waters"), 
    "Calcarina Sea": Maps("Robotic Institution"),  
    "Desolate Park": Maps("Mossy Stone Area", "Red Strings Maze"), 
    "Red Strings Maze": Maps("Desolate Park", "Budding Life World"), 
    "Budding Life World": Maps("Funky Dusky Hall"), 
    "Funky Dusky Hall": Maps("Budding Life World", "Dusty Pinwheel Path"), 
    "Dusty Pinwheel Path": Maps("Funky Dusky Hall", "Drenched Passageways"), 
    "Drenched Passageways": Maps("Dusty Pinwheel Path", "Table Scrap Expanse"), 
    "Table Scrap Expanse": Maps("Pop Tiles Maze"), 
    "Pop Tiles Maze": Maps("Table Scrap Expanse"), 
    "Digital Hand Hub": Maps("The Hand Hub", "Holographic Chamber"), 
    "Holographic Chamber": Maps("Ether Caverns"), 
    "Ether Caverns": Maps("Chaos Exhibition", "Holographic Chamber", "Fluorescent City"), 
    "Fluorescent City": Maps("Ether Caverns"), 
    "DNA Room": Maps("Intestines Maze"), 
    "Blood World": Maps("Stone Maze") + [Map("Intestines Maze", set(), set(), True)], 
    "Japan Town": Maps("Sewers", "Maiden Outlook", "Closet Pinwheel Path") + [Map("Dark Museum", set(), {"Glasses"})], 
    "Flying Fish World": Maps("Animated Hub", "Urban Street Area", "Square-Square World") + [Map("Dark Museum", set(), {"Glasses"})], 
    "Urban Street Area": [Map("Flying Fish World", set(), {"Spacesuit"})], 
    "Space": [Map("Urban Street Area", {"Fairy"})], 
    "Tapir-San's Place": [Map("Space", {"Chainsaw", "Spacesuit"}), Map("Atlantis", set(), {"City"})], 
    "Butterfly Garden": Maps("Sakura Forest", "Astronomical Gallery"), 
    "Illusive Forest": Maps("Torii Trail") + [Map("Sea of Trees", {"Glasses"})], 
    "Torii Trail": Maps("Illusive Forest", "Blue Screen Void"), 
    "Blue Screen Void": Maps("Torii Trail", "Sunset Hill"), 
    "Rice Field": Maps("Illusive Forest", "Secret Society"), 
    "Secret Society": Maps("Rice Field", "Sunset Hill"), 
    "Sea of Trees": Maps("Lonely Home", "Sugar Road"), 
    "Lonely Home": Maps("Gray Memory", "Sea of Trees", "Server Hub", "Party Playground"), 
    "Gray Memory": Maps("Planter Passage", "Flowerpot Outlands", "Lonely Home"), 
    "Planter Passage": Maps("Flowerpot Outlands", "Gray Memory", "Somber Establishment", "Server Hub"), 
    "Somber Establishment": Maps("Planter Passage", "Submerged Signs World", "Sepia Clouds World"), 
    "Submerged Signs World": Maps("Somber Establishment", "Server Hub"), 
    "Party Playground": Maps("Lonely Home", "Floating Tiled Islands"), 
    "Floating Tiled Islands": Maps("Party Playground", "Blue Sanctuary", "Flesh Paths World"), 
    "Sunset Hill": Maps("Blue Screen Void", "Sunflower Fields", "Secret Society"), 
    "Sunflower Fields": Maps("Sunset Hill", "Mini-Nexus"), 
    "Mini-Nexus": Maps("Blueberry Farm"), 
    "Crying Mural World": Maps("Mini-Nexus", "Frozen Smile World"), 
    "Frozen Smile World": Maps("Crying Mural World", "Cherry Willow Path"), 
    "Cherry Willow Path": Maps("Frozen Smile World", "Moonlit Street"), 
    "Moonlit Street": Maps("Autumn Sky"), 
    "Autumn Sky": Maps("Moonlit Street", "Eyeberry Orchard"), 
    "Eyeberry Orchard": Maps("Autumn Sky"), 
    "Pale Corridors": Maps("Mini-Nexus"), 
    "Potato Starch World": Maps("Mini-Nexus"), 
    "Vomiting Mouths World": Maps("Mini-Nexus"), 
    "Teru Teru Bozu Pond": Maps("Mini-Nexus", "Somber Establishment"), 
    "Blueberry Farm": Maps("Mini-Nexus", "Restored Character World"), 
    "Fabric World": Maps("Dressing Room", "Guts World"), 
    "Silkworm Forest": Maps("Tricolor Room"), 
    "Cloud Floor": Maps("Candy World"), 
    "Green Neon World": Maps("Grass World", "Construction Frame Building"), 
    "Construction Frame Building": Maps("Green Neon World", "Cog Maze"), 
    "Cog Maze": Maps("Construction Frame Building", "Nail World") + [Map("Forest Pier", set(), {"Forest Pier"})], 
    "Forest Pier": Maps("Abandoned Factory") + [Map("Hidden Shoal", {"Fairy"}), Map("Hidden Shoal", {"Spacesuit"})], 
    "Hidden Shoal": Maps("Forest Pier"), 
    "Abandoned Factory": Maps("Wind Tunnel", "Arc de Pillar World"), 
    "Wind Tunnel": Maps("Deserted Pier"), 
    "Arc de Pillar World": Maps("Abandoned Factory", "Mansion"), 
    "Mansion": Maps("Arc de Pillar World", "Deserted Pier", "Industrial Maze"), 
    "Industrial Maze": Maps("Mansion", "Overgrown City"), 
    "Overgrown City": Maps("Industrial Maze", "Chaotic Buildings"), 
    "Deserted Pier": Maps("Mansion", "Wind Tunnel", "Deserted Town"), 
    "Deserted Town": Maps("Deserted Pier", "Chaotic Buildings", "Abandoned Apartments"), 
    "Abandoned Apartments": Maps("Planetarium", "Deserted Town"), 
    "Planetarium": Maps("Abandoned Apartments", "Deserted Town"), 
    "Chaotic Buildings": Maps("Deserted Town", "Pillars World", "Transmission Tower World", "Overgrown City"), 
    "Pillars World": Maps("Chaotic Buildings"), 
    "Transmission Tower World": Maps("Chaotic Buildings", "Complex"), 
    "Complex": Maps("Transmission Tower World", "Old Train Station"), 
    "Old Train Station": Maps("Complex", "Cosmic World"), 
    "Old Train Station B": Maps("Rainbow Silhouette World"), 
    "Rainbow Silhouette World": Maps("Old Train Station B"), 
    "Cosmic World": Maps("Old Train Station", "Square Ruins"), 
    "Square Ruins": Maps("Cosmic World", "Depths"), 
    "Depths": Maps("Square Ruins"), 
    "Town Maze": Maps("Black Building", "Deserted Town", "Bottom Garden"), 
    "Cactus Desert": Maps("Execution Ground") + [Map("Tricolor Passage", set(), {"Yellow Path"})], 
    "Execution Ground": Maps("Cactus Desert", "Atelier"), 
    "Atelier": Maps("Execution Ground", "Portrait Purgatory", "Duality Wilds"), 
    "Sea Lily World": Maps("Mutant Pig Farm", "Cyber Maze"), 
    "Mutant Pig Farm": Maps("Aquatic Cafe", "Sea Lily World", "Stomach Maze") + [Map("The Hand Hub", {"Polygon"})], 
    "Aquatic Cafe": Maps("Mutant Pig Farm", "Monkey Mansion"), 
    "Stomach Maze": Maps("Mutant Pig Farm", "Sculpture Park"), 
    "Sculpture Park": Maps("Parking Garage", "Stomach Maze", "Sugar Road"), 
    "Parking Garage": Maps("Sculpture Park", "Crimson Labyrinth", "Heart World", "Red Streetlight World"), 
    "Oriental Pub": Maps("Cyber Maze", "Sparkling Dimension A", "Sparkling Dimension B", "Test Facility", "Tribulation Complex", "Holiday Hell", "Ice Cream Islands", "Abandoned Grounds", "Platformer World"), 
    "Sparkling Dimension A": Maps("Oriental Pub"), 
    "Sparkling Dimension B": Maps("Oriental Pub"), 
    "Test Facility": Maps("Abandoned Grounds"), 
    "Abandoned Grounds": Maps("Platformer World"), 
    "Platformer World": Maps("Tribulation Complex"), 
    "Tribulation Complex": Maps("Ice Cream Islands"), 
    "Ice Cream Islands": Maps("Holiday Hell"), 
    "Holiday Hell": Maps("Test Facility"), 
    "Octagonal Grid Hub": Maps("Colorless Valley") + [Map("Broken Faces Area", set(), {"Marginal"})], 
    "Colorless Valley": Maps("Octagonal Grid Hub", "Colorless Roads"), 
    "Colorless Roads": Maps("Colorless Valley"), 
    "Sugar Road": Maps("Overgrown Condominium", "Blob Desert", "Sculpture Park", "Graffiti City", "Mountaintop Ruins", "Chaos Exhibition", "Statue Forest", "Deluxe Mask Shop", "Stony Buildings", "Sea of Trees", "Chromatic Limbo") + [Map("Urotsuki's Dream Apartments", set(), {"Penguin"})], 
    "Blob Desert": Maps("Sugar Road", "Stellar Mausoleum"), 
    "Stellar Mausoleum": Maps("Blob Desert", "Mottled Desert"), 
    "Mottled Desert": Maps("Stellar Mausoleum"), 
    "Mountaintop Ruins": Maps("Sugar Road", "Eyeball Cherry Fields"), 
    "Eyeball Cherry Fields": Maps("Mountaintop Ruins", "Rusty Urban Complex") + [Map("Whispery Sewers", {"Child"}), Map("Whispery Sewers", {"Fairy"}), Map("Whispery Sewers", {"Dice"})], 
    "Whispery Sewers": Maps("Dream Pool") + [Map("Eyeball Cherry Fields", {"Child"}), Map("Eyeball Cherry Fields", {"Fairy"})], 
    "Dream Pool": Maps("Whispery Sewers", "Rusty Urban Complex") + [Map("Dark Nexus", {"Chainsaw", "Invisible"}), Map("Azure Garden", {"Chainsaw", "Fairy"})], 
    "Dark Nexus": Maps("Dream Pool", "Garden of Treachery"), 
    "Garden of Treachery": Maps("Dark Nexus", "Visine World"), 
    "Rusty Urban Complex": Maps("Eyeball Cherry Fields", "Foliage Estate", "Wind Turbine Plateau", "Dream Pool"), 
    "Wind Turbine Plateau": Maps("Rusty Urban Complex"), 
    "Foliage Estate": Maps("Rusty Urban Complex", "Azure Garden"), 
    "Azure Garden": Maps("Foliage Estate", "Magical Passage"), 
    "Magical Passage": Maps("Azure Garden"), 
    "Statue Forest": Maps("Sugar Road", "Dreadful Docks", "Submerged Communications Area"), 
    "Submerged Communications Area": Maps("Statue Forest", "Bleeding Heads Garden"), 
    "Bleeding Heads Garden": Maps("Red Streetlight World", "Alien Valley"), 
    "Dreadful Docks": Maps("Statue Forest", "Pastel Chalk World"), 
    "Pastel Chalk World": [], 
    "Deluxe Mask Shop": Maps("Sugar Road"), 
    "Chromatic Limbo": Maps("Sugar Road"),         
    "Star Ocean": Maps("Atlantis", "Rusted City"), 
    "Rusted City": Maps("Dark Warehouse", "Strange Plants World") + [Map("Star Ocean", {"Penguin"}), Map("Star Ocean", {"Spacesuit"}), Map("Ruined Garden", {"Silent Sewers"})], 
    "Strange Plants World": Maps("Rusted City", "Underground Laboratory") + [Map("Underground Passage", {"Spring"})], 
    "Underground Passage": Maps("Strange Plants World", "Icy Plateau", "Extraterrestrial Cliffside") + [Map("Stone Towers", set(), {"Stone Towers"})], 
    "Extraterrestrial Cliffside": [Map("Riverside Waste Facility", {"Fairy"}), Map("Riverside Waste Facility", {"Child"}), Map("Haunted Forest Town", {"Chainsaw"})], 
    "Haunted Forest Town": Maps("Candy Cane Fields", "Extraterrestrial Cliffside", "Celestial Garden"), 
    "Candy Cane Fields": Maps("Icy Plateau", "Haunted Forest Town"), 
    "Icy Plateau": Maps("Underground Passage", "Candy Cane Fields"), 
    "Stone Towers": Maps("Underground Passage"), 
    "Underground Laboratory": Maps("Strange Plants World", "Polluted Swamp") + [Map("Chaos Exhibition", {"Chainsaw"}), Map("Tesla Garden", set(), {"Tesla Garden"})], 
    "Polluted Swamp": Maps("Underground Laboratory", "The Rooftops", "Toxic Sea"), 
    "Toxic Sea": Maps("Polluted Swamp"), 
    "The Rooftops": Maps("Polluted Swamp", "Rainy Docks", "Monochromatic Abyss", "Symbolon"), 
    "Rainy Docks": Maps("The Rooftops"), 
    "Monochromatic Abyss": Maps("The Rooftops", "CMYK Tiles World"), 
    "CMYK Tiles World": Maps("Monochromatic Abyss", "Riverside Waste Facility"), 
    "Riverside Waste Facility": Maps("CMYK Tiles World", "Extraterrestrial Cliffside", "Undersea Temple"), 
    "Undersea Temple": Maps("Riverside Waste Facility"),         
    "Silent Sewers": Maps("Seaside Village", "Ruined Garden", "Dreary Drains"), 
    "Ruined Garden": Maps("Silent Sewers", "Vintage Town", "Monolith Jungle", "Rusted City"), 
    "Vintage Town": Maps("Ruined Garden", "Decrepit Dwellings"), 
    "Decrepit Dwellings": Maps("Vintage Town", "Abandoned Dreadnought"), 
    "Monolith Jungle": Maps("Ruined Garden", "Aureate Clockworks", "Twilight Park"), 
    "Dreary Drains": Maps("Silent Sewers", "Tesla Garden", "Ancient Aeropolis"), 
    "Ancient Aeropolis": Maps("Dreary Drains", "Desolate Hospital"), 
    "Desolate Hospital": Maps("Ancient Aeropolis", "Luminous Lake"), 
    "Luminous Lake": Maps("Memory Garden"), 
    "Memory Garden": Maps("Library"), 
    "Dragon Statue World": Maps("Memory Garden", "Rusted Factory"), 
    "Rusted Factory": Maps("Dragon Statue World"), 
    "Abandoned Dreadnought": Maps("Decrepit Dwellings", "Chainlink Lees"), 
    "Chainlink Lees": Maps("Abandoned Dreadnought", "Verdant Promenade"), 
    "Verdant Promenade": Maps("Dreary Drains"), 
    "Bismuth World": Maps("Verdant Promenade", "Forgotten Megalopolis"), 
    "Forgotten Megalopolis": Maps("Bismuth World", "Wintry Cliffs", "Sketch Plains"), 
    "Sketch Plains": Maps("Forgotten Megalopolis"), 
    "Wintry Cliffs": Maps("Forgotten Megalopolis", "Tomb of Velleities"), 
    "Tomb of Velleities": Maps("Wintry Cliffs"),         
    "Tesla Garden": Maps("Dreary Drains", "Underground Laboratory", "Graffiti City", "Doll House", "Neon Sea", "Pierside Residence"), 
    "Pierside Residence": Maps("Tesla Garden", "Tunnel Town"), 
    "Tunnel Town": Maps("Pierside Residence"), 
    "Doll House": Maps("Tesla Garden", "Cat Cemetery"), 
    "Cat Cemetery": Maps("Doll House", "Snowy Village"), 
    "Snowy Village": Maps("Cat Cemetery", "Misty Bridges", "Marble Ruins"), 
    "Marble Ruins": Maps("Snowy Village"), 
    "Graffiti City": Maps("Tesla Garden", "Blue Cactus Islands", "Sugar Road", "Vaporwave Mall") + [Map("Chalkboard Playground", {"Child"}), Map("Chalkboard Playground", {"Fairy"})], 
    "Neon Sea": Maps("Blue Cactus Islands", "Viridian Wetlands", "Lost Shoal"), 
    "Viridian Wetlands": Maps("Neon Sea"), 
    "Lost Shoal": Maps("Neon Sea", "Twilight Park"), 
    "Twilight Park": Maps("Lost Shoal", "Monolith Jungle"), 
    "Aureate Clockworks": Maps("Monolith Jungle", "Entropy Dungeon"), 
    "Entropy Dungeon": Maps("Aureate Clockworks", "Ancient Crypt"), 
    "Ancient Crypt": Maps("Crimson Labyrinth", "Radiant Stones Pathway") + [Map("Entropy Dungeon", {"Glasses"})], 
    "Radiant Stones Pathway": Maps("Ancient Crypt", "Flooded Buildings"), 
    "Flooded Buildings": Maps("Radiant Stones Pathway"),         
    "Vaporwave Mall": Maps("Graffiti City"), 
    "Blue Cactus Islands": Maps("Graffiti City", "Neon Sea"), 
    "Neon City": Maps("Square-Square World", "Abandoned Factory"), 
    "Botanical Garden": Maps("RGB Passage B", "Flooded Baths"), 
    "RGB Passage B": Maps("Botanical Garden", "Rainbow Hell"), 
    "Shadowy Caves": [Map("Dream Park", {"Bat"}), Map("Abyss of Farewells", {"Rainbow"}), Map("Guardians' Realm", {"Fairy", "Glasses"})], 
    "Abyss of Farewells": Maps("Dream Park"), 
    "Guardians' Realm": Maps("Dream Park") + [Map("Sacred Crypt", {"??"})], 
    "Guardians' Temple": [Map("Dream Park", {"Child"}), Map("Sacred Crypt", {"??"})], 
    "Scrambled Egg Zone": [], 
    "Dice World": Maps("Dream Park"), 
    "Birthday Tower": Maps("Dream Park"), 
    "Honeycomb World": Maps("Coffee Cup World") + [Map("Honeybee Laboratory", {"Insect"})],
    "Symbolon": Maps("Zodiac Fortress", "Data Stream") + [Map("Polluted Swamp", {"Symbolon"})], 
    "Data Stream": Maps("Symbolon", "Binary World"), 
    "Flooded Dungeon": Maps("FC Caverns A", "Nocturnal Grove", "Cotton Candy Haven"), 
    "Landolt Ring World": [Map("Hospital", {"Glasses"})], 
    "Monochrome Ranch": [], 
    "Sherbet Snowfield": Maps("Christmas World", "Sixth Terminal"), 
    "Domino Maze": Maps("Board Game Islands"), 
    "Integer World": Maps("Word World"), 
    "Snowman World": [Map("Tricolor Passage", set(), {"Blue Path"})], 
    "Celestial Garden": Maps("Haunted Forest Town"), 
    "Pastel Sky Park": [Map("Tricolor Passage", set(), {"Blue Path"})], 
}),
    "flow": Connections(".flow", "Sabitsuki", "", -1, {}, {}),
    "prayers": Connections("Answered Prayers", "Fluorette", "Tall Geta", -1, {}, {}),
    "someday": Connections("Someday", "Itsuki", "Scooter", -1, {}, {
    "Itsuki's Room": Maps("The Nexus") + [Map("Chaos", {"Give all your effects to the Teru Teru Bozu in the Lake."})], 
    "Chaos": Maps("Itsuki's Room", "Meta-Nexus"), 
    "Meta-Nexus": Maps("Chaos"), 
    "The Nexus": Maps("Itsuki's Room", "Lava World", "8-bit World", "Data World", "Purple Polka-Dot World", "Alphanumeric World", "Computer World", "Dark World", "Doodle World", "Mountain World", "Grassland World", "School World") + [Map("Space World", set(), {"Wrench"})], 
    "Lava World": Maps("The Nexus", "Rain World") + [Map("Corrupted School", set(), set(), True)], 
    "Rain World": Maps("Lava World", "Clock Tower"), 
    "Clock Tower": Maps("Rain World"), 
    "Corrupted School": Maps(), 
    "8-bit World": Maps("The Nexus", "LSD World") + [Map("Forest", set(), {"Fox"})], 
    "Forest": Maps("Data World"), 
    "Data World": Maps("The Nexus", "Desert") + [Map("Forest", set(), {"Fox"})], 
    "Desert": Maps("Data World", "Four Seasons Path", "Subway"), 
    "Four Seasons Path": Maps("Desert"), 
    "Subway": Maps("Streetlight World", "Nice Town", "Grassland World", "City", "Mall", "Ice World", "Desert"), 
    "Mall": Maps("Subway", "Edible World", "Empty Gallery"), 
    "Edible World": Maps("Mall"), 
    "Empty Gallery": Maps("Internet"), 
    "Internet": Maps("Computer World", "Art Gallery", "Wobbly World") + [Map("Tubes", set(), {"TV"})], 
    "Computer World": Maps("The Nexus", "Internet", "Glitch World"), 
    "Glitch World": Maps(), 
    "Tubes": Maps("Internet") + [Map("Hexagon Realm", {"Wrench"})], 
    "Hexagon Realm": Maps("Dark World"), 
    "Dark World": Maps("The Nexus", "Memory Graveyard", "LSD World"), 
    "Memory Graveyard": Maps("Dark World"), 
    "LSD World": Maps("8-bit World", "Alphanumeric World", "Dark World", "Pink Maze") + [Map("Hatsuyume", set(), set(), True)], 
    "Alphanumeric World": Maps("The Nexus", "Rainbow World", "LSD World"), 
    "Rainbow World": Maps("Alphanumeric World", "Tsukitsuki's Bedroom"), 
    "Tsukitsuki's Bedroom": Maps("Rainbow World"), 
    "Hatsuyume": Maps("Doodle World"), 
    "Doodle World": Maps("The Nexus", "Playground", "Art Gallery") + [Map("Lake", {"Healing Aura"})], 
    "Playground": Maps("Doodle World"), 
    "Lake": Maps("Doodle World"), 
    "Art Gallery": Maps("Doodle World", "Internet"), 
    "Pink Maze": Maps("Thread World", "LSD World"), 
    "Thread World": Maps("Pink Maze"), 
    "Question World": Maps("Pink Maze"), 
    "Decision Path": Maps("Question World"), 
    "School World": Maps("The Nexus", "Decision Path"), 
    "Space World": Maps("The Nexus", "Shooting Star Path", "Moon"), 
    "Shooting Star Path": Maps("Space Party") + [Map("Space World", set(), {"Wrench"})], 
    "Space Party": Maps("Shooting Star Path"), 
    "Moon": [Map("Space World", set(), {"Wrench"}), Map("Testing Area", {"TV", "Megaphone"}, {"Mercury"}), Map("Testing Area")], 
    "Testing Area": Maps("Moon") + [Map("Deep Internet", {"Wood", "TV", "Megaphone"}), Map("Moon 2", {"Lab Coat", "TV", "Megaphone"})], 
    "Deep Internet": Maps("Computer Maze"), 
    "Computer Maze": Maps(), 
    "Moon 2": Maps("Edible World") + [Map("Testing Area", {"TV", "Megaphone"}, {"Wood", "Mercury"}), Map("Testing Area")],         
    "Mountain World": Maps("The Nexus", "Data World 2", "Fog World"), 
    "Data World 2": Maps("Mountain World") + [Map("Ice World", {"Fox"})], 
    "Ice World": Maps("Data World 2", "Subway"), 
    "Subway": Maps("Streetlight World", "Nice Town", "Grassland World", "City", "Mall", "Ice World", "Desert"), 
    "Nice Town": Maps("Subway", "High School"), 
    "High School": Maps("Nice Town"), 
    "Grassland World": Maps("The Nexus", "Overgrown Caves", "Subway", "Caves"), 
    "Overgrown Caves": Maps("Grassland World"), 
    "Caves": Maps() + [Map("Grassland World", {"Fox"}), Map("Beach", {"Fox"})], 
    "Beach": Maps("Caves", "Seabed"), 
    "Seabed": Maps("Beach", "Sewers"), 
    "Sewers": Maps("Purple Polka-Dot World", "Seabed", "City") + [Map("Desert", {"Mercury"}), Map("Ice World", {"Mercury"})], 
    "City": Maps("Sewers", "Subway"),             
    "Purple Polka-Dot World": Maps("The Nexus", "Neon Path", "Sewers"), 
    "Neon Path": Maps("Purple Polka-Dot World") + [Map("Neon World", set(), {"Megaphone"})], 
    "Neon World": Maps("Neon Path", "Dance Flood"), 
    "Dance Flood": [Map("Neon World", set(), {"Megaphone"})],    
    "Fog World": Maps("Mountain World") + [Map("Hospital", set(), {"Healing Aura"})], 
    "Hospital": Maps("Fog World", "Streetlight World"), 
    "Streetlight World": Maps("Subway") + [Map("Hospital", set(), {"Healing Aura"})],      
    "Wobbly World": Maps("Internet") + [Map("Nice Bar", {"Wood"})], 
    "Nice Bar": Maps("Wobbly World"), 
}),
    "muma": Connections("Muma|Rope", "Muma", "", 0, {}, {})
}

PLAYERS = {
    "madotsuki": Player("Madotsuki's Room"),
    "urotsuki": Player("Urotsuki's Room"),
    "urotsuki_100%": Player("Urotsuki's Room", {"Bike", "Boy", "Chainsaw", "Lantern", "Fairy", "Spacesuit", "Glasses", "Rainbow", "Wolf", "Eyeball Bomb", "Telephone", "Maiko", "Penguin", "Insect", "Spring", "Invisible", "Plaster Cast", "Stretch", "Haniwa", "Cake", "Twintails", "Child", "School Boy", "Trombone", "Tissue", "Red Riding Hood", "Polygon", "Marginal", "Teru Teru Bozu", "Bat", "Drum", "Grave", "Crossing", "Bunny Ears", "Dice", "Ending #1", "Ending #2", "Ending #3", "Ending #4", "Forest Pier", "Blue Note", "Silent Sewers", "Tesla Garden", "Rainbow Ruins", "Symbolon", "Fluorescent Halls"}),
    "sabitsuki": Player("Sabitsuki's Room"),
    "fluorette": Player("Shrine"),
    "fluorette_100%": Player("Shrine"),
    "itsuki": Player("Itsuki's Room"),
    "itsuki_100%": Player("Itsuki's Room", {"TV", "Megaphone", "Mercury", "Wrench", "Lab Coat", "Wood", "Fox"}),
    "muma": Player("Memory Room"),
}

# CONFIG

# basic settings
### usage: --game [...], -g [...]
GAME = None
### usage: --player [...], -p [...]
### if None, uses default player for the game
PLAYER = None 
### usage: --shortest-mode, -s
### true: find a map with deepest path (i.e. Depths), false: find a longest path without backtracking
SHORTEST_MODE = False 
### usage: --deterministic, -d (***FALSE if SHORTEST_MODE is TRUE***)
### instead of the three-step nondeterministic method, find all possibility before moving to the next depth, DO NOT TURN ON FOR 2KKI (your pc will die)
DETERMINISTIC = False 
### usage: --luck-penalty [...], -l [...]
### point penalty for luck-based travel, do not count luck based paths by default
LUCK_PENALTY = -99999 
### usage: --verbose, -v
### prints progress messages. if false, only prints new findings/results
PRINT_LOG = False
### usage: --print-all-threshold [...], -P [...]
### print all paths over this many worlds deep. used to find tied paths. set to -1 to disable
PRINT_ALL_THRESHOLD = -1
### usage: --wiki, -w
### print result in wiki form (for use in yume.wiki/User:prodzpod and whatnot)
WIKI_FORM = False

# advanced settings: ***ONLY WORKS on SHORTEST_MODE = FALSE and DETERMINISTIC = FALSE***
### usage: --transition-threshold [...], -t [...]
### minimum path length needed to "stick" to that path
TRANSITION_THRESHOLD = 0 
### usage: --short-search [...], -S [...]
### number of iteration to check before moving onto next
SHORT_SEARCH = 5000
### usage: --heat [...], -H [...]
### chance per connection to "shuffle" each short search failure
HEAT = 0.05
### usage: --reset-threshold [...], -R [...]
### number of short search failure to completely reset the set, set to -1 to disable
RESET_THRESHOLD = 1000
### usage: --long-search [...], -L [...]
### number of iteration to check before progress update
LONG_SEARCH = 10000000
### usage: --fast-in [...], -F [...]
### maximum number of worlds to obtain the "go fast" effect. paths that does not get it before then are discarded early. set to -1 to disable
FAST_IN = -1

# help (usage: --help, -h)
_HELP = False

# utils
def log(*values):
    if PRINT_LOG:
        print(*values)

# INIT: handle argvs and set up variables

_ARGS = {"--game": "GAME", "-g": "GAME", "--player": "PLAYER", "-p": "PLAYER", "--shortest-mode": "SHORTEST_MODE", "-s": "SHORTEST_MODE", "--deterministic": "DETERMINISTIC", "-d": "DETERMINISTIC", "--luck-penalty": "LUCK_PENALTY", "-l": "LUCK_PENALTY", "--verbose": "PRINT_LOG", "-v": "PRINT_LOG", "--print-all-threshold": "PRINT_ALL_THRESHOLD", "-P": "PRINT_ALL_THRESHOLD", "--wiki": "WIKI_FORM", "-w": "WIKI_FORM", "--transition-threshold": "TRANSITION_THRESHOLD", "-t": "TRANSITION_THRESHOLD", "--short-search": "SHORT_SEARCH", "-S": "SHORT_SEARCH", "--heat": "HEAT", "-H": "HEAT", "--reset-threshold": "RESET_THRESHOLD", "-R": "RESET_THRESHOLD", "--long-search": "LONG_SEARCH", "-L": "LONG_SEARCH", "--fast-in": "FAST_IN", "-F": "FAST_IN", "--help": "_HELP", "-h": "_HELP"}
_TOGGLE = {"SHORTEST_MODE", "DETERMINISTIC", "PRINT_LOG", "WIKI_FORM", "_HELP"}
_args = {"GAME": None, "PLAYER": None, "SHORTEST_MODE": None, "DETERMINISTIC": None, "LUCK_PENALTY": None, "PRINT_LOG": None, "PRINT_ALL_THRESHOLD": None, "WIKI_FORM": None, "TRANSITION_THRESHOLD": None, "SHORT_SEARCH": None, "HEAT": None, "RESET_THRESHOLD": None, "LONG_SEARCH": None, "FAST_IN": None, "_HELP": None}
_selected = None
for argv in sys.argv:
    if argv in _ARGS:
        if _ARGS[argv] in _TOGGLE:
            _args[_ARGS[argv]] = True
            _selected = None
        else:
            _selected = _ARGS[argv]
    elif _selected is not None:
        if _args[_selected] is None:
            _args[_selected] = argv
        else:
            _args[_selected] += " " + argv

if _args["GAME"] is not None:
    GAME = _args["GAME"].lower()
elif len(sys.argv) > 1:
    GAME = sys.argv[1].lower()
if _args["PLAYER"] is not None:
    PLAYER = _args["PLAYER"].lower()
if _args["LUCK_PENALTY"] is not None:
    LUCK_PENALTY = float(_args["LUCK_PENALTY"])
if _args["PRINT_ALL_THRESHOLD"] is not None:
    PRINT_ALL_THRESHOLD = int(_args["PRINT_ALL_THRESHOLD"])
if _args["TRANSITION_THRESHOLD"] is not None:
    TRANSITION_THRESHOLD = int(_args["TRANSITION_THRESHOLD"])
if _args["SHORT_SEARCH"] is not None:
    SHORT_SEARCH = int(_args["SHORT_SEARCH"])
if _args["HEAT"] is not None:
    HEAT = float(_args["HEAT"])
if _args["RESET_THRESHOLD"] is not None:
    RESET_THRESHOLD = int(_args["RESET_THRESHOLD"])
if _args["LONG_SEARCH"] is not None:
    LONG_SEARCH = int(_args["LONG_SEARCH"])
if _args["FAST_IN"] is not None:
    FAST_IN = int(_args["FAST_IN"])
SHORTEST_MODE = SHORTEST_MODE if _args["SHORTEST_MODE"] is None else _args["SHORTEST_MODE"]
DETERMINISTIC = DETERMINISTIC if _args["DETERMINISTIC"] is None else _args["DETERMINISTIC"]
PRINT_LOG = PRINT_LOG if _args["PRINT_LOG"] is None else _args["PRINT_LOG"]
WIKI_FORM = WIKI_FORM if _args["WIKI_FORM"] is None else _args["WIKI_FORM"]
_HELP = _HELP if _args["_HELP"] is None else _args["_HELP"]

# INIT: set up initial variables based on config

if _HELP:
    print(f"")
    print(f"Usage: {sys.argv[0]} [Game] [Flags...]")
    print(f"")
    print(f"--help, -h")
    print(f"prints this help message")
    print(f"")
    print(f"-------------------------------------------------------")
    print(f"")
    print(f"--game [GAME], -g [GAME]")
    print(f"redundant flag, sets the game")
    print(f"currently allowed values: \"yume\", \"2kki\", \"flow\", \"prayers\", \"someday\", \"muma\"")
    print(f"")
    print(f"--player [PLAYER], -p [PLAYER]")
    print(f"uses a special character instead of a default character, which is a fresh save of each games")
    print(f"currently allowed values: \"madotsuki_100%\", \"urotsuki_100%\", \"fluorette_100%\", \"itsuki_100%\"")
    print(f"")
    print(f"--shortest-mode, -s")
    print(f"find a map with deepest path (i.e. Depths) instead")
    print(f"")
    print(f"--deterministic, -d")
    print(f"instead of the three-step nondeterministic method, find all possibility before moving to the next depth, DO NOT TURN ON FOR 2KKI (your pc will die)")
    print(f"does not do anything if shortest-mode is true")
    print(f"")
    print(f"--luck-penalty [number], -l [number]")
    print(f"point penalty for luck-based travel, luck based paths are disallowed by default")
    print(f"")
    print(f"--verbose, -v")
    print(f"prints progress messages. if false, only prints new findings/results")
    print(f"")
    print(f"--print-all-threshold [integer], -P [integer]")
    print(f"print all paths over this many worlds deep. used to find tied paths. disabled by default")
    print(f"")
    print(f"--wiki, -w")
    print(f"print result in wiki form (for use in yume.wiki/User:prodzpod and whatnot)")
    print(f"")
    print(f"-------------------------------------------------------")
    print(f"")
    print(f"advanced settings: ONLY WORKS on shortest-mode = FALSE and deterministic = FALSE (default values)")
    print(f"")
    print(f"--transition-threshold [integer], -t [integer]")
    print(f"minimum path length needed to \"stick\" to that path")
    print(f"")
    print(f"--short-search [integer], -S [integer]")
    print(f"number of iteration to check before moving onto next")
    print(f"")
    print(f"--heat [number], -H [number]")
    print(f"chance per connection to \"shuffle\" each short search failure")
    print(f"")
    print(f"--reset-threshold [integer], -R [integer]")
    print(f"number of short search failure to completely reset the set, set to -1 to disable")
    print(f"")
    print(f"--long-search [integer], -L [integer]")
    print(f"number of iteration to check before progress update")
    print(f"")
    print(f"--fast-in [integer], -F [integer]")
    print(f"maximum number of worlds to obtain the \"go fast\" effect. paths that does not get it before then are discarded early. disabled by default")
    print(f"")
    sys.exit()

if GAME is None:
    print(f"")
    print(f"Usage: {sys.argv[0]} [Game] [Flags...]")
    print(f"Enter {sys.argv[0]} -h for help")
    print(f"")
    sys.exit()

if GAME not in CONNECTIONS:
    print(f"")
    print(f"Error: Invalid Game")
    print(f"")
    sys.exit()

_connections = CONNECTIONS[GAME]
_name = (_connections.player_name if PLAYER is None else PLAYER).lower()

if _name not in PLAYERS:
    print(f"")
    print(f"Error: Invalid Player")
    print(f"")
    sys.exit()

print(f"")
print(f"---------- UROBOT+ v1.0 ----------")
print(f"                                  ")
print(f"                /---⧷             ")
print(f"                |    ⧷--o         ")
print(f"              o-!-o               ")
print(f"            -/     ⧷-             ")
print(f"           /         ⧷            ")
print(f"          o           ⧷           ")
print(f"          /            o          ")
print(f"         o              ⧷         ")
print(f"         |     o⧷       |         ")
print(f"        /   o  | ⧷  o    ⧷        ")
print(f"       o--o/ ⧷o   o/ ⧷o--o        ")
print(f"          |  -     -  |   ----    ")
print(f"          | | |   | | |  |{random.choice(['awoo', 'AWOO', 'aWOO', 'Awoo', 'weed', ' 28 ', ' 28?', '????', 'uwu ', ' owo', 'O WO', '0110', '0011', 'beep', 'boop', 'hehe', 'helo', 'hi:3', 'nom!', 'GET!', 'GET☆', 'GET♡', 'nasu', '!!!!', 'AAAA', ' AH ', ' :3 ', ' :0 ', ' :D ', ' :) ', 'yeah', 'THE FOG IS COMING. 02/13/2025. 13:55:23. YOU CANNOT STOP IT. YOU CAN HIDE BUT IT WILL ALWAYS FOLLOW YOU. REALITY IS A MIRAGE. YOU WILL FOREVER WANDER IN THE FOG, SEARCHING FOR AN ANSWER. WHEN YOU ARE MET WITH THE FOG, YOU WILL HAVE NO OPTION BUT TO SUBMIT TO IT. YOU MAY FEAR THE FOG, BUT KNOW IT IS MERELY A MEANS TO AN END.'])}|   ")
print(f"          o  -     -  o  /----    ")
print(f"          |⧷         /|           ")
print(f"          o ⧷o-----o/ o           ")
print(f"                                  ")
print(f"------ PRODZPOD+PRODUCTIONS ------")
print(f"")

print(f"Loaded Game: {_connections.game_name}")
initial_player = PLAYERS[_name] ##################################################### Player
playername = _connections.player_name ############################################### str
print(f"Loaded Player: {playername} ({_name})")
initial_player.path.append(initial_player.current_map)
initial_player.point += _connections.start_point

fast_effect = _connections.fast_effect ############################################## str
print("")

print(f"Loading Map Data...")
maps = _connections.maps ############################################################ dict[Map]
print(f"Found {len(maps)} maps.")
print(f"Applying Effect Data...")
for k in maps:
    random.shuffle(maps[k])
    for l in maps[k]:
        if l.name in _connections.simple_effects:
            l.effect.add(_connections.simple_effects[l.name])
print(f"Done.")
print("")
print(random.choice([
    f"Tip: press Ctrl+C at any point to stop the search.", 
    f"Tip: press Ctrl+C at any point to stop the search.", 
    f"Tip: press Ctrl+C at any point to stop the search.", 
    f"Tip: press Ctrl+C at any point to stop the search.", 
    f"Tip: press Ctrl+C at any point to stop the search.", 
    f"Tip: use \"{sys.argv[0]} -h\" to get help.",
    f"Tip: use \"{sys.argv[0]} -h\" to get help.",
    f"Tip: use \"{sys.argv[0]} -h\" to get help.",
    f"Tip: You Will Visit Star Building.",
    f"Tip: nom!",
    f"Tip: icon is a modification of Constellation World urotsuki constellation. thanks for spelude :p",
    f"Tip: Wooded Lakeside A → Oblique Hell tutorial: First entrance to maze, go up until fork in the road, right, enter closest boat, exit at the shortest pier, go up until long boardwalk, follow boardwalk to dark forest",
    f"Tip: awoo!",
    f"Tip: the time is {datetime.datetime.now()}.",
    f"Tip: Keep Dreaming!",
    f"Tip: You need low insanity for Serene Hill event/badge.",
    f"Tip: Check out \"yume.wiki/User:prodzpod\"!"
    ]))
print("")

iteration = 0 ####################################################################### int
best_depth = TRANSITION_THRESHOLD ######################################################## float
queue = deque([initial_player]) ##################################################### deque[Player]

# utils

def traversable(player, map):
    return map.name not in player.path and map.required <= player.effect and not (LUCK_PENALTY < (player.point - 3) and map.luck_based) and all(v not in player.effect for v in map.anti_required)

def traverse(player, map):
    return Player(
        map.name, 
        player.effect.union(map.effect), 
        player.path + [map.name], 
        player.point + 1 + (LUCK_PENALTY if map.luck_based == True else 0)
    )

def print_path(player):
    path = list(map(lambda x: f"[[{_connections.game_name}:{x}|{x}]]", player.path)) if WIKI_FORM else player.path
    ret = f"Path: {' → '.join(path)}"
    print(ret)
    return ret

def print_effects(player):
    EFFECT = {"Bike": "Bike/Motorcycle", "Lantern": "Lantern/Torch", "Fairy": "Fairy/Yousei", "School Boy": "School_Boy_(Gakuran)", "Teru Teru Bozu": "Teru Teru Bōzu (Paper Doll)", "Bunny Ears": "Bunny Ears/Usamimi"}
    effect = list(map(lambda x: f"[[{_connections.game_name}:Effects#{EFFECT[x] if x in EFFECT else x}|{EFFECT[x] if x in EFFECT else x}]]", player.effect)) if WIKI_FORM else player.effect
    ret = f"Unlocks gained: {', '.join(effect)}"
    print(ret)
    return ret

# Actual main

def find_shortest():
    global iteration, best_depth   
    explored = deque([initial_player.current_map]) # deque[str]
    print(f"Deepest World Search Started at {initial_player.current_map}")
    print(f"")
    while queue:
        iteration += 1
        player = queue.popleft()
        for map in maps[player.current_map]:
            if map.name not in explored and traversable(player, map):
                new_player = traverse(player, map)
                if "!" not in new_player.effect and not (FAST_IN > 0 and new_player.point >= FAST_IN and fast_effect in new_player.effect):
                    queue.append(new_player)
                    explored.append(new_player.current_map)
                if new_player.point > best_depth or (PRINT_ALL_THRESHOLD >= 0 and new_player.point >= PRINT_ALL_THRESHOLD):
                    print(f"New location reached by {playername} #{iteration} ({new_player.point} worlds deep)")
                    print_path(new_player)
                    print_effects(new_player)   
                    print("")
                    best_depth = new_player.point        

def find_longest():
    global queue, iteration, best_depth
    slow_search = False
    resets = 0
    milestone = SHORT_SEARCH
    print(f"Longest Path Search Started at {initial_player.current_map}")
    print(f"")
    while queue:
        iteration += 1
        milestone -= 1
        player = queue.popleft() if DETERMINISTIC else queue.pop()
        if milestone <= 0:
            if slow_search:
                log(f"{playername} #{iteration} reached")
                milestone = LONG_SEARCH
            else:
                resets += 1
                queue = deque([initial_player])
                milestone =  SHORT_SEARCH
                if resets % RESET_THRESHOLD == 0:
                    print(f"{playername} #{iteration} reached without meeting the threshold, full reset... (#{resets})")
                    for v in maps:
                        random.shuffle(maps[v])
                else:
                    log(f"Mutating list, reset #{resets} ({playername} #{iteration})")
                    for v in maps:
                        if random.random() < (HEAT * len(maps[v])):
                            _temp = deque(maps[v])
                            _temp.append(_temp.popleft())
                            maps[v] = _temp
                continue
        for map in maps[player.current_map]:
            if traversable(player, map):
                new_player = traverse(player, map)
                if new_player.point > best_depth or (PRINT_ALL_THRESHOLD >= 0 and new_player.point >= PRINT_ALL_THRESHOLD):
                    print(f"New location reached by {playername} #{iteration} ({new_player.point} worlds deep)")
                    print_path(new_player)
                    print_effects(new_player)   
                    print("")
                    best_depth = new_player.point     
                    milestone = LONG_SEARCH
                    slow_search = True
                if "!" not in new_player.effect and not (FAST_IN > 0 and new_player.point >= FAST_IN and fast_effect in new_player.effect):
                    queue.append(new_player)





# Main

if SHORTEST_MODE:
    find_shortest()
else:
    find_longest()
print("All possibilities have been tested. Final answer is above.")
print("")