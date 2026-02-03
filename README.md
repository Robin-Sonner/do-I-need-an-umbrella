[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/nkxJlVK3)

# dinau
dinau -> Do I need an umbrella? is a python library that wraps the open-meteo api.
In addition to the library the project also contains an application that uses said library to display various weather information.
The library and application mainly serve to explore CI/CD both on python package and application production, though the software being both functional and useful is a secondary goal.

## Installation Instructions
- Ensure that the python version on your system is at least 3.12
- Use ./setup.sh PYTHON_VERSION where PYTHON_VERSION is 12, 13 or 14
This creates a virtual environment for you, upgrades pip, then builds the dinau package for you based on the pyproject.toml with all optional dependencies
- Instead of pip install ".[dev,gui]" (inside setup.sh) pip install . can also be used. This will only build dinau, and does not install development tools or PyQT6 which is used in the App

## Documentation
Either check out ________
or use

source venv/bin/activate
cd docs
make html

to build the documentation yourself (this assumes you have built the dinau package with optional dependencies). The documentation will be inside docs/_build

## License
MIT. See LICENSE for details

