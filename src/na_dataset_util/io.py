"""
na_ds.io.py

This module provides io functions for LAMMPS data files and extract relevant information.
"""

from pathlib import Path

import numpy as np

from .type import NaDataset
from .util import dict2short_hash_filename


def write_train_test_txt(
    odir: Path,
    ofiles: list[Path],
    split: float = 0.8,
    overwrite: bool = False,
):
    """
    Export the train/test split to a text file.

    Args:
        odir (Path): The output directory.
        ofiles (list[Path]): List of output files.
        split (float): The split ratio for train/test data.
    """
    shuffled_ofiles = np.random.permutation(ofiles)
    num_train = int(len(ofiles) * split)
    filenames_list = [shuffled_ofiles[:num_train], shuffled_ofiles[num_train:]]
    txt_files = [odir / "train.txt", odir / "test.txt"]

    for txt_file, filenames in zip(txt_files, filenames_list, strict=True):
        if txt_file.exists() and not overwrite:
            raise FileExistsError(
                f"File {txt_file} already exists. "
                "Please remove it or use a different output directory."
            )
        with open(txt_file, "w", encoding="utf-8") as f:
            f.writelines(f"{filename.name}\n" for filename in filenames)


def write_dataset(
    odir: Path,
    dataset: NaDataset,
    overwrite: bool = False,
) -> Path:
    """
    Write NaDS content to a file.

    Args:
        odir (Path): The output directory.
        ds_content (NaDSContent): The NaDS content to write.
        overwrite (bool): Overwrite existing files.
    """
    odir.mkdir(parents=True, exist_ok=True)
    ofile = odir / dict2short_hash_filename(dataset)
    if ofile.exists() and not overwrite:
        raise FileExistsError(
            f"File {ofile} already exists. Please remove it or use a different output directory."
        )
    np.savez_compressed(ofile, **dataset)

    return ofile
