# spyral-utils

![CI](https://github.com/ATTPC/spyral-utils/actions/workflows/ci.yml/badge.svg)
[![PyPI version shields.io](https://img.shields.io/pypi/v/spyral-utils.svg)](https://pypi.python.org/pypi/spyral-utils/)
[![PyPI license](https://img.shields.io/pypi/l/spyral-utils.svg)](https://pypi.python.org/pypi/spyral-utils/)

spyral-utils is a utility library that contains some of the  core functionality of [Spyral](https://github.com/ATTPC/Spyral.git). These utilities were found to be useful not just within Spyral but also continuing analysis after using Spyral. Some key utilities include:

- Nuclear masses from the AMDC AME 2020 masses
- Some histogramming and gating/cuting tools that are plotting backend agnostic
- Energy loss analysis for gas and solid targets using pycatima
- 4-vector analysis through the vector package

See the [documentation](https://attpc.github.io/spyral-utils/) for more details.

## Installation

spyral-utils can be installed using `pip install spyral-utils`

## System requirements

spyral-utils requires Python >= 3.10 and  < 3.13

spyral-utils is cross-platform and tested for MacOS 14, Windows 11, and Ubuntu 22.04.

## Formats

Several parts of the utilities allow for saving and creating objects from JSON. Below is an outline of the expected formats for each of these

### Targets

For a gas target:

```json
{
    "compound": [
        [1, 1, 2]
    ],
    "pressure(Torr)": 300.0
}
```

For a solid target:

```json
{
    "compound": [
        [6, 12, 1]
    ],
    "thickness(ug/cm^2)": 50.0
}
```

For a gas mixture:

```json
{
    "components": [
        [
            [6, 12, 1],
            [1, 1, 4],
        ],
        [
            [18, 40, 1]
        ]
    ],
    "volume_fractions": [0.1, 0.9],
    "pressure(Torr)": 50.0
}
```

Compound specifications are lists of elements where each element is an array of `[Z, A, S]`. `S` is the 
stoichiometry of that particular element in the compound. spyral-utils does not support target layers at 
this time (but layered targets can be built from the building blocks provided by spyral-utils). In the above examples the 
gas target is for <sup>1</sup>H<sub>2</sub> gas at 300 Torr pressure and the solid target is for
<sup>12</sup>C<sub>1</sub> foil with a thickness of 50 &mu;g/cm<sup>2</sup>. The gas mixutre example is for
P10 gas (10% methane in argon) at 50 Torr.

### 2D-Cuts

The JSON description of a 2D-Cut (or 2D-gate) on data is as follows:

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

`name` is a identifier given for that particular cut. `verticies` is a list of `[x,y]` coordinates which define the polygon. Note that the polygon must be closed (the final vertex must be the same as the first vertex). You can also add the `xaxis` and `yaxis` keywords to specify the names of the axes of the cut (i.e. the column names of a dataframe).

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

The `name` and `vertices` fields are the same as those used by a Cut2D. The particle ID has the additional data `Z` and `A` which are the element and mass number of the associated nucleus. Like in a Cut2D you can also specify the axis names of the cut

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

## References

- [CAtima](https://github.com/hrosiak/catima)/[pycatima](https://github.com/hrosiak/pycatima)
- [AMDC Mass Evaluation](https://www-nds.iaea.org/amdc/): W.J. Huang et al 2021 Chinese Phys. C 45 030002
- [scipy](https://scipy.org/)
- [numpy](https://numpy.org/)
- [shapely](https://shapely.readthedocs.io/)
- [polars](https://www.pola.rs/)
- [vector](https://vector.readthedocs.io/)

For documentation we use

- [mkdocs](https://www.mkdocs.org)
- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings](https://mkdocstrings.github.io/)

For testing we use

- [pytest](https://docs.pytest.org/)

## Authors

- Gordon McCann
- Nathan Turi
