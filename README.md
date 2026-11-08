# Welcome
September 2022 is a month to remember (well at least if you get excited about
advanced numerical simulation).  The reason is that
[Altair](https://www.altair.com) announced the immediate availability in the
opensource domain of their explicit finite element code Radioss.
Now it is up to the community to start adding useful new features.
You can find the source code at [OpenCourant](https://github.com/orgs/OpenCourant).

# Introduction 
`pycourant` is a set of tools and utilities that support the use of OpenCourant.

# Dependencies
python-gmsh = "*"
pyvista = ">=0.48.4,<0.49"
beautifulsoup4 = "*"

# Todo
1. https://help.altair.com/hwsolvers/rad/topics/solvers/rad/starter_input_r.htm
2. upstream amim file reader to pyvista https://github.com/pyvista/pyvista/issues/8833

# Contributing
Please read guideline.md on conventions used in this project.

# Acknowledgment & Reference
1. The input keyword file generator originates from  [operato](https://github.com/nawijn/operato)
2. The automatic keyword parser is from https://github.com/Serince/operato
3. Keywords reference https://github.com/PhRoWe/operato
4. Document download tool from https://github.com/CalzitPLA/FC_OpenCourant
