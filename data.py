from get_sequence import s
from set_groups import groups_2D
from set_switches import limit_switches
from set_switches import limit_s_groups
from copy import deepcopy

# get the number of pistons and their labels
def pistons():
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
def merge_groups():
    seen = []
    merge = False
    for i in range(len(groups_2D[-1])):
        seen.append(groups_2D[-1][i][0])
    for j in range(len(groups_2D[0])):
        stroke = groups_2D[0][j][0]
        if stroke in seen:
            merge = False
            break
        else:
            merge = True
    return merge

# function to check if there are loops inside the sequence
def check_for_loops():
    stroke_signed = []
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
def lswitch_boolean():
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
    def __init__(self):
        self.sequence = s
        self.groups = groups_2D
        self.lswitch = limit_switches
        self.lswitch_groups = limit_s_groups
        self.loop = check_for_loops()
        self.merge = merge_groups()
        self.number_of_pistons = pistons()[0]
        self.pistons_labels = pistons()[1]
        self.lswitch_bool = lswitch_boolean()
