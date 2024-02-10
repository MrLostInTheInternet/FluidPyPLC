from FluidPyPLC.set_groups import Groups
from FluidPyPLC.set_switches import Switches

# get the number of pistons and their labels
def pistons(s):
    cleaned_sequence = [stroke.strip("+-") for stroke in s]
    piston_labels = sorted(set(cleaned_sequence))
    return len(piston_labels), piston_labels

# function to merge the last group with the first one if it is compatible
def merge_groups(groups):
    last_group_strokes = {stroke[0] for stroke in groups[-1]}
    return not any(stroke[0] in last_group_strokes for stroke in groups[0])

# function to check if there are loops inside the sequence
def check_for_loops(s):
    return any(s.count(stroke) > 1 for stroke in set(s))

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
class Data:
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
        self.number_of_pistons, self.pistons_labels = pistons(self.sequence)
        self.lswitch_bool = lswitch_boolean(sw.limit_switches)


