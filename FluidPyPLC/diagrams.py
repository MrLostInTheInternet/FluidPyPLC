import json
import matplotlib.pyplot as plt
import os
import pkg_resources
from FluidPyPLC.data import Data

config_file_path = pkg_resources.resource_filename('FluidPyPLC', 'resources/config.json')
with open(config_file_path) as f:
    config = json.load(f)
    path = config["folder_path"]

# get the x and y axis for the Phase's diagrams
def xy_axis(number_of_pistons, pistons_labels, sequence):
    number_of_pistons , piston_labels = number_of_pistons, pistons_labels
    x_axis = list(range(0, len(sequence) + 1))
    y_axis = [[0 for strokes in range(len(sequence) + 1)] for label in range(number_of_pistons)]

    # first loop to assign the values 1 or 0 to y axis based on each first stroke of the pistons
    for i in range(number_of_pistons):
        tmp_label = piston_labels[i]
        seen = []
        for j in range(len(sequence)):
            if tmp_label == sequence[j][0] and sequence[j][1] == '+':
                if tmp_label not in seen:
                    for z in range(len(sequence) + 1):
                        y_axis[i][z] = 0
                    seen.append(tmp_label)
                else:
                    break
            elif tmp_label == sequence[j][0] and sequence[j][1] == '-':
                if tmp_label not in seen:
                    for z in range(len(sequence) + 1):
                        y_axis[i][z] = 1
                    seen.append(tmp_label)
                else:
                    break

    # second loop to assign the values 1 or 0 to y axis based on the positive and negative strokes of all pistons
    for i in range(number_of_pistons):
        tmp_label = piston_labels[i]
        index = 0
        for j in range(len(sequence)):
            if tmp_label == sequence[j][0]:
                if sequence[j][1] == '+':
                    for z in range(index,j + 1):
                        y_axis[i][z] = 0
                    index = j + 1
                else:
                    for z in range(index, j + 1):
                        y_axis[i][z] = 1
                    index = j + 1
            else:
                continue

    return x_axis, y_axis

# draw the diagrams and save the plot as an image in the Plots folder
def diagrams(s):
    try:
        d = Data(s)
        number_of_pistons, labels = d.number_of_pistons, d.pistons_labels
        cell_text = [d.lswitch]
        columns = d.sequence

        fig, axs = plt.subplots(nrows=number_of_pistons, ncols=1)
        plt.get_current_fig_manager().set_window_title("Diagram's Phases")
        colors = plt.rcParams["axes.prop_cycle"]()
        x_axis, y_axis = xy_axis(number_of_pistons, labels, s)

        for i, ax in enumerate(axs if number_of_pistons > 1 else [axs]):
            c = next(colors)["color"]
            ax.set_ylabel(str(labels[i]), rotation=0, color=c)
            ax.set_ylim([0, 1.0])
            ax.set_yticks(range(2))
            ax.set_xlim([0, len(d.sequence)])
            ax.plot(x_axis, y_axis[i], 'o-', color=c)

        diagram = fig.add_subplot()
        diagram.table(cellText=cell_text, rowLabels=['limit switches'], colLabels=columns, loc='bottom', bbox=[0.0, -0.25, 1, 0.12])
        diagram.axis('off')
        plt.subplots_adjust(left=0.190, bottom=0.210, right=0.900, top=0.970, wspace=None, hspace=1.000)
        dir = os.path.join(path, 'Plots/phases_diagram.png')
        plt.savefig(dir)
    except:
        print("An error occurred: unable to create the plot")