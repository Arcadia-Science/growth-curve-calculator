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
from growth_curve_calculator import SpectraMaxData

xml_filepath = (
    "../../growth_curve_calculator/tests/example_data/"
    "Public_New ABS Protocol9_6_2024 10_54_51 PM_9_6_2024 10_53_28 PM.xml"
)
plate_reader = SpectraMaxData.from_xml(xml_filepath)
```

Example output:
```python
# get the names of each plate measured
>>> plate_reader.plate_names
['Phaeo', 'Isochrysis', 'Tetraselmis', 'Dunaliella']

# get the times at which each plate was measured
>>> plate_reader.read_times
[Timestamp('2024-09-06 22:47:13'),  # Phaeo
 Timestamp('2024-09-06 22:49:53'),  # Isochrysis
 Timestamp('2024-09-06 22:51:40'),  # Tetraselmis
 Timestamp('2024-09-06 22:53:41')]  # Dunaliella

# get the optical density measurements of a plate as a pandas DataFrame
>>> plate_reader.plate_measurements["Dunaliella"]
       1      2      3      4
A  0.411  0.351  0.366  0.400
B  0.320  0.326  0.372  0.311
C  0.438  0.347    NaN  0.355
D  0.331  0.473  0.931  0.758
```

## Contributing

If you are interested in contributing to this package, please check out the [developer notes](docs/development.md).
See how we recognize [feedback and contributions to our code](https://github.com/Arcadia-Science/arcadia-software-handbook/blob/main/guides-and-standards/guide-credit-for-contributions.md).
