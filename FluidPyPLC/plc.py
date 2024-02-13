import math
import json
import os
import pkg_resources

from FluidPyPLC.data import Data
from FluidPyPLC.set_switches import rotate


class Plc():
    def __init__(self, s):
        self.path = self.get_config_path()
        self.data = Data(s)
        self.sequence = s
        self.solenoids = self.sequence[:]
        self.limit_switches_groups = self.data.lswitch_groups
        self.limit_switches_sequence = rotate(self.data.lswitch, 1)
        self.is_loop_present = self.data.loop
        self.is_merge_possible = self.data.merge

        self.length_sequence = len(self.sequence)
        self.length_groups = len(self.data.groups) - 1 if self.is_merge_possible else len(self.data.groups)
        self.looped_pistons = []

        self.number_of_relay_memories = self.length_groups - 1
        self.relay_memory_switches = [[] for _ in range(self.number_of_relay_memories)]
        self.relay_memory_labels = []

        self._plc_io_byte = 0
        self._index_plc_byte = 1
        self._plc_seen_io_connection = []
        self._plc_seen_io = []
        self.plc_groups = self.data.groups
        self.number_of_plcs = 1 + math.floor(len(set(self.solenoids)) / 7)
        self.run()

    def get_config_path(self):
        try:
            config_file_path = pkg_resources.resource_filename('FluidPyPLC', 'resources/config.json')
            with open(config_file_path) as f:
                config = json.load(f)
                return config["folder_path"]
        except Exception as e:
            print(f"Error loading configuration: {e}\n")

    def run(self):
        self._process_looped_pistons()
        self._generate_relay_memories()
        self._process_io_plc(self.solenoids, self.plc_groups, 'A')
        self._process_io_plc(self.limit_switches_sequence, self.relay_memory_switches, 'E')
        self._rotate_limit_switches_array(self.limit_switches_sequence)
        self._write_plc_code()

    def _rotate_limit_switches_array(self, array):
        array = rotate(array, 1)

    def _process_looped_pistons(self):
        if self.is_loop_present:
            for stroke in self.solenoids:
                if self.solenoids.count(stroke) > 1 and stroke[0] not in self.looped_pistons:
                    self.looped_pistons.append(stroke[0])

    def _generate_relay_memories(self):
        index_limit_switch = 1
        for i in range(self.number_of_relay_memories):
            self.relay_memory_switches[i].append(self.limit_switches_groups[index_limit_switch][0])
            if i == (self.number_of_relay_memories - 1):
                if self.is_merge_possible:
                    self.relay_memory_switches[i].append(self.limit_switches_groups[index_limit_switch + 1][0])
                else:
                    self.relay_memory_switches[i].append(self.limit_switches_groups[0][0])
            else:
                self.relay_memory_switches[i].append(self.limit_switches_groups[index_limit_switch + 1][0])
            index_limit_switch += 1
            self.relay_memory_labels.append('K' + str(i))

    def _process_io_plc(self, items, bi_dimensional_array, letter):
        tmp_byte = self._plc_io_byte
        tmp_index = self._index_plc_byte
        tmp_seen_connection = {}
        tmp_seen_io = []

        for i in range(self.length_sequence):
            item = items[i]

            for j in range(len(bi_dimensional_array)):
                for z in range(len(bi_dimensional_array[j])):
                    if item == bi_dimensional_array[j][z]:
                        bi_dimensional_array[j][z] = f'{letter}B{tmp_byte}.{tmp_index}'

            if item not in tmp_seen_connection and tmp_index < 8:
                tmp_seen_connection[item] = f'{letter}B{tmp_byte}.{tmp_index}'
                tmp_index += 1
            elif item in tmp_seen_connection:
                items[i] = tmp_seen_connection[item]
            else:
                tmp_byte += 1
                tmp_index = 1
                tmp_seen_connection[item] = f'{letter}B{tmp_byte}.{tmp_index}'
                tmp_index += 1

            items[i] = tmp_seen_connection[item]
            tmp_seen_io.append(item)


    def _write_plc_code(self):
        dir = os.path.join(self.path, 'plc/plc.st')
        with open(dir, 'w') as f:
            self._write_variable_declaration(f)
            self._write_input_output_connections(f)
            self._write_group_logic(f)
            f.close()

    def _write_variable_declaration(self, file):
        file.write('PROGRAM PLC_PRG\n\n')
        file.write('VAR\n')
        for i in range(self.number_of_relay_memories):
            file.write(f'\t{self.relay_memory_labels[i]} : BOOL;\n')
        file.write('END_VAR\n\n')
        file.write('VAR_GLOBAL\n')
        for i in range(self.number_of_plcs):
            file.write('\tAB' + str(i) + " : BYTE;\n")
            file.write('\tEB' + str(i) + " : BYTE;\n")
        file.write('END_VAR\n\n')
        

    def _write_input_output_connections(self, file):
        limit_switch_rotated = rotate(self.data.lswitch, 1)
        file.write('//Inputs and Outputs connections\n\n')
        file.write('//AB* are FLUIDSIM PLC IN, EB* are FLUIDSIM PLC OUT\n')
        for i in range(self.length_sequence):
            if self.sequence[i] not in self._plc_seen_io:
                file.write(f'//{self.sequence[i]} -> {self.solenoids[i]}\t\t')
                file.write(f'{limit_switch_rotated[i]} -> {self.limit_switches_sequence[i]}\n')
                self._plc_seen_io.append(self.sequence[i])

    def _write_group_logic(self, file):

            #---------------FIRST GROUP-----------------------
            #------------------START--------------------------
            file.write('\nIF EB0.0 THEN\n\n')
            # IF statement *
            file.write(f'IF EB0.0 AND {self.limit_switches_sequence[-1]} AND NOT {self.relay_memory_labels[0]} ')
            for i in range(1, self.number_of_relay_memories):
                file.write(f'AND NOT {self.relay_memory_labels[i]} ')
            file.write('THEN\n\t')
            file.write(f'{self.solenoids[0]} := TRUE;\n')
            file.write('END_IF;\n\n')
            file.write(f'IF EB0.0 AND NOT {self.relay_memory_labels[0]} ')
            for i in range(1, self.number_of_relay_memories):
                file.write(f'AND NOT {self.relay_memory_labels[i]} ')
            file.write('THEN\n\t')
            #if group 0 ins't just one stroke then
            if len(self.plc_groups[0]) > 1:
                finish_group = 1 # start from 1, and =+ 1 until the group is finished
                stroke_index = 1 # index of the stroke in the sequence

                # while loop, until finish_group does not reach the group length, the loop continues
                while finish_group < len(self.plc_groups[0]):
                    # if limit switch is triggered by the first stroke
                    file.write(f'IF {self.limit_switches_sequence[stroke_index - 1]} = TRUE THEN\n\t\t')
                    # then the next solenoid is triggered
                    file.write(f'{self.solenoids[stroke_index]} := TRUE;\n\t')
                    file.write('END_IF;\n\t')
                    # add 1 to the indexes so the next strokes and limit switches will be triggered
                    stroke_index += 1
                    finish_group += 1
                # when the first group is finishes, then the limit switch that activates the first memory is triggered
                file.write(f'IF {self.relay_memory_switches[0][0]} THEN\n\t\t')
                file.write(f'{self.relay_memory_labels[0]} := TRUE;\n\t')
                file.write('END_IF;\n')
                # then we need to close the IF statement *
                file.write('END_IF;\n\n')
            else:
                # if the first group is composed by just one stroke then we pass to the next group by activating the first memory
                stroke_index = 1
                file.write(f'IF {self.relay_memory_switches[0][0]} THEN\n\t\t')
                file.write(f'{self.relay_memory_labels[0]} := TRUE;\n\t')
                file.write('END_IF;\n')
                # we close the IF statement *
                file.write('END_IF;\n\n')
            # first group is Done!

            # first memory relay activation
            file.write(f'IF {self.relay_memory_labels[0]} THEN\n')
            if self.is_merge_possible:
                # if the last group can be merged with the first one, then we include those strokes
                merged_groups = []
                merged_groups = self.plc_groups[0] + self.plc_groups[-1]
                for k in range(len(self.plc_groups[0]) + len(self.plc_groups[-1])):
                    file.write(f'\t{merged_groups[k]} := FALSE;\n')
                file.write('END_IF;\n\n')
            else:
                # if not, write only the group strokes
                for k in range(len(self.plc_groups[0])):
                    file.write(f'\t{self.plc_groups[0][k]} := FALSE;\n')
                file.write('END_IF;\n\n')

            #------------NEXT GROUPS-------------------------
            stroke_index_return = stroke_index
            for j in range(self.number_of_relay_memories):
                finish_group = 0

                file.write(f'IF {self.limit_switches_sequence[stroke_index - 1]} AND {self.relay_memory_labels[j]} THEN\n')
                file.write(f'\t{self.solenoids[stroke_index]} := TRUE;\n')
                while finish_group < len(self.plc_groups[j + 1]):
                    stroke_index += 1
                    finish_group += 1
                file.write('END_IF;\n\n')
            
            stroke_index = stroke_index_return
            for j in range(self.number_of_relay_memories):
                finish_group = 0
                file.write(f'IF {self.relay_memory_labels[j]} THEN\n\t')
                while finish_group < len(self.plc_groups[j + 1]):
                    # while the group isn't finished continue to write the triggered limit switches and solenoids
                    if finish_group != (len(self.plc_groups[j+1]) - 1):
                        file.write(f'IF {self.limit_switches_sequence[stroke_index]} THEN\n\t')
                        stroke_index += 1
                        file.write(f'\t{self.solenoids[stroke_index]} := TRUE;\n\t')
                        file.write('END_IF;\n\t')
                    else:
                        stroke_index += 1
                    # we move by one index at the time until the group does not finish
                    finish_group += 1
                
                file.write(f'IF {self.relay_memory_switches[j][1]} THEN\n\t\t')
                if self.number_of_relay_memories > 1 and j < self.number_of_relay_memories - 1:
                    file.write(f'{self.relay_memory_labels[j + 1]} := TRUE;\n\t\t')
                file.write(f'{self.relay_memory_labels[j]} := FALSE;\n\t')
                file.write('END_IF;\n')

                file.write(f'\tIF NOT {self.relay_memory_labels[j]} THEN\n')
                for k in range(len(self.plc_groups[j + 1])):
                    file.write(f'\t\t{self.plc_groups[j + 1][k]} := FALSE;\n')
                file.write('\tEND_IF;\n')
                file.write('END_IF;\n\n')
                #------------------------------------
            if self.is_merge_possible:
                file.write(f'IF {self.limit_switches_sequence[stroke_index - 1]} AND NOT {self.relay_memory_labels[0]} ')
                if len(self.plc_groups[-1]) > 1:
                    for i in range(1, self.number_of_relay_memories):
                        file.write(f'AND NOT {self.relay_memory_labels[i]} ')
                    file.write('THEN\n')
                    finish_group = 0
                    while finish_group < len(self.plc_groups[-1]):
                        file.write(f'\t{self.solenoids[stroke_index]} := TRUE;\n')
                        if finish_group > 0:
                            file.write('\tEND_IF;\n')
                        if finish_group != (len(self.plc_groups[-1]) - 1):
                            file.write(f'\tIF {self.limit_switches_sequence[stroke_index]} THEN\n\t')
                        stroke_index += 1
                        finish_group += 1
                            
                    file.write('END_IF;\n')
                else:
                    for i in range(1, self.number_of_relay_memories):
                        file.write(f'AND NOT {self.relay_memory_labels[i]} ')
                    file.write('THEN\n')
                    file.write(f'\t{self.solenoids[stroke_index]} := TRUE;\n')
                    file.write('END_IF;\n')
            file.write('END_IF;\n')
