# Example Data

## SpectraMax
The example data in this folder consists of XML files output by a SpectraMax iD3 plate reader, representing different types of measurements.

### Endpoint Measurements
These files contain single-timepoint optical density measurements:
* `sample_endpoints_1.xml`
* `sample_endpoints_2.xml`
* `sample_endpoints_3.xml`

These endpoint measurement XML files were arbitrarily chosen from a large set of optical density measurements collected at Arcadia on a variety of protist and algal species including Phaeodactylum, Protococcus, Tetraselmis, Chlamydomonas, Isochrysis, and Dunaliella. Samples from cultures of these organisms were placed into wells of a 96-well plate and scanned by the SpectraMax iD3 plate reader daily to measure their optical density, as a proxy for their growth.

### Spectrum Scans
* `sample_spectrum_scans.xml`

This file contains wavelength sweep measurements of *E. coli* cells expressing GFP or GFP variants, where either the excitation or emission wavelength is varied across a range to create a spectrum profile for samples.

### Kinetic Measurements
* `sample_kinetics.xml`

This file contains time-series measurements of *E. coli* cells expressing GFP or GFP variants where samples are measured repeatedly over a specified time interval. Kinetic measurements are useful for tracking processes that change over time, such as enzyme kinetics, bacterial growth, or cellular responses to stimuli.
