import os
import json
import random
NUM_WORLDS = 2000
CONNECTEDNESS = 0.002
ONEWAYNESS = 0.2
#
ret = { "worlds": {}, "flags": {}, "start": "" }
ret["start"] = str(random.randint(1, NUM_WORLDS))
for i in range(1, NUM_WORLDS + 1):
    ret["worlds"][str(i)] = {"exits": {}}
    for j in range(1, NUM_WORLDS + 1):
        if i == j: continue # no connect to self
        if random.random() < CONNECTEDNESS:
            ret["worlds"][str(i)]["exits"][str(j)] = {}
for i in range(1, NUM_WORLDS + 1):
    for j in range(1, NUM_WORLDS + 1):
        if i == j or j in ret["worlds"][str(i)]["exits"] or i not in ret["worlds"][str(j)]["exits"]: continue
        if random.random() >= ONEWAYNESS:
            ret["worlds"][str(i)]["exits"][str(j)] = {}
with open("generated.json", "w") as f:
    f.write(json.dumps(ret))
print("Done!")