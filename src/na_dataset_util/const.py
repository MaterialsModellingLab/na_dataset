"""
na_ds.const.py


This module provides constant values and type definitions for the NaDS package.
"""

from .type import NeighborInfo

PHASE_LABELS = [
    "fcc",
    # "bcc",
    # "hcp",
    "liquid",
]

NEIGHBOR_INFO_DICT: dict[int, NeighborInfo] = {
    1: NeighborInfo(
        radius=2.49,
        num_atoms=12,
        num_atoms_accumulated=12,
    ),
    2: NeighborInfo(
        radius=3.52,
        num_atoms=6,
        num_atoms_accumulated=18,
    ),
    3: NeighborInfo(
        radius=4.31,
        num_atoms=24,
        num_atoms_accumulated=42,
    ),
    4: NeighborInfo(
        radius=4.98,
        num_atoms=12,
        num_atoms_accumulated=54,
    ),
    5: NeighborInfo(
        radius=5.57,
        num_atoms=24,
        num_atoms_accumulated=78,
    ),
    6: NeighborInfo(
        radius=6.10,
        num_atoms=8,
        num_atoms_accumulated=86,
    ),
    7: NeighborInfo(
        radius=6.59,
        num_atoms=48,
        num_atoms_accumulated=134,
    ),
    8: NeighborInfo(
        radius=7.04,
        num_atoms=6,
        num_atoms_accumulated=140,
    ),
    9: NeighborInfo(
        radius=7.47,
        num_atoms=36,
        num_atoms_accumulated=176,
    ),
    10: NeighborInfo(
        radius=7.87,
        num_atoms=24,
        num_atoms_accumulated=200,
    ),
    11: NeighborInfo(
        radius=8.26,
        num_atoms=24,
        num_atoms_accumulated=224,
    ),
    12: NeighborInfo(
        radius=8.62,
        num_atoms=24,
        num_atoms_accumulated=248,
    ),
    13: NeighborInfo(
        radius=8.97,
        num_atoms=60,
        num_atoms_accumulated=308,
    ),
    14: NeighborInfo(
        radius=9.64,
        num_atoms=24,
        num_atoms_accumulated=332,
    ),
    15: NeighborInfo(
        radius=9.96,
        num_atoms=12,
        num_atoms_accumulated=344,
    ),
    16: NeighborInfo(
        radius=10.26,
        num_atoms=36,
        num_atoms_accumulated=380,
    ),
    17: NeighborInfo(
        radius=10.56,
        num_atoms=24,
        num_atoms_accumulated=404,
    ),
    18: NeighborInfo(
        radius=10.85,
        num_atoms=24,
        num_atoms_accumulated=428,
    ),
    19: NeighborInfo(
        radius=11.41,
        num_atoms=24,
        num_atoms_accumulated=452,
    ),
    20: NeighborInfo(
        radius=12.19,
        num_atoms=8,
        num_atoms_accumulated=460,
    ),
}

# Defined by 15th nearest neighbors of the fcc lattice
DEFAULT_NUM_ATOMS = 345
