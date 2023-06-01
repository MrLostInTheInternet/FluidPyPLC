from data import Data
from set_switches import rotate

class Plc():
    def __init__(self, s):
        self.run(s)
    def run(self, s):
        d = Data(s)
        solenoids = d.sequence
        plc_groups = [[] for _ in range(len(d.groups))]
        g = len(d.groups)
        l = len(d.sequence)
        # change labels to e.g. Apositive, Bnegative, etc ..
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
        dir = "./plc/plc.txt"
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
            f.write('\tSTART : BOOL;\n')
            f.write('END_VAR\n\n')
            for i in range(number_of_memories):
                f.write(f'{relay_memory_label[i]} := FALSE;\n')
            for i in range(l):
                f.write(f'{solenoids[i]} := FALSE;\n')
            limit_switch_list_bool = d.lswitch_bool
            for i in range(l):
                f.write(f'{d.lswitch[i]} := {limit_switch_list_bool[i]};\n')

            # shift by one to the left the list of switches
            limit_switches = rotate(d.lswitch, 1)
            #---------------FIRST GROUP-----------------------
            #------------------START--------------------------
            f.write('\nWHILE START = True DO\n')
            f.write(f'IF START = True AND {limit_switches[-1]} = True AND {relay_memory_label[0]} = False ')
            for i in range(1, number_of_memories):
                f.write(f'AND {relay_memory_label[i]} = False ')
            f.write('THEN\n\t')
            f.write(f'{solenoids[0]} := TRUE;\n\t')
            f.write(f'IF {solenoids[0]} = True THEN\n\t\t')
            #if group 0 ins't just one stroke then
            if len(d.groups[0]) > 1:
                convert_on_off = limit_switches[0][0]
                for on_off in range(1,len(limit_switches)):
                    if convert_on_off == limit_switches[on_off][0]:
                        f.write(f'{limit_switches[on_off]} := FALSE;\n\t')
                        break
                f.write(f'\t{limit_switches[0]} := TRUE;\n\t')
                f.write('END_IF;\n\t')
                finish_group = 1
                _index_ = 1
                while finish_group < len(d.groups[0]):
                    f.write(f'IF {limit_switches[_index_ - 1]} = True THEN\n\t\t')
                    f.write(f'{solenoids[_index_]} := TRUE;\n\t')
                    f.write('END_IF;\n\t')
                    f.write(f'IF {solenoids[_index_]} = True THEN\n\t\t')
                    convert_on_off = limit_switches[_index_][0]
                    for on_off in range(_index_ + 1,len(limit_switches)):
                        if convert_on_off == limit_switches[on_off][0]:
                            f.write(f'{limit_switches[on_off]} := FALSE;\n\t')
                            break
                    f.write(f'\t{limit_switches[_index_]} := TRUE;\n\t')
                    f.write('END_IF;\n\t')
                    _index_ += 1
                    finish_group += 1
                f.write('\nEND_IF;\n')
            else:
                _index_ = 0
                convert_on_off = limit_switches[_index_][0]
                for on_off in range(1,len(limit_switches)):
                    if convert_on_off == limit_switches[on_off][0]:
                        f.write(f'{limit_switches[on_off]} := FALSE;\n\t')
                        break
                f.write(f'\t{limit_switches[_index_]} := TRUE;\n\t')
                f.write('END_IF;\nEND_IF;\n')
                _index_ += 1
            f.write(f'\nIF {relay_memory_switches[0][0]} = True THEN\n\t')
            f.write(f'{relay_memory_label[0]} := TRUE;\n')
            f.write('END_IF;\n')

            #first relay-------------------------------------
            f.write(f'\nIF {relay_memory_label[0]} = True THEN\n')
            if merge:
                merged_groups = []
                merged_groups = d.groups[0] + d.groups[-1]
                for k in range(len(d.groups[0]) + len(d.groups[-1])):
                    f.write(f'\t{merged_groups[k]} := FALSE;\n')
                f.write('END_IF;\n\n')
            else:
                for k in range(len(d.groups[0])):
                    f.write(f'\t{d.groups[0][k]} := FALSE;\n')
                f.write('END_IF;\n\n')

            #------------NEXT GROUPS-------------------------
            for j in range(number_of_memories):
                finish_group = 0
                if j > 0:
                    #activation switch
                    f.write(f'\nIF {relay_memory_switches[j][0]} = True THEN\n\t')
                    f.write(f'{relay_memory_label[j]} := TRUE;\n')
                    f.write('END_IF;\n\n')

                f.write(f'IF {limit_switches[_index_ - 1]} = True AND {relay_memory_label[j]} = True THEN\n')
                while finish_group < len(d.groups[j + 1]):
                    f.write(f'\t{solenoids[_index_]} := TRUE;\n')
                    if finish_group != 0:
                        f.write('\tEND_IF;\n')
                    f.write(f'\tIF {solenoids[_index_]} = True THEN\n\t')
                    convert_on_off = limit_switches[_index_][0]
                    if convert_on_off.upper() in looped_pistons:
                        found = False
                        for on_off in range(_index_ - 1, -1, -1):
                            if convert_on_off == limit_switches[on_off][0]:
                                f.write(f'\t{limit_switches[on_off]} := FALSE;\n')
                                found = True
                                break
                        if not found:
                            for on_off in range(_index_ + 1,len(limit_switches)):
                                if convert_on_off == limit_switches[on_off][0]:
                                    f.write(f'\t{limit_switches[on_off]} := FALSE;\n')
                                    found = True
                                    break    
                    else:
                        found = False
                        for on_off in range(_index_ + 1,len(limit_switches)):
                            if convert_on_off == limit_switches[on_off][0]:
                                f.write(f'\t{limit_switches[on_off]} := FALSE;\n')
                                found = True
                                break
                        if not found:
                            for on_off in range(_index_ - 1, -1, -1):
                                if convert_on_off == limit_switches[on_off][0]:
                                    f.write(f'\t{limit_switches[on_off]} := FALSE;\n')
                                    break
                    f.write(f'\t\t{limit_switches[_index_]} := TRUE;\n')
                    f.write('\tEND_IF;\n')
                    if finish_group != (len(d.groups[j+1]) - 1):
                        f.write(f'\tIF {limit_switches[_index_]} = True THEN\n\t')
                    _index_ += 1
                    finish_group += 1
                f.write('END_IF;\n')
                if j == 0:
                    f.write(f'\nIF {relay_memory_switches[j][1]} = True THEN\n\t')
                    f.write(f'{relay_memory_label[j]} := FALSE;\n')
                    f.write('END_IF;\n')

                    f.write(f'\nIF {relay_memory_label[0]} = False THEN\n')
                    for k in range(len(d.groups[1])):
                        f.write(f'\t{d.groups[1][k]} := FALSE;\n')
                    f.write('END_IF;\n')
                elif j > 0:
                    #deactivation switch
                    f.write(f'\nIF {relay_memory_switches[j][1]} = True THEN\n\t')
                    f.write(f'{relay_memory_label[j]} := FALSE;\n')
                    f.write('END_IF;\n')

                    f.write(f'\nIF {relay_memory_label[j]} = False THEN\n')
                    for k in range(len(d.groups[1])):
                        f.write(f'\t{d.groups[1][k]} := FALSE;\n')
                    f.write('END_IF;\n\n')
                #------------------------------------
            if merge:
                f.write(f'IF {limit_switches[_index_ - 1]} = True AND {relay_memory_label[0]} = False ')
                if len(d.groups[-1]) > 1:
                    for i in range(1, number_of_memories):
                        f.write(f'AND {relay_memory_label[i]} = False ')
                    f.write('THEN\n')
                    finish_group = 0
                    while finish_group < len(d.groups[-1]):
                        f.write(f'\t{solenoids[_index_]} := TRUE;\n')
                        f.write(f'\tIF {solenoids[_index_]} = True THEN\n\t')
                        convert_on_off = limit_switches[_index_][0]
                        for on_off in range(_index_ + 1,len(limit_switches)):
                            if convert_on_off == limit_switches[on_off][0]:
                                f.write(f'\t{limit_switches[on_off]} := FALSE;\n')
                                break
                        for on_off in range(_index_):
                            if convert_on_off == limit_switches[on_off][0]:
                                f.write(f'\t{limit_switches[on_off]} := FALSE;\n')
                                break
                        f.write(f'\t\t{limit_switches[_index_]} := TRUE;\n')
                        f.write('\tEND_IF;\n')
                        if finish_group != (len(d.groups[-1]) - 1):
                            f.write(f'\tIF {limit_switches[_index_]} = True THEN\n\t')
                        _index_ += 1
                        finish_group += 1
                    f.write('END_IF;\n')
                else:
                    for i in range(1, number_of_memories):
                        f.write(f'AND {relay_memory_label[i]} = False ')
                    f.write('THEN\n')
                    f.write(f'\t{solenoids[_index_]} := TRUE;\n')
                    f.write(f'\tIF {solenoids[_index_]} = True THEN\n\t\t')
                    convert_on_off = limit_switches[_index_][0]
                    for on_off in range(_index_ + 1,len(limit_switches)):
                        if convert_on_off == limit_switches[on_off][0]:
                            f.write(f'{limit_switches[on_off]} := FALSE;\n\t\t')
                            break
                    for on_off in range(_index_):
                        if convert_on_off == limit_switches[on_off][0]:
                            f.write(f'{limit_switches[on_off]} := FALSE;\n\t\t')
                            break
                    f.write(f'{limit_switches[_index_]} := TRUE;\n\t')
                    f.write('END_IF;\nEND_IF;\n')
            f.write('END_WHILE\n')
            f.close()
        self.relay_memory_labels = relay_memory_label
        self.relay_memory_switches = relay_memory_switches
