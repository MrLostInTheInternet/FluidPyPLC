from FluidPyPLC.get_sequence import *
from FluidPyPLC.data import Data
from FluidPyPLC.plc import Plc
from FluidPyPLC.diagrams import diagrams
from FluidPyPLC.LadderLogic.ld import LD

import json
import os
import pkg_resources
import PySimpleGUI as sg

#sg.theme('DarkTanBlue')
sg.set_options(font=('Helvetica', 14))


config_file_path = pkg_resources.resource_filename('FluidPyPLC', 'resources/config.json')
with open(config_file_path) as f:
    config = json.load(f)
    path = config["folder_path"]

def collapse(layout, key, visible):
    return sg.pin(sg.Column(layout, key=key, visible=visible))

def elaborate_data(s):
    d = Data(s)
    groups = d.groups
    relay_memory_labels = Plc(s).relay_memory_labels
    lswitch = d.lswitch
    lswitch_bool = d.lswitch_bool
    num_blocks = len(groups) - 1
    data = [['']*6 for _ in range(len(lswitch))]
    data[0].insert(0, num_blocks)
    for i in range(len(groups)):
        data[i].insert(1, groups[i])
    number_of_memories = len(relay_memory_labels)
    data[0].insert(2, number_of_memories)
    for i in range(number_of_memories):
        data[i].insert(3, relay_memory_labels[i])
    for i in range(len(lswitch)):
        if lswitch_bool[i] == 'TRUE':
            data[i].insert(4, lswitch[i])
        else:
            data[i].insert(5, lswitch[i])
    return data


class Gui():
    def __init__(self):
        self.sequence = []
        self.data = []
    
    def gui_mode(self):
        section = [[sg.Multiline(expand_x = True, horizontal_scroll=True, size = (54, 29), key = 'plc_code', background_color='Light Gray', text_color='Black')]]

        headings = ('N° of Blocks','Groups', 'N° of Memories','Relay Memories Labels', 'Limit Switch Enabled', 'Limit Switch Disabled')

        image_viewer_column = [
            [sg.Table(values = (self.data) , headings = headings, size = (1, 8), visible = False, key = 'table', display_row_numbers=False, auto_size_columns=True, justification='center')],
            [sg.Image(key="-IMAGE-", visible = False, expand_x = True)]
        ]

        layout_data = [[sg.Text('Sequence:', size = (11, 2)), sg.Text(key = 'text', expand_x = True, size = (35, 2), text_color = 'White')],
                    [sg.Text('Insert stroke: ', size = (13, 1)), sg.Input(key = 'input', size = (3, 1), text_color='Black', background_color='White', pad=(10,1)), sg.Text('E.g. A+, b-, etc..',expand_x = True, text_color = 'White', justification='right')],
                    [sg.Button('Finish', size =(10, 1), button_color='Green', mouseover_colors=('Black', 'White'), pad=(3, 20)), sg.Button('Clear', size = (10, 1)), sg.Button('Delete', size = (10, 1)), sg.Button("Display Phases' Diagram", expand_x = True, mouseover_colors=('Black', 'White'), expand_y = False, button_color = ('Black','Gray'))],
                    [sg.Checkbox('Show PLC ST code', enable_events=True, key = 'show_plc'), sg.Checkbox('Show Data', enable_events=True, key = 'data', expand_x=True), sg.Button("Create Ladder Logic", size=(20, 1), mouseover_colors=('Black', 'White'), expand_y = False, button_color = ('Black','Gray'))],
                    [sg.Output(expand_x=True, size=(0, 6), pad=(10,2), key='log', background_color="Light Gray", text_color="Black")],
                    [collapse(section, 'plc', False)],
                ]

        layout = [
            [
                sg.Column(layout_data, vertical_alignment= 'top'),
                sg.VSeperator(),
                sg.Column(image_viewer_column, visible = False, key = 'image_column'),
            ]
        ]

        window = sg.Window('GUI', layout, finalize = True)
        window['input'].bind("<Return>", "_Enter")

        sequence = ''
        Text = ''
        toggle_bool1 = False
        toggle_bool2 = False
        toggle_bool3 = False
        check = False
        get_version = pkg_resources.get_distribution('FluidPyPLC')
        version = get_version.version

        print(f'>> Welcome to FluidPyPLC v{version}\n\n')
        while True:
            event, values = window.read()
            if event is None:
                break
            if event in (sg.WINDOW_CLOSED, 'Exit'):
                break
            if event == 'input' + '_Enter':
                stroke = values['input']
                if stroke == '/':
                    print('[!] Click finish to terminate the sequence.')
                    window['input'].update('')
                    continue
                check_stroke = stroke_handler(stroke)
                
                if check_stroke:
                    check_sequence = sequence_handler(stroke, self.sequence)
                
                if check_stroke and check_sequence:
                    sequence_append(stroke, self.sequence)
                    sequence += stroke.upper() + '/'
                    window['text'].update(sequence)
                    window['input'].update('')
                else:
                    
                    window['input'].update('')
            
            if event == 'Finish':
                if len(self.sequence) == 0:
                    print('[!] No sequence submitted.')
                else:
                    check = close_sequence_handler(self.sequence)
                    if check is False:
                        print("[!] The sequence isn't completed.")
                        continue
                    else:
                        self.data = elaborate_data(self.sequence)
                        diagrams(self.sequence)
                        Plc(self.sequence)
                        dir1 = os.path.join(path, 'plc/plc.st')
                        with open(dir1, 'r') as p:
                            Text = p.readlines()
                            Text = ''.join(line for line in Text)
                        window['table'].update(self.data, visible = False)
                        window['plc_code'].update(Text)
                        print("\n[+] Phases' diagram generated <-and-> PLC ST code generated")
                                
            if event == 'Clear':
                self.sequence = []
                sequence = ''
                window['text'].update('')
                toggle_bool2 = False
                window['-IMAGE-'].update(visible = False)
                window['plc_code'].update('')
                window['table'].update('')
                window['log'].update('')
                print(">>> Data cleared")
            
            if event == 'Delete':
                try:
                    sequence = sequence[:-3]
                    window['text'].update(sequence)
                    if len(self.sequence) == 1:
                        print(f'[ ] {self.sequence[0]} has been deleted.')
                        self.sequence.pop()
                        continue
                    print(f'[ ] {self.sequence[-1]} has been deleted.')
                    self.sequence.pop()
                except:
                    print("[!] There is no sequence to delete")

            if event == "Display Phases' Diagram" and check:
                toggle_bool2 = not toggle_bool2
                im = os.path.join(path, 'Plots/phases_diagram.png')
                window['-IMAGE-'].update(im, visible = toggle_bool2)
                window['image_column'].update(visible = toggle_bool2 or toggle_bool3)
            elif event == "Display Phases' Diagram" and not check:
                print("[!] No available sequence to be displayed. Please insert the sequence first.")

            if event == 'show_plc':
                toggle_bool1 = not toggle_bool1
                window['plc'].update(visible=toggle_bool1)
                window['plc_code'].update(Text)

            if event == 'data':
                toggle_bool3 = not toggle_bool3
                window['table'].update(self.data, visible = toggle_bool3)
                window['image_column'].update(visible = toggle_bool3 or toggle_bool2)

            if event == 'Create Ladder Logic':
                if self.sequence:
                    output = LD().output
                    print(f"[+] Created {output}.xml in the {path} folder. Click Import LD to import it in CODESYS.")
                else:
                    print('[!] There is no sequence submitted. Please insert the sequence first.')
        window.close()
