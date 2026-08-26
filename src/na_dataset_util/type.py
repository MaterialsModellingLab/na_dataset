"""
na_ds.type.py

This module provides type definitions for the NaDataset package.
"""

from typing import Annotated, Literal, TypedDict, TypeVar

import numpy as np
import numpy.typing as npt

DType = TypeVar("DType", bound=np.generic)
Array3 = Annotated[npt.NDArray[DType], Literal[3]]
Array3x2 = Annotated[npt.NDArray[DType], Literal[3, 2]]
ArrayNx3 = Annotated[npt.NDArray[DType], Literal["N", 3]]
ArrayN = Annotated[npt.NDArray[DType], Literal["N"]]


class NeighborInfo(TypedDict):
    """
    Structure to hold neighbor information.
    """

    radius: float
    num_atoms: float
    num_atoms_accumulated: float


class NaDataset(TypedDict):
    """
    Structure to hold NaDS content.
    """

    atoms: ArrayNx3[np.float32]
    label: str
    temperature: np.float32
    original_lammps_data_filename: str
