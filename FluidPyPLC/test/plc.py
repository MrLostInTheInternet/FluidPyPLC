import math
import json
import os
import pkg_resources

from FluidPyPLC.data import Data
from FluidPyPLC.set_switches import rotate

config_file_path = pkg_resources.resource_filename('FluidPyPLC', 'resources/config.json')
with open(config_file_path) as f:
    config = json.load(f)
    path = config["folder_path"]

class Plc():
    def __init__(self, s):
        self.run(s)
    def run(self, s):
        d = Data(s)
        solenoids = []
        g = len(d.groups)
        l = len(d.sequence)
        # change labels to e.g. Apositive, Bnegative, etc ..
        plc_groups = [[] for _ in range(g)]
        solenoids = [stroke.replace('+', 'positive') for stroke in d.sequence]
        solenoids = [stroke.replace('-', 'negative') for stroke in solenoids]
        for i in range(g):
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

        # shift by one to the left the list of switches
        limit_switches = rotate(d.lswitch, 1)
        '''
        Create correct labels for the correct activation of CODESYS' code for FluidSim through OPC DA Server
        The labels will be AB0, AB1, etc.. for FLUIDSIM PLC IN, and they will be associated with the Solenoids,
        EB0, EB1, etc.. for FLUIDSIM PLC OUT, and they will be associated with the START and the limit switches
        '''
        plc_range_8bit = 0
        plc_index_8bit = 1
        plc_seen_IO_description = []
        plc_seen_IO = []
        for i in range(l):
            if solenoids[i] not in plc_seen_IO_description and plc_index_8bit < 8:
                plc_seen_IO_description.append(solenoids[i])
                for j in range(len(d.groups)):
                    for z in range(len(plc_groups[j])):
                        if solenoids[i] == plc_groups[j][z]:
                            plc_groups[j][z] = "AB" + str(plc_range_8bit) + "." + str(plc_index_8bit)
                solenoids[i] = "AB" + str(plc_range_8bit) + "." + str(plc_index_8bit)
                plc_seen_IO.append(solenoids[i])
                plc_index_8bit += 1
            elif solenoids[i] in plc_seen_IO_description:
                solenoids[i] = plc_seen_IO[plc_seen_IO_description.index(solenoids[i])]
            elif plc_index_8bit >= 8 and solenoids[i] not in plc_seen_IO_description:
                plc_seen_IO_description.append(solenoids[i])
                plc_index_8bit = 1
                plc_range_8bit += 1
                for j in range(len(d.groups)):
                    for z in range(len(plc_groups[j])):
                        if solenoids[i] in plc_groups[j][z]:
                            plc_groups[j][z] = "AB" + str(plc_range_8bit) + "." + str(plc_index_8bit)
                solenoids[i] = "AB" + str(plc_range_8bit) + "." + str(plc_index_8bit)
                plc_seen_IO.append(solenoids[i])
                plc_index_8bit += 1
        plc_range_8bit = 0
        plc_index_8bit = 1
        plc_seen_IO_description = []
        plc_seen_IO = []
        for i in range(l):
            if limit_switches[i] not in plc_seen_IO_description and plc_index_8bit < 8:
                plc_seen_IO_description.append(limit_switches[i])
                for j in range(len(relay_memory_switches)):
                    for z in range(len(relay_memory_switches[j])):
                        if limit_switches[i] == relay_memory_switches[j][z]:
                            relay_memory_switches[j][z] = "EB" + str(plc_range_8bit) + "." + str(plc_index_8bit)
                limit_switches[i] = "EB" + str(plc_range_8bit) + "." + str(plc_index_8bit)
                plc_seen_IO.append(limit_switches[i])
                plc_index_8bit += 1
            elif limit_switches[i] in plc_seen_IO_description:
                limit_switches[i] = plc_seen_IO[plc_seen_IO_description.index(limit_switches[i])]
            elif plc_index_8bit >= 8 and limit_switches[i] not in plc_seen_IO_description:
                plc_seen_IO_description.append(limit_switches[i])
                plc_index_8bit = 1
                plc_range_8bit += 1
                for j in range(len(relay_memory_switches)):
                    for z in range(len(relay_memory_switches[j])):
                        if limit_switches[i] == relay_memory_switches[j][z]:
                            relay_memory_switches[j][z] = "EB" + str(plc_range_8bit) + "." + str(plc_index_8bit)
                limit_switches[i] = "EB" + str(plc_range_8bit) + "." + str(plc_index_8bit)
                plc_seen_IO.append(limit_switches[i])
                plc_index_8bit += 1
        plc_seen_IO_description = []
        plc_seen_IO = []
        n_of_plcs_8bit = 1 + math.floor(len(set(d.sequence)) / 7)
        d.lswitch = rotate(d.lswitch, 1)
        # open the plc.txt file and write the code, in ST language, on it
        dir = os.path.join(path, 'plc/plc.st')
        with open(dir,'w') as f:
            #relays variables ----------------------------------------------------
            f.write('PROGRAM PLC_PRG\n')
            f.write('VAR\n')
            for i in range(number_of_memories):
                f.write(f'\t{relay_memory_label[i]} : BOOL;\n')
            for i in range(n_of_plcs_8bit):
                f.write('\tAB' + str(i) + " : BYTE;\n")
                f.write('\tEB' + str(i) + " : BYTE;\n")
            f.write('END_VAR\n\n')

            f.write('//Inputs and Outputs connections\n\n//AB* are FLUIDSIM PLC IN, EB* are FLUIDSIM PLC OUT\n')
            for i in range(l):
                if d.sequence[i] not in plc_seen_IO:
                    f.write(f'//{d.sequence[i]} -> {solenoids[i]}\t\t')
                    f.write(f'{d.lswitch[i]} -> {limit_switches[i]}\n')
                    plc_seen_IO.append(d.sequence[i])

            #---------------FIRST GROUP-----------------------
            #------------------START--------------------------
            f.write('\nIF EB0.0 THEN\n\n')
            # IF statement *
            f.write(f'IF EB0.0 AND {limit_switches[-1]} AND NOT {relay_memory_label[0]} ')
            for i in range(1, number_of_memories):
                f.write(f'AND NOT {relay_memory_label[i]} ')
            f.write('THEN\n\t')
            f.write(f'{solenoids[0]} := TRUE;\n')
            f.write('END_IF;\n\n')
            f.write(f'IF EB0.0 AND NOT {relay_memory_label[0]} ')
            for i in range(1, number_of_memories):
                f.write(f'AND NOT {relay_memory_label[i]} ')
            f.write('THEN\n\t')
            #if group 0 ins't just one stroke then
            if len(plc_groups[0]) > 1:
                finish_group = 1 # start from 1, and =+ 1 until the group is finished
                stroke_index = 1 # index of the stroke in the sequence

                # while loop, until finish_group does not reach the group length, the loop continues
                while finish_group < len(plc_groups[0]):
                    # if limit switch is triggered by the first stroke
                    f.write(f'IF {limit_switches[stroke_index - 1]} = TRUE THEN\n\t\t')
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
                f.write('END_IF;\n\n')
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
            f.write(f'IF {relay_memory_label[0]} THEN\n')
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
            stroke_index_return = stroke_index
            for j in range(number_of_memories):
                finish_group = 0

                f.write(f'IF {limit_switches[stroke_index - 1]} AND {relay_memory_label[j]} THEN\n')
                f.write(f'\t{solenoids[stroke_index]} := TRUE;\n')
                while finish_group < len(plc_groups[j + 1]):
                    stroke_index += 1
                    finish_group += 1
                f.write('END_IF;\n\n')
            
            stroke_index = stroke_index_return
            for j in range(number_of_memories):
                finish_group = 0
                f.write(f'IF {relay_memory_label[j]} THEN\n\t')
                while finish_group < len(plc_groups[j + 1]):
                    # while the group isn't finished continue to write the triggered limit switches and solenoids
                    if finish_group != (len(plc_groups[j+1]) - 1):
                        f.write(f'IF {limit_switches[stroke_index]} THEN\n\t')
                        stroke_index += 1
                        f.write(f'\t{solenoids[stroke_index]} := TRUE;\n\t')
                        f.write('END_IF;\n\t')
                    else:
                        stroke_index += 1
                    # we move by one index at the time until the group does not finish
                    finish_group += 1
                
                f.write(f'IF {relay_memory_switches[j][1]} THEN\n\t\t')
                if number_of_memories > 1 and j < number_of_memories - 1:
                    f.write(f'{relay_memory_label[j + 1]} := TRUE;\n\t\t')
                f.write(f'{relay_memory_label[j]} := FALSE;\n\t')
                f.write('END_IF;\n')

                f.write(f'\tIF NOT {relay_memory_label[j]} THEN\n')
                for k in range(len(plc_groups[j + 1])):
                    f.write(f'\t\t{plc_groups[j + 1][k]} := FALSE;\n')
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
                        if finish_group > 0:
                            f.write('\tEND_IF;\n')
                        if finish_group != (len(plc_groups[-1]) - 1):
                            f.write(f'\tIF {limit_switches[stroke_index]} THEN\n\t')
                        stroke_index += 1
                        finish_group += 1
                            
                    f.write('END_IF;\n')
                else:
                    for i in range(1, number_of_memories):
                        f.write(f'AND NOT {relay_memory_label[i]} ')
                    f.write('THEN\n')
                    f.write(f'\t{solenoids[stroke_index]} := TRUE;\n')
                    f.write('END_IF;\n')
            f.write('END_IF;\n')
            f.close()
        self.relay_memory_labels = relay_memory_label
        self.relay_memory_switches = relay_memory_switches
