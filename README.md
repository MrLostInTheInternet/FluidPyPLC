<p align="center">
    <h1 align="center">
        🔗 FluidPyPLC
    </h1>
    <p align="center">
    Analyzer of Circuits' Sequences
    <br/>
    PLC ST code Generator <br>
    Ladder Logic converter</p>
</p>

[![Downloads](https://static.pepy.tech/badge/FluidPyPLC)](https://pepy.tech/project/FluidPyPLC)
![PyPI version](https://img.shields.io/pypi/v/FluidPyPLC.svg)
[![Snyk Vulnerabilities](https://snyk.io/advisor/python/FluidPyPLC/badge.svg)](https://snyk.io/advisor/python/FluidPyPLC)
![License](https://img.shields.io/pypi/l/FluidPyPLC.svg)
[![PyPI Downloads](https://img.shields.io/pypi/dd/FluidPyPLC.svg)](https://pypi.org/project/FluidPyPLC/)
[![Downloads](https://static.pepy.tech/badge/FluidPyPLC/month)](https://pepy.tech/project/FluidPyPLC)
![Python Version](https://img.shields.io/pypi/pyversions/FluidPyPLC.svg)

<div align="center">
  <h4>
    <a href="/CONTRIBUTING.md">
      👥 Contributing
    </a>
    <a href="/LICENSE">
      📄License
    </a>
  </h4>
</div>

# Simulation
<p align="center">
    <img alt="UI" src="https://github.com/MrLostInTheInternet/FluidPyPLC/blob/main/assets/newUi.png" style="width:650px" align="left">
    <img alt="FluidSim" src="https://github.com/MrLostInTheInternet/FluidPyPLC/blob/main/assets/FluidSim.gif" style="width:275px;" align="right">
    <img alt="FluidSim" src="https://github.com/MrLostInTheInternet/FluidPyPLC/blob/main/assets/newUI_fluidsim_related.png" style="width:275px;" align="right">
</p>
<br clear="all"/>

# Table of Contents
- [Table of Contents](#table-of-contents)
- [🏁 Getting Started ](#getting-started)
  - [⚙️ Configuration ](#configuration)
  - [⬇️ Installation ](#️installation)
  - [🎈 Usage ](#usage)
  - [⚙️ CODESYS configuration ](#codesys_configuration)
- [📄 License](#license)
- [✍️ Authors ](#️authors)
# 🏁 Getting Started <a name = "getting-started"></a>

FluidPyPLC is an updated version of the previous FluidPy, it is more light and efficient than before. It has new settings and can handle more sequence's cases.
Enjoy the new version.

<h1>What is FluidPyPLC?</h1>
It's a python script that takes any sequence of pistons e.g. A+/B-/B+/A-. It solves all the blocks of the inserted sequence, it draws the Phases' Diagram, and converts the solution in Structured Text for PLCs. The GUI mode will show you the data structure of the sequence, the plc ST code and the plot. You can then copy and paste the ST code in any program you want that reads it, e.g. CODESYS.
(I tried with CODESYS and works)


## ⚙️ Configuration <a name="configuration"></a>
To use this tool you need to install Python and Pip on your computer. For Windows users you can find it [here](https://python.org/downloads) or by using:
```bash
winget install python3 python3-pip
```
For Linux users you can install it via apt:
```bash
sudo apt-get install python3 python3-pip python3-tk
```
## ⬇️ Installation <a name="installation"></a>
Use pip to install FluidPyPLC:
```bash
pip install FluidPyPLC
pip install setuptools
```

Now you need to set a main folder where to save your data, and you need to create there the Plot and the plc folder. You can do it manually or you can use:
```bash
fluidpy --folder path/to/your/folder
```
And FluidPyPLC will create the two folders for you, and change the config.json file "folder_path" to "your folder path".

[+] For Windows Users. If you want an icon to execute the GUI faster -> create a new shortcut and assign the Target:
```bash
Target: fluidpy.exe --gui
```
Windows will automatically locate the fluidpy.exe script in your Python/scripts folder and you can launch the app from your icon now.

If fluidpy.exe is not recognize as a command, you have to add the Python/scripts to your PATH, locate then your Python/scripts folder on your computer, copy the path and add it to the PATH ENV Variables.

[Use my favicon if you want]
## 🎈 Usage <a name="usage"></a>
You can invoke the command from anywhere on your terminal:
```bash
fluidpy
```

To view all the usage's methods use the tags ```--help``` or ```-h```.
 
## ⚙️ CODESYS configuration <a name="codesys_configuration"></a>
[+] To test your PLC's sequence code you can use the plc.py and one of the CONFIGURATION pdfs in the Configurations folder.


[+] If you want to test the code with the CODESYS Visualization, use the plc.bak2.py as plc.py, and the tutorial below. 

In CODESYS you have to create a project. In the project you will have your PLC device, your main application with your main PRG file. To test the ST code you must add a Modbus Serial Device to handle the inputs and outputs of your plc. The Modbus will act as an intermediate between your code and a virtual plc device, like you are setting up the inputs and outputs on a plc in real life.

To do that, open your CODESYS project, go to
```bash
Tools -> CODESYS installer
```
then search for "Modbus" and install the modules required. After that you have to
```bash
right-click your PLC device -> Add device 
```
and then select
```bash
Modbus -> Modbus serial port -> Modbus COM
```
Now that the Modbus COM is added: <br>
```bash
right-click Modbus_COM -> Add device -> Select Modbus -> Modbus serial device -> Modbus Serial Device
```
If you want to rename it you can (e.g. Modbus I/O handler, etc..). <br>
Now <b>right-click it -> Map I/O</b> and finally you can map your inputs and outputs based on the ST code generated by FluidPyPLC. <br>
Now you only have to design your Machine in the visualization file and assign the switches to the limit switches (To test the code, you have to manually change the limit switches as you don't have physical Pneumatic Pistons with physical limit switches). Enjoy your PLC's simulation.

## 🎈 Ladder Logic <a name="LadderLogic"></a>
In the GUI mode you can launch the Ladder Logic Converter and it will create an output.xml file into the main path chosen by you. The .xml file will be in PLCopenXML format ready to be imported into CODESYS.

Things to still add to the code:
- [X] Ladder Logic Converter
- [ ] Automatic Import Button
- [ ] Automatic PLC configuration between CODESYS and FluidSim

# 📄 License <a name = "license"></a>
GPLv3

# ✍️ Authors <a name = "authors"></a>
- [MrLostInTheInternet](https://github.com/MrLostInTheInternet)

<p align="center">
<br>
<a href="https://github.com/MrLostInTheInternet" target='_blank'>
<img height='32' style='border:0px;height:32px;border-radius:.5rem' src='https://img.shields.io/badge/GitHub-100000?style&#x3D;for-the-badge&amp;logo&#x3D;github&amp;logoColor&#x3D;white' border='0'
</a>

<a href="https://youtu.be/aMCsqmX1pOI" target='_blank'>
<img height='32' style='border:0px;height:32px;border-radius:.5rem' src='https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white'
border='0'
</a>
    
<p align="center">
thanks to <a href="https://github.com/writeme-project/writeme">writeme</a> for the README template
</p>
