from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'FluidSim Circuits Analyzer & PLC ST Code Generator'
LONG_DESCRIPTION = "FluidPyPLC solves complex pneumatics/oleodynamics circuits' sequences and generates an ST code to use on any PLC to run those sequences"

# Setting up
setup(
    name="FluidPyPLC",
    version=VERSION,
    author="MrLostInTheInternet (Eugen Iofciu Vasile)",
    author_email="<eugen.iofciuvasile@hotmail.com>",
    license="GPLv3",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['PySimpleGUI', 'matplotlib', 'tk', 'pillow'],
    entry_points={
        'console_scripts': [
            'FluidPyPLC = FluidPyPLC.main:f',
        ]},
    keywords=['python', 'plc', 'fluidsim', 'structured text', 'plc python', 'codesys', 'circuits', 'pneumatics', 'oleodynamics', 'plc programming'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

