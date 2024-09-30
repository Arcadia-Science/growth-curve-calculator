# growth-curve-calculator

This repo contains a Python package called `growth_curve_calculator`, the main purpose of which is to facilitate visualizing growth curves of cell cultures from optical density measurements.

Currently only supports parsing optical density measurements from the SpectraMax iD3.

## Installation

Clone the repository and install via pip:
```bash
git clone https://github.com/Arcadia-Science/growth-curve-calculator.git
cd growth-curve-calculator
pip install -e .
```

<!-- The package is hosted on PyPI and can be installed using pip:

```bash
pip install growth-curve-calculator
``` -->

## Usage

Read a SpectraMax XML file:
```python
from growth_curve_calculator.parse_SpectraMax_xml import SpectraMaxXmlParser

plate_reader = SpectraMaxXmlParser("some_SpectraMax_file.xml")
```

Example output:
```python
# get the names of each plate measured
>>> plate_reader.plate_names
['Phaeo', 'Protococcus', 'Tetraselmis']

# get the times at which each plate was measured
>>> plate_reader.read_times
[Timestamp('2024-08-22 19:50:34'),  # Phaeo
 Timestamp('2024-08-22 19:52:59'),  # Protococcus
 Timestamp('2024-08-22 19:52:59')]  # Tetraselmis

# get the optical density measurements of a plate as a pandas DataFrame
>>> plate_measurements = plate_reader.get_plate_measurements()
>>> plate_measurements["Tetraselmis"]
       1      2      3      4      5      6      7      8      9
A  0.061  0.077  0.054  0.058  0.098  0.085  0.074  0.109  0.142
B  0.075  0.074  0.058  0.057  0.106  0.082  0.067  0.060  0.146
C  0.092  0.092  0.055  0.062  0.093  0.092  0.064  0.069  0.156
D  0.161  0.183  0.070  0.078  0.112  0.136  0.120  0.178  0.109
```

## Contributing

If you are interested in contributing to this package, please check out the [developer notes](docs/development.md).
See how we recognize [feedback and contributions to our code](https://github.com/Arcadia-Science/arcadia-software-handbook/blob/main/guides-and-standards/guide-credit-for-contributions.md).
