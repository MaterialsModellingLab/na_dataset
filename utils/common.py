# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

import pathlib

THIS_SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
DATA_DIR = THIS_SCRIPT_DIR / "data"
IMAGE_DIR = THIS_SCRIPT_DIR / "images"
LAMMPS_OUTPUT_DIR = THIS_SCRIPT_DIR.parent / "lammps" / "output"

DATA_DIR.mkdir(exist_ok=True)
IMAGE_DIR.mkdir(exist_ok=True)
