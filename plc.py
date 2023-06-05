from data import Data
from set_switches import rotate

class Plc():
    def __init__(self, s):
        self.run(s)
    def run(self, s):
        d = Data(s)
        solenoids = []
        g = len(d.groups)
        l = len(d.sequence)
        # change labels to e.g. Apositive, Bnegative, etc ..
        plc_groups = [[] for _ in range(len(d.groups))]
        solenoids = [stroke.replace('+', 'Positive') for stroke in d.sequence]
        solenoids = [stroke.replace('-', 'Negative') for stroke in solenoids]
        for i in range(len(d.groups)):
            for j in range(len(d.groups[i])):
                if d.groups[i][j][1] == '+':
                    plc_stroke = str(d.groups[i][j][0]) + 'positive'
                else:
                    plc_stroke = str(d.groups[i][j][0]) + 'negative'
                plc_groups[i].insert(j, plc_stroke)
        # check the loops and possible groups merge
        loop = d.loop
        merge = d.merge
        if merge:
            g -= 1
        else:
            g = g
        looped_pistons = []
        if loop:
            for stroke in solenoids:
                if solenoids.count(stroke) > 1 and stroke[0] not in looped_pistons:
                    looped_pistons.append(stroke[0])
        # based on these variables we use different methods for the PLC ST language
        # define number of relay memories and their labels
        number_of_memories = g - 1
        relay_memory_switches = [[] for _ in range(number_of_memories)]
        # make sure to start from the second group of limit switches -> lswitch_index = 1
        lswitch_index = 1
        # loop to assign the relay memories limit switches, e.g. START -> [a0] -> K, [b1] -> !K
        for i in range(number_of_memories):
            relay_memory_switches[i].append(d.lswitch_groups[lswitch_index][0])
            if i == (number_of_memories- 1):
                if merge == True:
                    relay_memory_switches[i].append(d.lswitch_groups[lswitch_index+1][0])
                elif merge == False:
                    relay_memory_switches[i].append(d.lswitch_groups[0][0])
            else:
                relay_memory_switches[i].append(d.lswitch_groups[lswitch_index+1][0])
            lswitch_index += 1
        # assign labels to the relay memories
        relay_memory_label = []
        for i in range(number_of_memories):
            relay_memory_label.append('K' + str(i))
        
        # open the plc.txt file and write the code, in ST language, on it
        dir = "./plc/plc.st"
        with open(dir,'w') as f:
            #relays variables ----------------------------------------------------
            f.write('PROGRAM PLC_PRG\n')
            f.write('VAR\n')
            for i in range(number_of_memories):
                f.write(f'\t{relay_memory_label[i]} AT %Q* : BOOL;\n')
            #solenoids variables -------------------------------------------------
            seen = []
            for i in range(l):
                if solenoids[i] not in seen:
                    f.write(f'\t{solenoids[i]} AT %Q* : BOOL;\n')
                    seen.append(solenoids[i])
            #limit switches variables --------------------------------------------
            seen = []
            for i in range(l):
                if d.lswitch[i] not in seen:
                    f.write(f'\t{d.lswitch[i]} AT %I* : BOOL;\n')
                    seen.append(d.lswitch[i])
            seen = []
            f.write('\tSTART : BOOL;\n')
            f.write('END_VAR\n\n')

            # shift by one to the left the list of switches
            limit_switches = rotate(d.lswitch, 1)
            #---------------FIRST GROUP-----------------------
            #------------------START--------------------------
            f.write('IF START THEN\n')
            # IF statement *
            f.write(f'IF START AND {limit_switches[-1]} AND NOT {relay_memory_label[0]} ')
            for i in range(1, number_of_memories):
                f.write(f'AND NOT {relay_memory_label[i]} ')
            f.write('THEN\n\t')
            f.write(f'{solenoids[0]} := TRUE;\n\t')
            #if group 0 ins't just one stroke then
            if len(plc_groups[0]) > 1:
                finish_group = 1 # start from 1, and =+ 1 until the group is finished
                stroke_index = 1 # index of the stroke in the sequence

                # while loop, until finish_group does not reach the group length, the loop continues
                while finish_group < len(plc_groups[0]):
                    # if limit switch is triggered by the first stroke
                    f.write(f'IF {limit_switches[stroke_index - 1]} = True THEN\n\t\t')
                    # then the next solenoid is triggered
                    f.write(f'{solenoids[stroke_index]} := TRUE;\n\t')
                    f.write('END_IF;\n\t')
                    # add 1 to the indexes so the next strokes and limit switches will be triggered
                    stroke_index += 1
                    finish_group += 1
                # when the first group is finishes, then the limit switch that activates the first memory is triggered
                f.write(f'IF {relay_memory_switches[0][0]} THEN\n\t\t')
                f.write(f'{relay_memory_label[0]} := TRUE;\n\t')
                f.write('END_IF;\n')
                # then we need to close the IF statement *
                f.write('\nEND_IF;\n\n')
            else:
                # if the first group is composed by just one stroke then we pass to the next group by activating the first memory
                stroke_index = 1
                f.write(f'IF {relay_memory_switches[0][0]} THEN\n\t\t')
                f.write(f'{relay_memory_label[0]} := TRUE;\n\t')
                f.write('END_IF;\n')
                # we close the IF statement *
                f.write('END_IF;\n\n')
            # first group is Done!

            # first memory relay activation
            f.write(f'\nIF {relay_memory_label[0]} THEN\n')
            if merge:
                # if the last group can be merged with the first one, then we include those strokes
                merged_groups = []
                merged_groups = plc_groups[0] + plc_groups[-1]
                for k in range(len(plc_groups[0]) + len(plc_groups[-1])):
                    f.write(f'\t{merged_groups[k]} := FALSE;\n')
                f.write('END_IF;\n\n')
            else:
                # if not, write only the group strokes
                for k in range(len(plc_groups[0])):
                    f.write(f'\t{plc_groups[0][k]} := FALSE;\n')
                f.write('END_IF;\n\n')

            #------------NEXT GROUPS-------------------------
            for j in range(number_of_memories):
                finish_group = 0

                f.write(f'IF {limit_switches[stroke_index - 1]} AND {relay_memory_label[j]} THEN\n')
                while finish_group < len(plc_groups[j + 1]):
                    # while the group isn't finished continue to write the triggered limit switches and solenoids
                    f.write(f'\t{solenoids[stroke_index]} := TRUE;\n\t')
                    if finish_group > 0:
                        f.write('END_IF;\n\t')
                    if finish_group != (len(plc_groups[j+1]) - 1):
                        f.write(f'IF {limit_switches[stroke_index]} THEN\n\t')
                    # we move by one index at the time until the group does not finish
                    stroke_index += 1
                    finish_group += 1
                
                f.write(f'IF {relay_memory_switches[j][1]} THEN\n\t\t')
                if number_of_memories > 1 and j < number_of_memories - 1:
                    f.write(f'{relay_memory_label[j + 1]} := TRUE;\n\t\t')
                f.write(f'{relay_memory_label[j]} := FALSE;\n\t')
                f.write('END_IF;\n')

                f.write(f'\tIF NOT {relay_memory_label[j]} THEN\n')
                for k in range(len(plc_groups[1])):
                    f.write(f'\t\t{plc_groups[1][k]} := FALSE;\n')
                f.write('\tEND_IF;\n')
                f.write('END_IF;\n\n')
                #------------------------------------
            if merge:
                f.write(f'IF {limit_switches[stroke_index - 1]} AND NOT {relay_memory_label[0]} ')
                if len(plc_groups[-1]) > 1:
                    for i in range(1, number_of_memories):
                        f.write(f'AND NOT {relay_memory_label[i]} ')
                    f.write('THEN\n')
                    finish_group = 0
                    while finish_group < len(plc_groups[-1]):
                        f.write(f'\t{solenoids[stroke_index]} := TRUE;\n')
                        if finish_group != (len(plc_groups[-1]) - 1):
                            f.write(f'\tIF {limit_switches[stroke_index]} THEN\n\t')
                        stroke_index += 1
                        finish_group += 1
                    f.write('END_IF;\n')
                else:
                    for i in range(1, number_of_memories):
                        f.write(f'AND {relay_memory_label[i]} = False ')
                    f.write('THEN\n')
                    f.write(f'\t{solenoids[stroke_index]} := TRUE;\n')
                    f.write('END_IF;\n')
            f.write('END_IF;\n')
            f.close()
        self.relay_memory_labels = relay_memory_label
        self.relay_memory_switches = relay_memory_switches
