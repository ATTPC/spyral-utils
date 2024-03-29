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