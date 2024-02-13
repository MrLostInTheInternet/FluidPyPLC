from FluidPyPLC.get_sequence import *
from FluidPyPLC.data import Data
from FluidPyPLC.plc import Plc
from FluidPyPLC.diagrams import diagrams
from FluidPyPLC.LadderLogic.ld import LD
from tkinter import ttk
from ttkbootstrap import Style
from PIL import Image, ImageTk

import json
import os
import sys
import io
import pkg_resources
import tkinter as tk
import subprocess

class Gui():
    def __init__(self, root):
        self.sequence_manager = Sequence()
        self.data = []
        self.path = self.get_config_path()
        self.version = pkg_resources.get_distribution('FluidPyPLC').version
        self.root = root
        self.root.title(f'FluidPyPLC v{self.version}')
        self.style = Style(theme='litera')
        self.root.resizable(False, False)
        self.toggle_data = True
        self.toggle_plot = True
        self.toggle_plc_code = True
        self.text = ''
    
        # Create the main layout
        self.create_layout()
        self.data_table.grid_remove()
        self.diagram_plot.grid_remove()
        self.open_plot_button.grid_remove()
        self.plc_var_local_text.grid_remove()
        self.plc_var_global_text.grid_remove()
        self.plc_connections_text.grid_remove()
        self.plc_logic_groups_text.grid_remove()
        self.copy_local_var_button.grid_remove()
        self.copy_var_global_button.grid_remove()
        self.copy_connections_button.grid_remove()
        self.copy_plc_code_button.grid_remove()
        self.var_local_text_label.grid_remove()
        self.var_global_text_label.grid_remove()
        self.plc_connections_text_label.grid_remove()
        self.plc_code_text_label.grid_remove()

        self.stdout_capture = StdoutCapture()

        # Redirect stdout to the capture buffer
        sys.stdout = self.stdout_capture

        # Bind the window close event to handle gracefully exiting the application
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def run(self):
        self.log_text.insert(tk.END, f'>> Welcome to FluidPyPLC v{self.version}\n\n')
        self.root.mainloop()

    def display_print_output(self):
        # Get the captured output from the buffer
        printed_output = self.stdout_capture.getvalue()

        # Display the captured output in the log_text widget
        self.log_text.insert(tk.END, printed_output)

        # Clear the capture buffer after displaying the output
        self.stdout_capture.truncate(0)
        self.stdout_capture.seek(0)

    def get_config_path(self):
        try:
            config_file_path = pkg_resources.resource_filename('FluidPyPLC', 'resources/config.json')
            with open(config_file_path) as f:
                config = json.load(f)
                return config["folder_path"]
        except Exception as e:
            self.log_text.insert(tk.END, f"Error loading configuration: {e}\n")

    def process_input(self, event=None):
        stroke = self.input_entry.get().upper()
        if stroke == '/':
            self.log_text.insert(tk.END, "[!] Click Finish to submit the sequence.\n")
            self.input_entry.delete(0, tk.END)
            self.input_entry.focus_set()
            return
        # Validate the stroke format first
        if not self.sequence_manager.stroke_handler(stroke):
            self.display_print_output()
            return
        elif not self.sequence_manager.sequence_handler(stroke):
            self.display_print_output()
            return
        else:
            self.sequence_manager.sequence_append(stroke)
            sequence_display = '/'.join(self.sequence_manager.sequence) + '/'
            self.sequence_text.config(text=sequence_display)
            self.input_entry.delete(0, tk.END)
            self.input_entry.focus_set()

    def elaborate_data(self):
        try:
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
        except Exception as e:
            self.log_text.insert(tk.END, f"Error processing data: {e}\n")
            return []

    def create_layout(self):
        left_frame = ttk.Frame(self.root)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        ttk.Label(left_frame, text='Sequence:', style='Info.TLabel').grid(row=0, column=0, sticky='w', padx=5)
        self.sequence_text = ttk.Label(left_frame, text='', style='Info.TLabel')
        self.sequence_text.grid(row=0, column=1, sticky='w', padx=5)

        ttk.Label(left_frame, text='Insert stroke: ', style='Info.TLabel').grid(row=1, column=0, sticky='w', padx=5)
        self.input_entry = ttk.Entry(left_frame)
        self.input_entry.grid(row=1, column=1, sticky='ew')
        ttk.Label(left_frame, text='E.g. A+, b-, etc..', style='Info.TLabel').grid(row=1, column=2, sticky='e', padx=5)

        self.input_entry.bind("<Return>", lambda event: self.process_input())

        ttk.Button(left_frame, text='Finish', style='success.TButton', command=self.finish_sequence).grid(row=2, column=0, sticky='ew', pady=5, padx=5)
        ttk.Button(left_frame, text='Clear', style='warning.TButton', command=self.clear_data).grid(row=2, column=1, sticky='ew', pady=5, padx=5)
        ttk.Button(left_frame, text='Delete', style='danger.TButton', command=self.delete_sequence).grid(row=2, column=2, columnspan=2, sticky='ew', pady=5, padx=5)
        ttk.Button(left_frame, text='Toggle Data Table', style='primary.Outline.TButton', command=self.toggle_data_table).grid(row=3, column=0, sticky='ew', pady=5, padx=5)
        ttk.Button(left_frame, text='Toggle Diagram\'s Phases', style='primary.Outline.TButton', command=self.toggle_image_png).grid(row=3, column=1, sticky='ew', pady=5, padx=5)
        ttk.Button(left_frame, text='Create Ladder Logic', style='primary.Outline.TButton', command=self.create_ld_output).grid(row=3, column=2, sticky='ew', pady=5, padx=5)
        ttk.Button(left_frame, text='Show PLC Code', style='primary.Outline.TButton', command=self.toggle_plc_text).grid(row=3, column=3, sticky='ew', pady=5, padx=5)

        ttk.Label(left_frame, text='Log', style='Info.TLabel').grid(row=4, column=0, sticky='w', padx=5)
        self.log_text = tk.Text(left_frame, height=6, width=70)
        self.log_text.grid(row=5, column=0, columnspan=4, sticky='ew', pady=5, padx=5)


        self.var_local_text_label = ttk.Label(left_frame, text='Local Variables', style='Info.TLabel')
        self.var_local_text_label.grid(row=6, column=0, sticky='w', padx=5)

        self.var_global_text_label = ttk.Label(left_frame, text='Global Variables', style='Info.TLabel')
        self.var_global_text_label.grid(row=6, column=1, sticky='w', padx=5)

        self.plc_connections_text_label = ttk.Label(left_frame, text='Connections IO', style='Info.TLabel')
        self.plc_connections_text_label.grid(row=6, column=2, sticky='w', padx=5)

        self.plc_code_text_label = ttk.Label(left_frame, text='PLC Structured Text Code', style='Info.TLabel')
        self.plc_code_text_label.grid(row=8, column=0, sticky='w', padx=5)
        
        self.plc_var_local_text = tk.Text(left_frame, height=13, width=20)
        self.plc_var_local_text.grid(row=7, column=0, columnspan=1, sticky='ew', pady=5, padx=5)

        self.plc_var_global_text = tk.Text(left_frame, height=13, width=20)
        self.plc_var_global_text.grid(row=7, column=1, columnspan=1, sticky='ew', pady=5, padx=5)

        self.plc_connections_text = tk.Text(left_frame, height=13, width=50)
        self.plc_connections_text.grid(row=7, column=2, columnspan=2, sticky='ew', pady=5, padx=5)

        self.plc_logic_groups_text = tk.Text(left_frame, height=16, width=70)
        self.plc_logic_groups_text.grid(row=8, column=0, columnspan=4, sticky='ew', pady=5, padx=5)

        self.copy_local_var_button = ttk.Button(left_frame, text='Copy', style='success.TButton', command=lambda: self.copy_to_clipboard(self.plc_var_local_text))
        self.copy_local_var_button.grid(row=6, column=0, sticky='e', padx=5)

        self.copy_var_global_button = ttk.Button(left_frame, text='Copy', style='success.TButton', command=lambda: self.copy_to_clipboard(self.plc_var_global_text))
        self.copy_var_global_button.grid(row=6, column=1, sticky='e', padx=5)

        self.copy_connections_button = ttk.Button(left_frame, text='Copy', style='success.TButton', command=lambda: self.copy_to_clipboard(self.plc_connections_text))
        self.copy_connections_button.grid(row=6, column=3, sticky='e', padx=5)

        self.copy_plc_code_button = ttk.Button(left_frame, text='Copy', style='success.TButton', command=lambda: self.copy_to_clipboard(self.plc_logic_groups_text))
        self.copy_plc_code_button.grid(row=8, column=3, sticky='e', padx=5)

        # Right side layout (image viewer and table)
        right_frame = ttk.Frame(self.root)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

        # Image Placeholder
        self.diagram_plot = tk.Label(right_frame, text="Diagram Phases Image", relief="ridge")
        self.diagram_plot.grid(row=0, column=0, sticky='nsew')

        self.open_plot_button = ttk.Button(right_frame, text='Open Plots folder', command=self.open_plots_folder)
        self.open_plot_button.grid(row=0, column=1, sticky='se', padx=10, pady=10)

        headings = ('N° of Blocks', 'Groups', 'N° of Memories', 'Relay Memories', 'Switch Enabled', 'Switch Disabled')
        self.data_table = ttk.Treeview(right_frame, columns=headings, show='headings')
        for heading in headings:
            self.data_table.heading(heading, text=heading)
            self.data_table.column(heading, width=100)  # Set column width
        self.data_table.grid(row=2, column=0, sticky='nsew')

        # Add scrollbar for the data table
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.data_table.yview)
        scrollbar.grid(row=2, column=1, sticky='ns')
        self.data_table.configure(yscrollcommand=scrollbar.set)

    def open_plots_folder(self):
        try:
            plots_folder_path = os.path.join(self.path, 'Plots')
            if os.path.exists(plots_folder_path):
                match sys.platform:
                    case "darwin":  # MacOS
                        subprocess.call(['open', plots_folder_path])
                    case "win32":   # Windows
                        os.startfile(plots_folder_path)
                    case _:
                        subprocess.call(['xdg-open', plots_folder_path])  # Linux, Unix, etc.
            else:
                self.log_text.insert(tk.END, "Plots folder not found.\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"Error opening plots folder: {e}\n")

    def clear_stdout(self):
        sys.stdout = io.StringIO()

    def clear_data(self):
        self.sequence_manager.sequence.clear()
        self.sequence_text.config(text='')
        self.diagram_plot.config(text='Diagram Phases Image')
        self.log_text.delete('1.0', tk.END)
        self.plc_var_local_text.delete('1.0', tk.END)
        self.plc_var_global_text.delete('1.0', tk.END)
        self.plc_connections_text.delete('1.0', tk.END)
        self.plc_logic_groups_text.delete('1.0', tk.END)
        self.data_table.delete(*self.data_table.get_children())
        self.log_text.insert(tk.END, ">>> Data cleared\n")
        self.clear_stdout()

    def delete_sequence(self):
        if self.sequence_manager.sequence:
            removed_stroke = self.sequence_manager.sequence.pop()
            sequence_display = '/'.join(self.sequence_manager.sequence) + '/'
            self.sequence_text.config(text=sequence_display)
            self.log_text.insert(tk.END, f'[X] {removed_stroke} has been deleted.\n')
        else:
            self.log_text.insert(tk.END, "[!] There is no sequence to delete\n")

    def finish_sequence(self):
        if not self.sequence_manager.sequence:
            self.log_text.insert(tk.END, '[!] No sequence submitted.\n')
            return
        if not self.sequence_manager.close_sequence_handler():
            self.log_text.insert(tk.END, "[!] The sequence isn't completed.\n")
            return
        self.data = self.elaborate_data()
        diagrams(self.sequence_manager.sequence)

        Plc(self.sequence_manager.sequence)
        dir1 = os.path.join(self.path, 'plc/plc.st')

        if os.path.exists(dir1):
            with open(dir1, 'r') as p:
                plc_content = p.readlines()
            plc_var_local_text = ""
            plc_var_global_text = ""
            plc_connections_text = ""
            plc_logic_groups_text = ""
            current_section = ""
            for line in plc_content:
                if line.startswith("VAR_GLOBAL"):
                    current_section = "global"
                elif line.startswith("//"):
                    current_section = "connections"
                elif line.startswith("IF"):
                    current_section = "logic_groups"

                if current_section == "global":
                    plc_var_global_text += line
                elif current_section == "connections":
                    plc_connections_text += line
                elif current_section == "logic_groups":
                    plc_logic_groups_text += line
                else:
                    plc_var_local_text += line

            self.plc_var_local_text.delete('1.0', tk.END)
            self.plc_var_local_text.insert(tk.END, plc_var_local_text + '\n')

            self.plc_var_global_text.delete('1.0', tk.END)
            self.plc_var_global_text.insert(tk.END, plc_var_global_text + '\n')

            self.plc_connections_text.delete('1.0', tk.END)
            self.plc_connections_text.insert(tk.END, plc_connections_text + '\n')

            self.plc_logic_groups_text.delete('1.0', tk.END)
            self.plc_logic_groups_text.insert(tk.END, plc_logic_groups_text + '\n')
        else:
            self.log_text.insert(tk.END, "No available sequence found.\n")
            self.toggle_bool1 = False
        self.data_table.delete(*self.data_table.get_children())
        for row in self.data:
            self.data_table.insert('', 'end', values=row)
        self.log_text.insert(tk.END, "\n[+] Phases' diagram generated <-and-> PLC ST code generated\n")
        self.set_diagram_phases_image()

    def set_diagram_phases_image(self):
        try:
            # Load and display the image
            image_path = os.path.join(self.path, 'Plots/phases_diagram.png')
            image = Image.open(image_path)
            image = ImageTk.PhotoImage(image)
            self.diagram_plot.config(image=image)
            self.diagram_plot.image = image  # Keep a reference to avoid garbage collection
        except Exception as e:
            self.log_text.insert(tk.END, f"Error displaying diagram phases image: {e}\n")

    def toggle_data_table(self):
        if self.toggle_data:
            self.data_table.grid(row=2, column=0, sticky='nsew')
        else:
            self.data_table.grid_remove()
        self.toggle_data = not self.toggle_data

    def toggle_image_png(self):
        if self.toggle_plot:
            self.diagram_plot.grid(row=0, column=0, sticky='nsew')
            self.open_plot_button.grid(row=1, column=0, sticky='se', padx=10, pady=10)
        else:
            self.diagram_plot.grid_remove()
            self.open_plot_button.grid_remove()
        self.toggle_plot = not self.toggle_plot

    def toggle_plc_text(self):
        if self.toggle_plc_code:
            self.var_local_text_label.grid(row=6, column=0, sticky='w', padx=5)
            self.var_global_text_label.grid(row=6, column=1, sticky='w', padx=5)
            self.plc_connections_text_label.grid(row=6, column=2, sticky='w', padx=5)
            self.plc_code_text_label.grid(row=8, column=0, sticky='w', padx=5)
            self.copy_local_var_button.grid(row=6, column=0, sticky='e', padx=5)
            self.copy_var_global_button.grid(row=6, column=1, sticky='e', padx=5)
            self.copy_connections_button.grid(row=6, column=3, sticky='e', padx=5)
            self.copy_plc_code_button.grid(row=8, column=3, sticky='e', padx=5)
            self.plc_var_local_text.grid(row=7, column=0, columnspan=1, sticky='ew', pady=5, padx=5)
            self.plc_var_global_text.grid(row=7, column=1, columnspan=1, sticky='ew', pady=5, padx=5)
            self.plc_connections_text.grid(row=7, column=2, columnspan=2, sticky='ew', pady=5, padx=5)
            self.plc_logic_groups_text.grid(row=9, column=0, columnspan=4, sticky='ew', pady=5, padx=5)
        else:
            self.var_local_text_label.grid_remove()
            self.var_global_text_label.grid_remove()
            self.plc_connections_text_label.grid_remove()
            self.plc_code_text_label.grid_remove()
            self.copy_local_var_button.grid_remove()
            self.copy_var_global_button.grid_remove()
            self.copy_connections_button.grid_remove()
            self.copy_plc_code_button.grid_remove()
            self.plc_var_local_text.grid_remove()
            self.plc_var_global_text.grid_remove()
            self.plc_connections_text.grid_remove()
            self.plc_logic_groups_text.grid_remove()
        self.toggle_plc_code = not self.toggle_plc_code

    def create_ld_output(self):
        if self.sequence_manager.sequence:
            output = LD().output
            self.log_text.insert(tk.END, f"[+] Created {output}.xml in the {self.path} folder. Click Import LD to import it in CODESYS.\n")
        else:
            self.log_text.insert(tk.END, "[!] No available sequence to be displayed. Please insert the sequence first.\n")
            
    def copy_to_clipboard(self, text_box):
        self.root.clipboard_clear()
        content = text_box.get("1.0", "end-1c")
        self.root.clipboard_append(content)

    def close_window(self):
        self.root.quit()
        self.root.destroy()

class StdoutCapture(io.StringIO):
    def write(self, s):
        # Capture the printed output
        super().write(s)
        self.flush()
