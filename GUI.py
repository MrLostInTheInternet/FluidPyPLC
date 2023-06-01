from get_sequence import *

import PySimpleGUI as sg

def collapse(layout, key, visible):
    return sg.pin(sg.Column(layout, key=key, visible=visible))

class Gui():
    def __init__(self):
        self.s = []
    def run(self):
        section = [[sg.Multiline(expand_x = True, horizontal_scroll=True, size = (50, 19), key = 'plc_code')]]

        headings = ('Block S.','Groups', 'N. Memories','Relay Memories', 'L. S. Enabled', 'L. S. Disabled')

        image_viewer_column = [
            [sg.Table(values = data , headings = headings, size = (10, 6), auto_size_columns=True, expand_x = True, visible = False, key = 'table')],
            [sg.Image(key="-IMAGE-", visible = False, expand_x = True)]
        ]

        layout_data = [[sg.Text('Sequence:', size = (11, 2)), sg.Text(key = 'text', expand_x = True, size = (35, 2), text_color = 'Black')],
                    [sg.Text('Insert stroke: ', size = (11, 2)), sg.Input(key = 'input', size = (6, 2), text_color='Black')],
                    [sg.Button('Finish', size =(10, 1)), sg.Button('Clear', size = (10, 1)), sg.Button("Display Diagram's fases", expand_x = True, expand_y = True)],
                    [sg.Checkbox('Show PLC ST code', enable_events=True, key = 'checkbox_key'), sg.Checkbox('Show Data', enable_events=True, key = 'data')],
                    [collapse(section, 'plc', False)],
                ]

        layout = [
            [
                sg.Column(layout_data, vertical_alignment= 'top'),
                sg.VSeperator(),
                sg.Column(image_viewer_column, visible = False, key = 'image_column'),
            ]
        ]

        sequence = []

        window = sg.Window('GUI', layout, finalize = True)
        window['input'].bind("<Return>", "_Enter")

        # while True