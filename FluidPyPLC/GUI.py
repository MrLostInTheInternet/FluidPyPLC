from FluidPyPLC.get_sequence import *
from FluidPyPLC.data import Data
from FluidPyPLC.plc import Plc
from FluidPyPLC.diagrams import diagrams
from FluidPyPLC.LadderLogic.ld import LD

import json
import os
import pkg_resources
import PySimpleGUI as sg

class Gui():
    def __init__(self):
        self.sequence_manager = Sequence()
        self.data = []
        self.path = self.get_config_path()
        self.version = pkg_resources.get_distribution('FluidPyPLC').version
        sg.set_options(font=('Helvetica', 14))
        self.layout = self.create_layout()
        self.window = sg.Window(f'FluidPyPLC v{self.version}', self.layout, finalize=True)
        self.window['input'].bind("<Return>", "_Enter")
        self.toggle_bool1 = False
        self.toggle_bool2 = False
        self.toggle_bool3 = False
        self.text = ''
    
    def run(self):
        print(f'>> Welcome to FluidPyPLC v{self.version}\n\n')
        while True:
            event, values = self.window.read()
            if event in (None, sg.WINDOW_CLOSED, 'Exit'):
                break

            self.handle_events(event, values)

        self.window.close()

    def get_config_path(self):
        config_file_path = pkg_resources.resource_filename('FluidPyPLC', 'resources/config.json')
        with open(config_file_path) as f:
            config = json.load(f)
            return config["folder_path"]

    def process_input(self, input_value):
        stroke = input_value.upper()
        if stroke == '/':
            print("[!] Click Finish to submit the sequence.")
            self.window['input'].update('')
            self.window['input'].set_focus()
            return

        # Validate the stroke format first
        if not self.sequence_manager.stroke_handler(stroke):
            return

        # If the stroke is valid and doesn't cause a sequence error, append it
        if self.sequence_manager.sequence_handler(stroke):
            self.sequence_manager.sequence_append(stroke)
            sequence_display = '/'.join(self.sequence_manager.sequence) + '/'
            self.window['text'].update(sequence_display)
            self.window['input'].update('')
            self.window['input'].set_focus()

    def elaborate_data(self):
        d = Data(self.sequence_manager.sequence)
        groups = d.groups
        relay_memory_labels = Plc(self.sequence_manager.sequence).relay_memory_labels
        lswitch = d.lswitch
        lswitch_bool = d.lswitch_bool

        # Determine the number of blocks and memories
        num_blocks = len(groups) - 1
        number_of_memories = len(relay_memory_labels)

        # Initialize data array with empty lists
        data = [[''] * 6 for _ in range(max(len(lswitch), number_of_memories))]

        # Populate the data array
        for i, group in enumerate(groups):
            data[i][1] = group

        for i, label in enumerate(relay_memory_labels):
            data[i][3] = label

        for i, (switch, state) in enumerate(zip(lswitch, lswitch_bool)):
            data[i][4 if state == 'TRUE' else 5] = switch

        # Insert number of blocks and memories
        data[0][0] = num_blocks
        data[0][2] = number_of_memories

        return data

    def collapse(self, layout, key, visible):
        return sg.pin(sg.Column(layout, key=key, visible=visible))
    
    def create_layout(self):
        section = [[sg.Multiline(expand_x = True, horizontal_scroll=True, size = (54, 29), key = 'plc_code', background_color='Light Gray', text_color='Black')]]

        headings = ('N° of Blocks','Groups', 'N° of Memories','Relay Memories Labels', 'Limit Switch Enabled', 'Limit Switch Disabled')
        
        image_viewer_column = [
            [
                sg.Table(values = (self.data) , headings = headings, size = (1, 8), visible = False, key = 'table', display_row_numbers=False, auto_size_columns=True, justification='center')],
            [
                sg.Image(key="-IMAGE-", visible = False, expand_x = True)]
        ]

        layout_data = [
                [
                    sg.Text('Sequence:', size = (11, 2)), sg.Text(key = 'text', expand_x = True, size = (35, 2), text_color = 'White')],
                [
                    sg.Text('Insert stroke: ', size = (13, 1)),
                    sg.Input(key = 'input', size = (3, 1),
                    text_color='Black', background_color='White', pad=(10,1)),
                    sg.Text('E.g. A+, b-, etc..',expand_x = True, text_color = 'White', justification='right')],
                [
                    sg.Button('Finish', size =(10, 1), button_color='Green', mouseover_colors=('Black', 'White'), pad=(3, 20)),
                    sg.Button('Clear', size = (10, 1)), sg.Button('Delete', size = (10, 1)),
                    sg.Button("Display Phases' Diagram", expand_x = True, mouseover_colors=('Black', 'White'), expand_y = False, button_color = ('Black','Gray'))],
                [
                    sg.Checkbox('Show PLC ST code', enable_events=True, key = 'show_plc'),
                    sg.Checkbox('Show Data', enable_events=True, key = 'data', expand_x=True),
                    sg.Button("Create Ladder Logic", size=(20, 1), mouseover_colors=('Black', 'White'), expand_y = False, button_color = ('Black','Gray'))],
                [
                    sg.Output(expand_x=True, size=(0, 6), pad=(10,2), key='log', background_color="Light Gray", text_color="Black", font="Hack")],
                [
                    self.collapse(section, 'plc', False)],
            ]

        layout = [
            [
                sg.Column(layout_data, vertical_alignment= 'top'),
                sg.VSeperator(),
                sg.Column(image_viewer_column, visible = False, key = 'image_column'),
            ]
        ]

        return layout
        
    def handle_events(self, event, values):
        if event == 'input' + '_Enter':
            self.process_input(values['input'])

        if event == 'Finish':
            if not self.sequence_manager.sequence:
                print('[!] No sequence submitted.')
            elif not self.sequence_manager.close_sequence_handler():
                print("[!] The sequence isn't completed.")
            else:
                self.data = self.elaborate_data()
                diagrams(self.sequence_manager.sequence)
                Plc(self.sequence_manager.sequence)
                dir1 = os.path.join(self.path, 'plc/plc.st')
                with open(dir1, 'r') as p:
                    self.text = p.read()
                self.window['table'].update(self.data, visible=False)
                self.window['plc_code'].update(self.text)
                print("\n[+] Phases' diagram generated <-and-> PLC ST code generated")

        if event == 'Clear':
            self.sequence_manager.sequence.clear()
            self.window['text'].update('')
            self.window['-IMAGE-'].update(visible=False)
            self.window['plc_code'].update('')
            self.window['table'].update('')
            self.window['log'].update('')
            print(">>> Data cleared")

        if event == 'Delete':
            if self.sequence_manager.sequence:
                removed_stroke = self.sequence_manager.sequence.pop()
                sequence_display = '/'.join(self.sequence_manager.sequence) + '/'
                self.window['text'].update(sequence_display)
                print(f'[X] {removed_stroke} has been deleted.')
            else:
                print("[!] There is no sequence to delete")

        if event == "Display Phases' Diagram":
            self.toggle_bool2 = not self.toggle_bool2
            if self.sequence_manager.sequence:
                im = os.path.join(self.path, 'Plots/phases_diagram.png')
                self.window['-IMAGE-'].update(im, visible=self.toggle_bool2)
                self.window['image_column'].update(visible=self.toggle_bool2 or self.toggle_bool3)
            else:
                print("[!] No available sequence to be displayed. Please insert the sequence first.")

        if event == 'show_plc':
            self.toggle_bool1 = not self.toggle_bool1
            self.window['plc'].update(visible=self.toggle_bool1)
            self.window['plc_code'].update(self.text)

        if event == 'data':
            self.toggle_bool3 = not self.toggle_bool3
            self.window['table'].update(self.data, visible=self.toggle_bool3)
            self.window['image_column'].update(visible=self.toggle_bool3 or self.toggle_bool2)

        if event == 'Create Ladder Logic':
            output = LD().output
            print(f"[+] Created {output}.xml in the {self.path} folder. Click Import LD to import it in CODESYS.")

