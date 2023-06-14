from FluidPyPLC.set_groups import Groups
from FluidPyPLC.set_switches import Switches
from copy import deepcopy

# get the number of pistons and their labels
def pistons(s):
    piston_label = []
    tmp = deepcopy(s)
    tmp = [words.replace("-", "") for words in tmp]
    tmp = [words.replace("+", "") for words in tmp]
    n_of_pistons = len(set(tmp))
    for stroke in tmp:
        if stroke not in piston_label:
            piston_label.append(stroke)
    return n_of_pistons, piston_label

# function to merge the last group with the first one if it is compatible
def merge_groups(groups):
    seen = []
    merge = False
    for i in range(len(groups[-1])):
        seen.append(groups[-1][i][0])
    for j in range(len(groups[0])):
        stroke = groups[0][j][0]
        if stroke in seen:
            merge = False
            break
        else:
            merge = True
    return merge

# function to check if there are loops inside the sequence
def check_for_loops(s):
    stroke_signed = []
    loop = False
    for i in range(len(s)):
        stroke = s[i]
        rep = s.count(stroke)
        if stroke not in stroke_signed:
            if rep > 1:
                stroke_signed.append(stroke)
                loop = True
                break
            else:
                loop = False
        else:
            loop = True
            break
    return loop

# function to understand which limit switches are held down from the beginning, e.g. the limit switches normally open, are closed
def lswitch_boolean(limit_switches):
    lswitch_bool = ['TRUE',]
    seen_letter = []
    seen_switch = []
    for i in range(1, len(limit_switches)):
        limit_switch = limit_switches[i]
        if limit_switch[0] not in seen_letter:
            seen_letter.append(limit_switch[0])
            seen_switch.append(limit_switch)
            lswitch_bool.append('FALSE')
        else:
            if limit_switch not in seen_switch:
                lswitch_bool.append('TRUE')
            else:
                lswitch_bool.append('FALSE')
    return lswitch_bool

# stored data
class Data():
    def __init__(self, s):
        self.sequence = s
        self.run()

    def run(self):
        g = Groups(self.sequence)
        sw = Switches(self.sequence, g.groups_2D)
        self.groups = g.groups_2D
        self.lswitch = sw.limit_switches
        self.lswitch_groups = sw.limit_s_groups
        self.loop = check_for_loops(self.sequence)
        self.merge = merge_groups(g.groups_2D)
        self.number_of_pistons = pistons(self.sequence)[0]
        self.pistons_labels = pistons(self.sequence)[1]
        self.lswitch_bool = lswitch_boolean(sw.limit_switches)

