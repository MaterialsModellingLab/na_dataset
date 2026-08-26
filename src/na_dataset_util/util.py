"""
na_ds.util.py

This module provides utility functions.
"""

import hashlib
import json

import numpy as np

from .const import PHASE_LABELS


def dict2short_hash_filename(
    contents: dict, prefix: str = "", extension: str = ".npz", length=12
) -> str:
    """
    Generate a short hash filename from a dictionary.
    """

    def convert_for_serialization(obj: dict):
        if isinstance(obj, (np.ndarray, np.generic)):
            return hashlib.sha256(obj.data.tobytes()).hexdigest()
        elif isinstance(obj, dict):
            return {k: convert_for_serialization(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_for_serialization(v) for v in obj]
        return obj

    serializable_contents = convert_for_serialization(contents)
    json_str = json.dumps(serializable_contents, sort_keys=True, separators=(",", ":"))
    full_hash = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
    short_hash = full_hash[:length]
    return f"{prefix}{short_hash}{extension}"


def validate_label(label: str) -> bool:
    """
    Validate the label for the phase.
    """
    return label in PHASE_LABELS


def label2str(label: int) -> str:
    """
    Convert a label to its string representation.
    """
    if label < 0 or label >= len(PHASE_LABELS):
        raise ValueError(f"Invalid label: {label}")
    return PHASE_LABELS[label]


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 13:
        suffix = "th"
    else:
        match n % 10:
            case 1:
                suffix = "st"
            case 2:
                suffix = "nd"
            case 3:
                suffix = "rd"
            case _:
                suffix = "th"
    return f"{n}{suffix}"
