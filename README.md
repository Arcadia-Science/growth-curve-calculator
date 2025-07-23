# Growth Curve Calculator

This Python package facilitates parsing, analyzing, and visualizing microplate reader data, with a focus on growth curves generated from optical density measurements.

Currently supports parsing data from the SpectraMax iD3 microplate reader, including:
- Endpoint measurements (single time point readings)
- Spectrum scans (wavelength sweeps)
- Kinetic measurements (time series data)

## Installation

Install via pip:
```bash
pip install git+https://github.com/Arcadia-Science/growth-curve-calculator.git
```


## Usage

### Parsing SpectraMax XML Files

```python
>>> from growth_curve_calculator import parse_spectramax_xml

# Extract plate reader data from an XML file
>>> xml_filepath = "growth_curve_calculator/tests/example_data/sample_endpoints_1.xml"
>>> plate_data_list = parse_spectramax_xml(xml_filepath)

# Number of plate reader runs
>>> len(plate_data_list)
2

# Get names of plates in the file
>>> [plate.name for plate in plate_data_list]
['Chlamy', 'Phaeo']
```

### Working with `MicroplateData`

```python
>>> type(plate)
growth_curve_calculator.microplate.MicroplateData

# Access the first plate's data
>>> plate = plate_data_list[0]

# View plate metadata
>>> plate.name
'Chlamy'
>>> print(plate.timestamp)
2024-08-06 22:19:29

>>> plate.plate_type
<PlateType.PLATE_96: 96>

>>> plate.metadata
{'Plate  (1 of 2)': '',
 'Plate name': 'Chlamy',
 'Barcode': '',
 'Microplate name': 'Standard clrbtm',
 'Rows': '8',
 'Columns': '12',
 'Well count': '96 Wells',
 ...
}

# Access measurement data (pandas DataFrame)
>>> dataframe = plate.measurements
>>> dataframe.head()

  well_row  well_column well_id  value  excitation_nm
1        A            6     A06  0.050          750.0
2        A            7     A07  0.040          750.0
3        A            8     A08  0.042          750.0
4        A            9     A09  1.063          750.0
6        B            6     B06  0.134          750.0
```

### Working with spectral data

```python
import matplotlib.pyplot as plt
from growth_curve_calculator import parse_spectramax_xml

# Parse a spectrum scan file
spectrum_file = "growth_curve_calculator/tests/example_data/sample_spectrum_scans.xml"
plate_data_list = parse_spectramax_xml(spectrum_file)

# Filter to known plate reader run
run_name = "day7pla1EX"
names = [plate.name for plate in plate_data_list]
run_index = names.index(run_name)
plate = plate_data_list[run_index]

# Filter measurements to a particular well
well_id = "A01"
well_data = plate.measurements.query("well_id == @well_id")

# Plot excitation spectrum
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(well_data["excitation_nm"], well_data["value"])

# Aesthetics
ax.fill_between(well_data["excitation_nm"], well_data["value"], alpha=0.1)
ax.set_xlabel("Excitation Wavelength (nm)")
ax.set_ylabel("Fluorescence Intensity")
ax.set_title(f"Excitation Spectrum for Well {well_id}")
```

<image src="docs/_assets/readme_excitation_spectrum.png" width="512"></image>


## Contributing

If you are interested in contributing to this package, please check out the [developer notes](docs/development.md).
See how we recognize [feedback and contributions to our code](https://github.com/Arcadia-Science/arcadia-software-handbook/blob/main/guides-and-standards/guide-credit-for-contributions.md).
