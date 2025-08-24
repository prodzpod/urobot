"""
to generate a "2kki_pre" file:
- go to https://explorer.yume.wiki/
- developer console
- await(await fetch("https://explorer.yume.wiki/data")).json().worldData.map(x => { return {id: x.id, name: x.title, exits: x.connections}; }); 
- copy object on the output & save it as "2kki_pre.json"
"""
import json
import re
EFFECTS = {
    "Glasses": ["Dark Museum"],
    "Spacesuit": ["Flying Fish World"],
    "Fairy": ["Black Building"],
    "Chainsaw": ["Hospital"],
    "Dice": ["Acerola World"],
    "Grave": ["Graveyard World"],
    "Polygon": ["Warehouse", "The Desktop"],
    "Rainbow": ["Theatre World"],
    "Marginal": ["Broken Faces Area"],
    "Boy": ["Geometry World"],
    "Bike": ["Garden World", "Portrait Purgatory"],
    "Maiko": ["Shinto Shrine"],
    "Plaster Cast": ["Japan Town", "Blissful Clinic"],
    "Stretch": ["Graffiti Maze", "Bodacious Rotation Station"],
    "Trombone": ["Acoustic Lounge"],
    "Bat": ["Tribe Settlement"],
    "Telephone": ["Dark Room"],
    "Cake": ["Cutlery World"],
    "Haniwa": ["Haniwa Temple"],
    "Tissue": ["White Fern World", "Azure Arm Land"],
    "Red Riding Hood": ["Fairy Tale Woods", "Birch Forest"],
    "Lantern": ["Forest World", "Rural Starflower Field"],
    "Gakuran": ["Monochrome Feudal Japan"],
    "Invisible": ["The Invisible Maze"],
    "Eyeball Bomb": ["Mini-Maze"],
    "Insect": ["Scenic Outlook"],
    "Teru Teru Bozu": ["Dark Alleys"],
}
EFFECTS_TRANSITORY = {
    "Drum": ["Purple World", "Onyx Tile World"],
    "Spring": ["Apartments", "Urotsuki's Dream Apartments"],
    "Penguin": ["Urotsuki's Dream Apartments", "Urotsuki's Room"],
    "Child": ["Ocean Floor", "Hourglass Desert"],
}
EFFECTS_PREREQUISITE = {
    "Twintails": ["The Deciding Street", "Telephone"],
    "Trombone": ["The Baddies Bar", "Chainsaw"],
}
ret = {
    "worlds": {},
    "flags": {
        "Season: SS/FW": None,
        "Season: SF/SW": None,
    },
    "start": "Urotsuki's Room"
}
backup_worlds = []
def create_metaworld(base, fns):
    global ret
    ret["flags"]["Metaworld: %s" % base] = False
    ret["worlds"][base]
    if "_GLOBAL" not in ret["worlds"][base]["grants"]: ret["worlds"][base]["grants"]["_GLOBAL"] = {}
    ret["worlds"][base]["grants"]["_GLOBAL"]["Metaworld: %s" % base] = True
    for entry in ret["worlds"]:
        if base in ret["worlds"][entry]["exits"]:
            ret["worlds"][entry]["exits"][base]["Metaworld: %s" % base] = False
    for i, fn in enumerate(fns):
        newv = "%s (%s)" % (base, str(i + 2))
        ret["worlds"][newv] = fn[0](json.loads(json.dumps(ret["worlds"][base])))
        for entry in ret["worlds"]:
            if base in ret["worlds"][entry]["exits"]:
                edge = fn[1](json.loads(json.dumps(ret["worlds"][entry]["exits"][base])), entry)
                if edge != None:
                    ret["worlds"][entry]["exits"][newv] = edge
with open("2kki_pre.json", encoding="utf8") as f:
    pre = f.read()
pre = json.loads(pre)
worlds = {}
for entry in pre:
    worlds[entry["id"]] = entry
for entry in pre:
    ret["worlds"][entry["name"]] = {"exits": {}, "grants": {}}
    for k, v in EFFECTS.items():
        if entry["name"] in v:
            if "_GLOBAL" not in ret["worlds"][entry["name"]]["grants"]: ret["worlds"][entry["name"]]["grants"]["_GLOBAL"] = {}
            ret["worlds"][entry["name"]]["grants"]["_GLOBAL"]["Effect: " + k] = True
    for e in entry["exits"]:
        # type 1: oneway (ignore)
        # type 2: onewayed (fake)
        # type 4: key (ignore)
        # type 8: lock (fake)
        # type 16: isolated (fake)
        # type 32: toisolate (stop)
        # type 64: effectlock
        # type 128: chance (ignore)
        # type 256: special
        # type 512: telephone (ignore)
        # type 1024: telephoned (fake)
        # type 2048: season
        if e["type"] & 8 > 0 or e["type"] & 2 > 0 or e["type"] & 16 > 0 or e["type"] & 1024 > 0: continue
        if e["type"] & 256 > 0: 
            if entry["name"] == "Constellation World" and worlds[e["targetId"]]["name"] == "Spacey Retreat":
                e["type"] = 64
                e["typeParams"] = { "64": {"params": "Bunny Ears,Spring" }}
            elif entry["name"] == "Sushi Belt World" and worlds[e["targetId"]]["name"] == "Humanism":
                e["type"] = 64
                e["typeParams"] = { "64": {"params": "Fairy,Spacesuit" }}
            else: continue # TODO: individual craziness
        if e["type"] & 32 > 0: 
            ret["worlds"][entry["name"]]["grants"][worlds[e["targetId"]]["name"]] = { "_STOP": True }
        ret["worlds"][entry["name"]]["exits"][worlds[e["targetId"]]["name"]] = {}
        for k, v in EFFECTS_TRANSITORY.items():
            if entry["name"] == v[0] and worlds[e["targetId"]]["name"] == v[1]:
                if worlds[e["targetId"]]["name"] not in ret["worlds"][entry["name"]]["grants"]: ret["worlds"][entry["name"]]["grants"][worlds[e["targetId"]]["name"]] = {}
                ret["worlds"][entry["name"]]["grants"][worlds[e["targetId"]]["name"]]["Effect: " + k] = True
        if e["type"] & 64 > 0:
            effects = re.split("&comma; | or |; |,", e["typeParams"]["64"]["params"])
            if len(effects) >= 1:
                eff = effects[0]
                eff = eff.replace("Teru Teru B\u014dzu", "Teru Teru Bozu")
                ret["flags"]["Effects: " + eff] = False
                if len(effects) > 1:
                    for eff in effects[1:]:
                        eff = eff.replace("Teru Teru B\u014dzu", "Teru Teru Bozu")
                        ret["flags"]["Effects: " + eff] = False
                    backup_worlds.append((entry["name"], worlds[e["targetId"]]["name"], effects))
                else: ret["worlds"][entry["name"]]["exits"][worlds[e["targetId"]]["name"]]["Effects: " + eff] = True
        if e["type"] & 2048 > 0:
            season = e["typeParams"]["2048"]["params"]
            ssfw = season == "Spring" or season == "Summer"
            sfsw = season == "Spring" or season == "Fall"
            ret["worlds"][entry["name"]]["exits"][worlds[e["targetId"]]["name"]]["Season: SS/FW"] = ssfw
            ret["worlds"][entry["name"]]["exits"][worlds[e["targetId"]]["name"]]["Season: SF/SW"] = sfsw
def effp1(w): w["grants"]["_GLOBAL"]["Effect: " + k] = True; return w
def _effp2(v1, w): w["Effect: " + v1] = True; return w
def effp2(v1): return lambda w, _: _effp2(v1, w)
for k, v in EFFECTS_PREREQUISITE.items():
    create_metaworld(v[0], [[effp1, effp2(v[1])]])
def effor1(w): return w
def _effor2(kv0, g, w, fr): w["Effect: " + g] = True; return w if fr == kv0 else None
def effor2(kv0, g): return lambda w, fr: _effor2(kv0, g, w, fr)
# manual
for kv in backup_worlds:
    create_metaworld(kv[1], [[effor1, effor2(kv[0], g)] for g in kv[2][1:]])
    ret["worlds"][kv[0]]["exits"][kv[1]]["Effects: " + kv[2][0]] = True
# Manual Changes Zone
ret["worlds"]["Sushi Belt World"]["exits"]["Humanism"]["Effect: Maiko"] = True
ret["worlds"]["Sushi Belt World"]["exits"]["Humanism (2)"]["Effect: Maiko"] = True
# enable the great virtualcity loopback
ret["worlds"]["Field of Cosmos"]["exits"]["Bubble World"] = {}
ret["worlds"]["Adabana Gardens"]["exits"]["Bubble World"] = {}
ret["worlds"]["Guts World"]["exits"]["Red Sewers"] = {}
ret["worlds"]["Guts World"]["grants"]["Red Sewers"] = {"qxy3 shortcut": True}
ret["worlds"]["Red Sewers"]["exits"]["Bubble World"] = {"qxy3 shortcut": True}
ret["worlds"]["Red Sewers"]["exits"]["Guts World"] = {"qxy3 shortcut": False}
ret["flags"]["qxy3 shortcut"] = False
ret["worlds"]["Glitched Butterfly Sector"]["exits"]["Sierpinski Maze"] = {}
ret["worlds"]["Virtual City"]["exits"]["River Complex"] = { "Effects: Telephone": True }
def rainy1(w): w["exits"]["Rainy Apartments"] = { "qxy3 shortcut": False }; return w
create_metaworld("Virtual City", [[rainy1, lambda w, fr: w if fr != "River Complex" else None]])
ret["worlds"]["River Complex"]["grants"].pop("Virtual City")
def rc1(w): w["exits"]["Christmas World"] = {}; w["exits"]["Highway"] = {}; w["exits"]["River Road A"] = {}; return w
create_metaworld("River Complex", [[rc1, lambda w, fr: w if fr != "Virtual City" and fr != "Smiling Trees World" else None]])
# apartment ufo divide
create_metaworld("Apartments", [[lambda w: w, lambda _, __: None]])
ret["worlds"]["Apartments (2)"]["exits"] = {"Forlorn Beach House": {}, "Fairy Tale Woods": {}, "Broken Faces Area": {}}
del ret["worlds"]["Broken Faces Area"]["exits"]["Forlorn Beach House"]
ret["flags"]["semivisited apartments"] = False
ret["worlds"]["Broken Faces Area"]["grants"]["Fairy Tale Woods"] = {"semivisited apartments": True}
ret["worlds"]["Library"]["exits"]["Apartments"] = {"semivisited apartments": True}
ret["worlds"]["Broken Faces Area"]["exits"]["Apartments (2)"] = {}
ret["worlds"]["Elvis Masada's Place"]["exits"]["Apartments (2)"] = {}
ret["worlds"]["Spelling Room"]["exits"]["Apartments (2)"] = {}
# abandoned chinatown divide
create_metaworld("Abandoned Chinatown", [[lambda w: w, lambda _, __: None]])
ret["worlds"]["Abandoned Chinatown (2)"]["exits"] = {"Laboratory": {}, "Limbus Plains": {}}
ret["worlds"]["Laboratory"]["exits"]["Abandoned Chinatown (2)"] = {}
ret["worlds"]["Limbus Plains"]["exits"]["Abandoned Chinatown (2)"] = {}
# balloon park divide
create_metaworld("Balloon Park", [[lambda w: w, lambda _, __: None]])
ret["worlds"]["Balloon Park"]["exits"] = {"Underground Subway": {}, "Dice Swamp": {}}
ret["worlds"]["Balloon Park (2)"]["exits"] = {"Worksite": {}, "Legacy Nexus": {}, "Bleeding Tree Disco": {}, "Cerulean School": {}}
del ret["worlds"]["Worksite"]["exits"]["Balloon Park"]
ret["worlds"]["Worksite"]["exits"]["Balloon Park (2)"] = {}
del ret["worlds"]["Bleeding Tree Disco"]["exits"]["Balloon Park"]
ret["worlds"]["Bleeding Tree Disco"]["exits"]["Balloon Park (2)"] = {}
del ret["worlds"]["Cerulean School"]["exits"]["Balloon Park"]
ret["worlds"]["Cerulean School"]["exits"]["Balloon Park (2)"] = {}
# maple forest divide
create_metaworld("Maple Forest", [[lambda w: w, lambda _, __: None]])
ret["worlds"]["Maple Forest (2)"]["exits"] = {"Four Seasons Forest": {}, "Deserted Center": {}}
ret["worlds"]["Four Seasons Forest"]["exits"]["Maple Forest (2)"] = {}
ret["worlds"]["Deserted Center"]["exits"]["Maple Forest (2)"] = {}
# 256s
ret["flags"]["visited forest pier"] = False
ret["worlds"]["Forest Pier"]["grants"]["_GLOBAL"] = { "visited forest pier": True }
ret["worlds"]["Black Building"]["exits"]["Town Maze"] = { "visited forest pier": True }
ret["flags"]["visited dream park"] = False
ret["worlds"]["Dream Park"]["grants"]["_GLOBAL"] = { "visited dream park": True }
ret["worlds"]["Chocolate World"]["exits"]["Butter Rain World"] = { "visited dream park": True, "Effect: Cake": True }
ret["worlds"]["Christmas World"]["exits"]["Sherbet Snowfield"] = { "visited dream park": True, "Effect: Teru Teru Bozu": True }
ret["worlds"]["Geometry World"]["exits"]["Sound Saws World"] = { "visited dream park": True, "Effect: Boy": True }
ret["worlds"]["Heart World"]["exits"]["Cipher Fog World"] = { "visited dream park": True, "Effect: Crossing": True }
ret["flags"]["visited japan town"] = False
ret["worlds"]["Japan Town"]["grants"]["_GLOBAL"] = { "visited japan town": True }
ret["worlds"]["Chocolate World"]["exits"]["Sewers"] = { "visited japan town": True, "Effect: Boy": True }
ret["worlds"]["Tapir-San's Place"]["exits"]["Sewers"] = { "visited japan town": True, "Effect: Boy": True }
ret["worlds"]["Dark Room"]["exits"]["Tribe Settlement"] = {}
ret["worlds"]["Constellation World"]["exits"]["Red Lily Lake"] = {}
ret["worlds"]["Constellation World"]["exits"]["Innocent Dream"] = { "Effect: Penguin": True }
ret["worlds"]["Data Stream"]["exits"]["Binary World"] = {}
ret["flags"]["visited stone towers"] = False
ret["worlds"]["Stone Towers"]["grants"]["_GLOBAL"] = { "visited stone towers": True }
ret["worlds"]["Dream Park"]["exits"]["Underground Passage"] = { "visited stone towers": True }
ret["worlds"]["Gray Road"]["exits"]["Techno Condominium"] = {}
ret["worlds"]["Intestines Maze"]["exits"]["Floating Tiled Islands"] = {}
ret["worlds"]["Intestines Maze"]["grants"]["Floating Tiled Islands"] = { "_STOP": True }
ret["worlds"]["Library"]["exits"]["Maiden Outlook"] = {}
ret["worlds"]["Library"]["exits"]["Character Plains"] = {}
ret["worlds"]["Lamp Passage"]["exits"]["Flesh Paths World"] = { "Effect: Chainsaw": True }
ret["flags"]["polluted swamp way"] = False
ret["worlds"]["Underground Laboratory"]["grants"]["Polluted Swamp"] = { "polluted swamp way": True }
ret["worlds"]["Polluted Swamp"]["exits"]["The Rooftops"] = { "polluted swamp way": True, "Effect: Chainsaw": True }
ret["worlds"]["Polluted Swamp"]["exits"]["Toxic Sea"] = { "polluted swamp way": True, "Effect: Chainsaw": True }
ret["worlds"]["Realistic Beach"]["exits"]["Teleport Maze"] = { "Effect: Fairy": True }
ret["worlds"]["School"]["exits"]["Hat World"] = {}
ret["flags"]["visited silent sewers"] = False
ret["worlds"]["Silent Sewers"]["grants"]["_GLOBAL"] = { "visited silent sewers": True }
ret["worlds"]["Rusted City"]["exits"]["Ruined Garden"] = { "visited silent sewers": True }
ret["worlds"]["Space"]["exits"]["Urban Street Area"] = { "Effect: Fairy": True }
ret["worlds"]["Tan Desert"]["exits"]["Evergreen Woods"] = {}
ret["worlds"]["Toy World"]["exits"]["Zodiac Fortress"] = {}
ret["worlds"]["Toy World"]["exits"]["Mouse Den"] = {}
ret["flags"]["visited rainbow ruins"] = False
ret["worlds"]["Bright Forest"]["grants"]["_GLOBAL"] = { "visited rainbow ruins": True }
ret["worlds"]["Urotsuki's Dream Apartments"]["exits"]["Ethnic World"] = { "visited rainbow ruins": True }
ret["worlds"]["Phosphorus World"]["exits"]["Forest Interlude"] = {}
ret["flags"]["visited lovesick world"] = False
ret["worlds"]["Lovesick World"]["grants"]["_GLOBAL"] = { "visited lovesick world": True }
ret["worlds"]["Opal Ruins A"]["exits"]["Blue Lavender Shoal"] = { "visited lovesick world": True }
ret["worlds"]["Shop Ruins"]["exits"]["Blood Cell Sea"] = { "Effect: Chainsaw": True }
ret["worlds"]["Blood Cell Sea"]["exits"]["Stuffed Dullahan World"] = { "Effect: Chainsaw": True }
ret["worlds"]["Rock World"]["exits"]["Sanctuary"] = {}
ret["worlds"]["Forest Pier"]["exits"]["Hidden Shoal"] = { "Effect: Chainsaw": True }
ret["worlds"]["Silhouette Complex"]["exits"]["Grand Beach"] = { "Effect: Drum": False }
ret["worlds"]["Decrepit Village"]["exits"]["Carnivorous Pit"] = { "Effect: Chainsaw": True }
ret["worlds"]["Ornamental Plains"]["exits"]["Wrinkled Fields"] = { "Effect: Child": True }
ret["worlds"]["Hat World"]["exits"]["School"] = {}
ret["worlds"]["Hat World"]["exits"]["Microbiome World"] = {}
ret["worlds"]["Blue Eyes World"]["exits"]["Restored Character World"] = {}
ret["worlds"]["Scrapyard"]["exits"]["Corridor of Eyes"] = {}
ret["worlds"]["Rice Dumpling Plateau"]["exits"]["Corridor of Eyes"] = {}
ret["worlds"]["Butterfly Garden"]["exits"]["Sakura Forest"] = {}
ret["worlds"]["Butterfly Garden"]["exits"]["Astronomical Gallery"] = {}
ret["worlds"]["Microbiome World"]["exits"]["Hat World"] = {}
ret["worlds"]["Knife World"]["exits"]["Abyssal Garden"] = {}
ret["worlds"]["Abyssal Garden"]["exits"]["Knife World"] = {}
ret["flags"]["visited thumbtack world"] = False
ret["worlds"]["Thumbtack World"]["grants"]["_GLOBAL"] = { "visited thumbtack world": True }
ret["worlds"]["Rice Field"]["exits"]["Beyond"] = { "visited thumbtack world": True }
ret["worlds"]["Beyond"]["exits"]["Rice Field"] = { "visited thumbtack world": True }
ret["flags"]["visited Copper Tube Desert"] = False
ret["worlds"]["Copper Tube Desert"]["grants"]["_GLOBAL"] = { "visited Copper Tube Desert": True }
ret["worlds"]["Bacteria World"]["exits"]["Dark Red Wasteland"] = { "visited Copper Tube Desert": True }
ret["worlds"]["Ice Block World"]["exits"]["Glitch Hell"] = {}
ret["worlds"]["Ice Block World"]["exits"]["Witch Heaven"] = {}
ret["worlds"]["Witch Heaven"]["exits"]["Ice Block World"] = {}
ret["worlds"]["Witch Heaven"]["exits"]["Pink Life World"] = {}
ret["worlds"]["Pink Life World"]["exits"]["Witch Heaven"] = {}
ret["worlds"]["Warzone"]["exits"]["Video Game Graveyard"] = {}
ret["worlds"]["Blue Sanctuary"]["exits"]["Candlelit Factory"] = {}
ret["flags"]["visited Expanded Corridors"] = False
ret["worlds"]["Expanded Corridors"]["grants"]["_GLOBAL"] = { "visited Expanded Corridors": True }
ret["worlds"]["Blue Sanctuary"]["exits"]["Quarter Flats"] = { "visited Expanded Corridors": True }
ret["worlds"]["Labyrinth of Dread"]["exits"]["Crow Forest"] = {}
ret["worlds"]["Floating Tiled Islands"]["exits"]["Intestines Maze"] = {}
ret["worlds"]["Garden World"]["exits"]["Board Game Islands"] = { "Effect: Child": True }
ret["worlds"]["Bishop Cathedral"]["exits"]["Board Game Islands"] = { "Effect: Child": True }
ret["worlds"]["Board Game Islands"]["exits"]["Bishop Cathedral"] = {}
ret["worlds"]["Board Game Islands"]["exits"]["Garden World"] = {}
ret["worlds"]["Entrails"]["exits"]["Domino Maze"] = { "Effect: Child": True }
ret["worlds"]["Domino Maze"]["exits"]["Entrails"] = {}
ret["worlds"]["Lit Tile Path"]["exits"]["Obstacle Course 2"] = {}
ret["worlds"]["Reef Maze"]["exits"]["Lost Forest"] = {}
ret["worlds"]["Reef Maze"]["exits"]["Haunted Laboratory"] = {}
ret["worlds"]["Reef Maze"]["exits"]["Hall of Memories"] = {}
ret["worlds"]["Lost Forest"]["exits"]["Reef Maze"] = {}
ret["worlds"]["Haunted Laboratory"]["exits"]["Reef Maze"] = {}
ret["worlds"]["Hall of Memories"]["exits"]["Reef Maze"] = {}
ret["worlds"]["Nefarious Chessboard"]["exits"]["Fake Apartments"] = {}
ret["worlds"]["3D Underworld"]["exits"]["Oblique Hell"] = {}
ret["flags"]["visited Sepia Clouds World"] = False
ret["worlds"]["Sepia Clouds World"]["grants"]["_GLOBAL"] = { "visited Sepia Clouds World": True }
ret["worlds"]["Somber Establishment"]["exits"]["Submerged Signs World"] = { "visited Sepia Clouds World": True }
ret["worlds"]["Somber Establishment"]["exits"]["Ruby Forest"] = { "visited Sepia Clouds World": True }
ret["worlds"]["Birch Forest"]["exits"]["Magnet Room"] = {}
ret["worlds"]["Birch Forest"]["exits"]["Thumbtack World"] = {}
ret["worlds"]["Collision World"]["exits"]["Doodle Path"] = {}
ret["worlds"]["Abandoned Campsite"]["exits"]["Mourning Void"] = {}
ret["worlds"]["Shrouded Arcadia"]["exits"]["Potato World"] = {}
ret["worlds"]["Burger Joint"]["exits"]["Potato World"] = {}
ret["worlds"]["Archived Aqueduct"]["exits"]["Ballerina Forest"] = {}
ret["worlds"]["Sorrow and Comfort Monuments"]["exits"]["Character Plains"] = {}
ret["worlds"]["Abandoned Joes"]["exits"]["Black Dust Desert"] = {}
ret["worlds"]["Journey's Road"]["exits"]["Psychedelic Letter World"] = {}
ret["worlds"]["Night World"]["exits"]["Crossing Forest"] = { "Effect: Crossing": True }
ret["worlds"]["Pen Passage"]["exits"]["Restored Character World"] = {}
ret["worlds"]["Regretful Seas"]["exits"]["Seafloor Dungeon"] = {}
ret["worlds"]["Lake of Bones"]["exits"]["Hemlock Lab"] = { "Effect: Chainsaw": True }
ret["worlds"]["Hemlock Lab"]["exits"]["Recursive Warehouse"] = {}
ret["worlds"]["Loquat Orchard"]["exits"]["Somber Waterfront"] = {}
ret["worlds"]["Loquat Orchard"]["grants"]["Somber Waterfront"] = { "_STOP": True }
ret["worlds"]["Otherworldly Bar"]["exits"]["Somber Waterfront"] = {}
ret["worlds"]["Otherworldly Bar"]["grants"]["Somber Waterfront"] = { "_STOP": True }
ret["worlds"]["Pen Passage"]["exits"]["Somber Waterfront"] = {}
ret["worlds"]["Pen Passage"]["grants"]["Somber Waterfront"] = { "_STOP": True }
ret["worlds"]["Bone Zone"]["exits"]["Crow's Nest"] = {}
ret["worlds"]["Bone Zone"]["grants"]["Crow's Nest"] = { "_STOP": True }
ret["flags"]["visited The Second Nexus"] = False
ret["worlds"]["The Second Nexus"]["grants"]["_GLOBAL"] = { "visited The Second Nexus": True }
ret["worlds"]["Shallow Pathways"]["exits"]["Kelp Forest"] = { "visited The Second Nexus": True }
ret["flags"]["visited Dream Precinct"] = False
ret["worlds"]["Dream Precinct"]["grants"]["_GLOBAL"] = { "visited Dream Precinct": True }
ret["worlds"]["Burgundy Flats"]["exits"]["Disfigured Expanse"] = { "visited Dream Precinct": True }
ret["flags"]["visited Fish Person Shoal"] = False
ret["worlds"]["Fish Person Shoal"]["grants"]["_GLOBAL"] = { "visited Fish Person Shoal": True }
ret["worlds"]["Somber Waterfront"]["exits"]["Quarter Flats"] = { "visited Fish Person Shoal": True }
# End of Manual Changes Zone
with open("2kki.json", "w", encoding="utf8") as f:
    f.write(json.dumps(ret))
print("Done!")