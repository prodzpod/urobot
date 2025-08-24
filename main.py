import os
import sys
import json
import math
import time
import random
from collections import deque
from functools import reduce
from z3 import *
def can_cast(source, dest_type):
    try:
        dest_type(source)
        return True
    except Z3Exception:
        return False
def st_time(func):
    """
        st decorator to calculate the total time of a func
    """
    def st_func(*args, **keyArgs):
        t1 = time.time()
        r = func(*args, **keyArgs)
        t2 = time.time()
        print("Function=%s, Time=%s" % (func.__name__, t2 - t1))
        return r
    return st_func
def get_instructions(ans):
    global FINAL_TXT
    if ans == False:
        print("Path of length " + str(GOAL) + " not found")
        return False
    print("Path of length " + str(GOAL) + " found")
    FINAL_TXT = ""
    if str(ans.arg(0).children()[0].sort()) == "Bool":
        for i, x in enumerate(ans.children()):
            if i >= 10:
                FINAL_TXT += "\n" + ("  ...")
                break
            FINAL_TXT += "\n" + ("  Answer Number " + str(i+1) + ":")
            print_answer(x)
    else:
        print_answer(ans)
    return True
def print_answer(ans):
    global FINAL_TXT
    lastAnd = ans.arg(len(WORLDS) + len(FLAGS) + 1).children()[-1]
    trace = lastAnd.children()[0]
    ret = []
    while trace.num_args() > 0:
        ret.append(trace.decl())
        trace = trace.children()[-1]
    ret.reverse()
    FINAL_TXT += "\n" + ("    Flags: " + ", ".join([f.name for i, f in enumerate(FLAGS) if ans.arg(len(WORLDS) + i + 1).children()[-1] == True]))
    FINAL_TXT += "\n" + ("    1: " + START)
    for i, t in enumerate(ret): FINAL_TXT += "\n" + ("    " + str(i + 2) + ": " + str(t))
#
def const_visited():
    return Const("visited", INT)
def const_current():
    return Const("current", INT)
def id_from_name(name):
    for i, w in enumerate(WORLDS):
        if w.name == name:
            return BitVecVal(i, INT)
    return 0
def state_but(defs):
    ret = []
    if "visited" in defs:
        ret.append(defs["visited"])
    else: ret.append(const_visited())
    if "current" in defs:
        ret.append(defs["current"])
    else: ret.append(const_current())
    for w in WORLDS:
        if ("W_" + w.name) in defs:
            ret.append(defs["W_" + w.name])
        else: ret.append(w.get_const())
    for f in FLAGS:
        if ("F_" + f.name) in defs:
            ret.append(defs["F_" + f.name])
        else: ret.append(f.get_const())
    return state(ret)
class World():
    def __init__(self, name, dests, grants, increment=1):
        self.name = name
        self.dests = dests
        self.grants = grants
        self.increment = increment
    def get_const(self):
        return Const("W_" + self.name, BOOL)
    def add_dests(self, fp):
        for k, v in self.dests.items():
            kw = [w for w in WORLDS if w.name == k][0]
            _from = { "current": id_from_name(self.name), "W_" + k: False, "F__STOP" : False }
            _to = { "visited": const_visited() + kw.increment, "current": id_from_name(k), "W_" + k: True }
            for flag, val in v.items():
                _from["F_" + flag] = val
                _to["F_" + flag] = val
            if k in self.grants: 
                for flag, status in self.grants[k].items():
                    _to["F_" + flag] = status
            if "_GLOBAL" in kw.grants:
                for flag, status in kw.grants["_GLOBAL"].items():
                    _to["F_" + flag] = status
            branches = [k for k, v in _to.items() if v == None]
            add_rule(fp, k, _from, _to, branches)
def add_rule(fp, k, _from, _to, branches):
    global TOTAL
    if len(branches) == 0:
        fp.rule(state_but(_to), [state_but(_from)], k)
    else:
        _to[branches[0]] = True
        add_rule(fp, k, _from, _to, branches[1:])
        _to[branches[0]] = False
        add_rule(fp, k, _from, _to, branches[1:])
class Flag():
    def __init__(self, name, initial=False):
        self.name = name
        self.initial = initial
    def get_const(self):
        return Const("F_" + self.name, BOOL)
    def start_check(self):
        worldgrants = [w for w in WORLDS if w.name == START][0].grants
        if "_GLOBAL" in worldgrants:
            worldglobal = worldgrants["_GLOBAL"]
            initial = worldglobal[self.name] if self.name in worldglobal else self.initial
        else: initial = self.initial
        if initial == None: return self.get_const()
        else: return initial
#
CONFIG = {}
with open("@config.json") as f:
    CONFIG = json.loads(f.read())
WORLDS = []
FLAGS = []
START = ""
GOAL = CONFIG["general"]["start_goal"]
BFS_UNTIL = CONFIG["bruteforce"]["bfs_until"]
FINAL_TXT = ""
#
print("\nUROBOT 2.0\n")
if os.path.exists(sys.argv[1]):
    with open(sys.argv[1]) as f:
        file = json.loads(f.read())
    for k, v in file["worlds"].items():
        WORLDS.append(World(k, v["exits"], v["grants"] if "grants" in v else {}))
    for k, v in file["flags"].items():
        FLAGS.append(Flag(k, v))
    FLAGS.append(Flag("_STOP"))
    START = file["start"]
else: print("File does not exist!")
#
TOTAL = reduce(lambda a, b: a + b, [w.increment for w in WORLDS])
INT = BitVecSort(math.ceil(math.log2(TOTAL)) + 1)
BOOL = BoolSort()
state = Function("state", [INT, INT] + [BOOL for _ in WORLDS] + [BOOL for _ in FLAGS] + [BOOL])
def z3_search(fp=None):
    global START, GOAL
    if fp == None:
        fp = Fixedpoint()
        fp.set("engine", "datalog", "datalog.generate_explanations", True)
        fp.register_relation(state)
        fp.declare_var([const_visited(), const_current()] + [w.get_const() for w in WORLDS] + [f.get_const() for f in FLAGS])
        fp.fact(state([BitVecVal(1, INT), id_from_name(START)] + [w.name == START for w in WORLDS] + [f.start_check() for f in FLAGS]))
        print("Adding Constraints")
        for w in WORLDS:
            if CONFIG["general"]["verbose"]: print("Adding Constraints (" + str(WORLDS.index(w) + 1) + " / " + str(len(WORLDS)) + ")")
            w.add_dests(fp)
    fp.query(state([BitVecVal(GOAL, INT), const_current()] + [w.get_const() for w in WORLDS] + [f.get_const() for f in FLAGS]))
    res = get_instructions(fp.get_answer())
    if can_cast(res, bool) and bool(res) == False:
        print("Final Length: " + str(GOAL - 1) + ", Terminating")
    else: 
        print(FINAL_TXT)
        GOAL += 1
        z3_search(fp) 
DONE = False
class Bruteforce_Path():
    def __init__(self, point, path, flags):
        self.point = point
        self.path = path
        self.flags = flags
    def __eq__(self, other):
        if other is not Bruteforce_Path: return False
        if self.path[-1] != other.path[-1]: return False
        if len(self.path) != len(other.path): return False
        for w in self.path: 
            if w not in other.path: return False
        if len(self.flags) != len(other.flags): return False
        for w in self.flags: 
            if w not in other.flags[w] or self.flags[w] != other.flags[w]: return False
        return True
    def traverse(self, fs, w):
        global WORLDS2
        cw = WORLDS2[w]
        success = True
        ret = Bruteforce_Path(self.point + cw.increment, self.path[:] + [w], self.flags.copy())
        for k, v in fs.items():
            if v == False and k not in self.flags:
                continue
            if k not in self.flags:
                success = False
                break
            if self.flags[k] == None:
                ret.flags[k] = v
                continue
            if ret.flags[k] == v:
                continue
            else:
                success = False
                break
        sw = WORLDS2[self.path[-1]]
        if w in sw.grants:
            for k, v in sw.grants[w].items():
                ret.flags[k] = v
        if "_GLOBAL" in cw.grants:
            for k, v in cw.grants["_GLOBAL"].items():
                ret.flags[k] = v
        return ret if success else None
WORLDS2 = {}
def bruteforce_search():
    global GOAL, DONE, WORLDS, WORLDS2
    # pretreatment
    for w in WORLDS:
        w.finalbonus = 0
        for k, v in w.grants.items():
            if "_STOP" in v:
                del w.dests[k]
                w.finalbonus = 1
        w.finalworlds = []
    pretreatment_finished = False
    while pretreatment_finished == False:
        pretreatment_finished = True
        for w in [w for w in WORLDS if len(w.dests) == 0]:
            for entry in WORLDS:
                if w.name in entry.dests and entry.dests[w.name] == {}:
                    pretreatment_finished = False
                    if w.finalbonus + w.increment > entry.finalbonus:
                        entry.finalbonus = w.finalbonus + w.increment
                        entry.finalworlds = w.finalworlds + [w.name]
                    del entry.dests[w.name]
        for w in [w for w in WORLDS if len(w.dests) == 1 and w.dests[next(iter(w.dests))] == {}]:
            for entry in WORLDS:
                if w.name in entry.dests and entry.dests[w.name] == {}:
                    pretreatment_finished = False
                    if w.finalbonus + w.increment > entry.finalbonus:
                        entry.finalbonus = w.finalbonus + w.increment
                        entry.finalworlds = w.finalworlds + [w.name]
                    del entry.dests[w.name]
    pretreatment_finished = False
    while pretreatment_finished == False:
        rfound = deque([])
        for entry in WORLDS:
            for k in entry.dests:
                if k not in rfound: rfound.append(k)
        pretreatment_finished = len(rfound) != 0
        WORLDS = [w for w in WORLDS if w.name in rfound]
    for w in WORLDS:
        WORLDS2[w.name] = w
    found = []
    last_found = time.time()
    stack = deque([Bruteforce_Path(WORLDS2[START].increment, [START], WORLDS2[START].grants["_GLOBAL"] if "_GLOBAL" in WORLDS2[START].grants else {})])
    timeout = CONFIG["bruteforce"]["midpoint_timeout"]
    printing = False
    calc = 0
    shuffled = 0
    midpoint = CONFIG["bruteforce"]["midpoint_every"]
    while len(stack) > 0:
        if calc % midpoint == 0:
            if CONFIG["general"]["verbose"]: print("%s entries in stack, %s calculations done" % (str(len(stack)), str(calc)))
            if time.time() - last_found > timeout:
                # 26: Number of Nexus Worlds in 2kki
                strategy = "Shifting" if shuffled < 26 else random.choice(["Shuffling", "Sorting", "Rotating", "Rotating", "Rotating", "Shifting", "Shifting", "Shifting", "Shifting", "Shifting", "Reversing"])
                if CONFIG["general"]["verbose"]: print("%s (%s entries in stack, %s calculations done)" % (strategy, str(len(stack)), str(calc)))
                if strategy == "Shifting":
                    stack.rotate(-1)
                elif strategy == "Rotating":
                    stack.rotate(random.randint(1, len(stack) - 1))
                elif strategy == "Shuffling":
                    random.shuffle(stack)
                elif strategy == "Reversing":
                    stack.reverse()
                elif strategy == "Deduplicating":
                    newstack = deque()
                    for s in stack:
                        if s not in newstack: newstack.append(s)
                    stack = newstack
                elif strategy == "Sorting":
                    stack = deque(sorted(stack, key=lambda entry: entry.point + WORLDS2[entry.path[-1]].finalbonus))
                last_found = time.time()
                timeout += CONFIG["bruteforce"]["timeout_increment"]
                shuffled += 1
                printing = True
        # if time.time() - last_found > len(WORLDS):
        #    print("Bruteforce Timed out, switching to Z3:")
        #    return len(found)
        pop = stack.pop() if GOAL > BFS_UNTIL else stack.popleft()
        cw = WORLDS2[pop.path[-1]]
        calc += 1
        for d in cw.dests:
            if d in pop.path: continue
            ret = pop.traverse(cw.dests[d], d)
            if ret == None: continue
            if ret.point + WORLDS2[d].finalbonus >= GOAL:
                GOAL = ret.point + WORLDS2[d].finalbonus + 1
                print("Path of length %s found" % str(ret.point + WORLDS2[d].finalbonus))
                last_found = time.time()
                found = ret.path
                if GOAL <= BFS_UNTIL:
                    newstack = deque()
                    for s in stack:
                        if s not in newstack: newstack.append(s)
                    stack = newstack
                elif time.time() - last_found > 1:
                    printing = True
                if printing == True:
                    print("    Flags: " + ", ".join(ret.flags))
                    for i, x in enumerate(found):
                        print("    %s: %s" % (str(i+1), x))
                    for i, x in enumerate(WORLDS2[d].finalworlds):
                        print("    %s: %s" % (str(i+len(ret.path)+1), x))
            stack.append(ret)
    print("Final Length: " + str(GOAL - 1) + ", Terminating")
    DONE = True
    return len(found)
GOAL = bruteforce_search() + 1
if DONE == False: z3_search()
print("\n")