# Quick Start Guide

## Installation

To install spyral-utils use pip:

```bash
pip install spyral-utils
```

As per usual, it is highly recommended to install spyral-utils to a virtual environment.

## Dependencies and Requirements

spyral-utils is cross platform and tested for MacOS, Windows, and Linux. spyral-utils explicitly supports Python versions 3.10, 3.11, and 3.12.

The required packages for spyral-utils are

- [numpy](https://numpy.org/)
- [scipy](https://scipy.org/)
- [shapely](https://shapely.readthedocs.io/)
- [polars](https://pola.rs/)
- [pycatima](https://github.com/hrosiak/pycatima)
- [vector](https://vector.readthedocs.io)
- Uses data from the AMDC AME 2020: Meng Wang et al 2021 Chinese Phys. C 45 030003

All of these will be automatically installed to your environment when running the installation command.

To generate the documentation locally you will also need

- [mkdocs](https://www.mkdocs.org)
- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings](https://mkdocstrings.github.io/)

and to run tests you'll need

- [pytest](https://docs.pytest.org)

These additional dependencies can be intstalled using the `-d` or `--dev` flag with pdm.

## Data Formats

Many of the objects used in spyral-utils can be serialized/deserialized to JSON. Below are the common use cases.

### Targets

The JSON description of a target is as follows:

For a gas target:

```json
{
    "id": null,
    "compound": [
        [1, 1, 2]
    ],
    "pressure(Torr)": 300.0,
    "thickness(ug/cm^2)": null
}
```

For a solid target:

```json
{
    "id": null,
    "compound": [
        [6, 12, 1]
    ],
    "pressure(Torr)": null,
    "thickness(ug/cm^2)": 50.0
}
```

The indication of a `null` pressure or thickness tells spyral-utils if that JSON is for a solid or gas target. Compound
specifications are lists of elements where each element is an array of `[Z, A, S]`. `S` is the stoichiometry of that particular 
element in the compound. spyral-utils does not support target layers at this time (but layered targets can be built from the
building blocks provided by spyral-utils). In the above examples the gas target is for <sup>1</sup>H<sub>2</sub> gas at 300
Torr pressure and the solid target is for <sup>12</sup>C<sub>1</sub> foil with a thickness of 50 &mu;g/cm<sup>2</sup>.

If you are using a material that is not easily defined by the compound field, you can use the CAtima definition, if it exists.
For example, if you are using P10 gas you can define the gas target as:

```json
{
    "id": "P10",
    "compound": null,
    "pressure(Torr)": 300.0,
    "thickness(ug/cm^2)": null
}
```

The list of available CAtima materials is:

- Plastics
- Air
- CH2
- LH2
- LD2
- Water
- Diamond
- Glass
- ALMG3
- ArCO2_30
- CF4
- Isobutane
- Kapton
- Mylar
- NaF
- P10
- Polyolefin
- CmO2
- Suprasil
- HAVAR
- Steel
- CO2
- CH4
- Methanol
- Acetone
- Acetylene
- Adenine
- Adipose_Tissue
- Alanine
- Bakelite
- AgBr
- AgCl
- AgI
- Al2O3
- Amber
- Ammonia
- Aniline
- Anthracene
- A_150
- B_100
- BaF2
- BaSO4
- Benzene
- BeO
- BGO
- Blood
- Bone_Compact
- Bone_Cortical
- Brain_ICRP
- B4C
- BC400
- nButanol
- C_552
- CdTe
- CdWO4
- CaCO3
- CaF2
- CaO
- CaWO4
- CsF
- CsI
- CCl4
- C2Cl4
- Cellophane
- Chlorobenzene
- Chloroform
- Cyclohexane
- Concrete
- Diethyl_Ether
- Ethane
- Ethanol
- Ethylene
- Eye_lens
- Fe2O3
- FeO
- Freon12
- Freon12B2
- Freon13
- Freon13B1
- Freon13I1
- Gd2O2S
- GaAs
- Gel_Photo_Emulsion
- Glass_Pyrex
- Glass_Lead
- Glucose
- Glutamine
- Glycerol
- Guanine
- Gypsum
- nHeptane
- nHexane
- KI
- K2O
- LaBr3
- LaOBr
- La2O2S
- Lung
- MgCO3
- MgF2
- MgO
- MS20_Tissue
- Muscle_skeletal
- Muscle_strained
- Muscle_sucrose
- Muscle_no_sucrose
- Na2CO3
- NaI
- NaCl
- Na2O
- NaNO3
- Naphthalene
- Nitrobenzene
- N2O
- Octane
- Paraffin
- nPentane
- PhotoEmulsion
- PuO2
- Polyacrylonitrile
- Polycarbonate
- PMMA
- POM
- Polypropylene
- Polystyrene
- Propane
- nPropanol
- PVC
- Pyridine
- SiO2
- Skin
- Sucrose
- Teflon
- TlCl
- Toluene
- Trichloroethylene
- WF6
- UC2
- UC
- UO2
- Urea
- Valine


### Cut2D

The JSON description of a Cut2D(or 2D-gate) on data is as follows:

```json
{
    "name": "test_cut",
    "vertices": [
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
        [0.0, 0.0]
    ]
}
```

`name` is a identifier given for that particular cut. `verticies` is a list of `[x,y]` coordinates which define the polygon. Note
that the polygon must be closed (the final vertex must be the same as the first vertex). You can also add the `xaxis` and `yaxis`
keywords to specify the names of the axes of the cut (i.e. the column names of a dataframe).

```json
{
    "name": "test_cut",
    "xaxis": "my_x",
    "yaxis": "my_y",
    "vertices": [
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
        [0.0, 0.0]
    ]
}
```

### Particle ID

The JSON description of a particle ID gate is as follows:

```json
{
    "name": "test_cut",
    "vertices": [
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
        [0.0, 0.0]
    ],
    "Z": 6,
    "A": 12
}
```

The `name` and `vertices` fields are the same as those used by a Cut2D. The particle ID has the additional data `Z` and `A` which are
the element and mass number of the associated nucleus. Like in a Cut2D you can also specify the axis names of the cut

```json
{
    "name": "test_cut",
    "xaxis": "my_x",
    "yaxis": "my_y",
    "vertices": [
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
        [0.0, 0.0]
    ],
    "Z": 6,
    "A": 12
}
```
