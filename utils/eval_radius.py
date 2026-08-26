#!/usr/bin/env python3
# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

import argparse
import logging
import sys

import numpy as np
import pandas as pd
import plotly as px
import plotly.graph_objects as go
import plotly.io as pio
from common import DATA_DIR

from na_dataset_util import NEIGHBOR_INFO_DICT, PHASE_LABELS
from na_dataset_util.util import ordinal

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
handler.setLevel(logging.INFO)
logger.propagate = False

pio.renderers.default = "browser"

NEIGHBOR_TABLE_FCC = {
    info["num_atoms_accumulated"] + 1: ordinal(idx)
    for idx, info in NEIGHBOR_INFO_DICT.items()
}


def load(args: dict[str, any]) -> pd.DataFrame:
    import tensorflow as tf
    import tensorflow_datasets as tfds

    def load_dataset(args: dict[str, any]) -> tf.data.Dataset:
        """
        Load the dataset using TensorFlow Datasets.
        """
        if args.get("version", None):
            tfds.core.VERSION = args["version"]
            logger.info(f"Using TensorFlow Datasets version: {tfds.core.VERSION}")
        else:
            logger.info("Using the latest TensorFlow Datasets version.")

        # Set random seed for reproducibility
        tf.random.set_seed(args.get("seed", 1))

        builder = tfds.builder("na_dataset", version=args["version"])
        builder.download_and_prepare()
        # show dataset info
        info = builder.info
        logger.info("Dataset info: %s", info)
        data = builder.as_dataset(split=args["split"], shuffle_files=False)
        logger.info(f"Dataset split '{args['split']}' contains {len(data)} examples.")
        return info, data

    def eval_dataset(data: tf.data.Dataset) -> pd.DataFrame:
        """
        Evaluate the dataset by iterating through it and printing some examples.
        """
        record = []
        neighbors_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 15]
        for example in data:
            atoms_full = example["atoms"].numpy()

            for neighbor in neighbors_list:
                # Add 1 to contain the central atom
                num_atoms = NEIGHBOR_INFO_DICT[neighbor]["num_atoms_accumulated"] + 1
                if len(atoms_full) < num_atoms:
                    logger.error(
                        f"Not enough atoms in example: {len(atoms_full)} < {num_atoms}. Skipping."
                    )
                    sys.exit(1)
                atoms = atoms_full[:num_atoms]
                radius = np.linalg.norm(atoms[-1], axis=-1)
                record.append(
                    {
                        "num_atoms": num_atoms,
                        "radius": radius,
                        "temperature": example["temperature"].numpy(),
                        "label": example["label"].numpy(),
                    }
                )
        df = pd.DataFrame(record)
        logger.info("Evaluated DataFrame:\n%s", df)
        return df

    info, data = load_dataset(args)
    df = eval_dataset(data)
    return info, df


def plot_dataset(
    df: pd.DataFrame,
    *,
    phase: str,
    fig: go.Figure | None = None,
    colors: list = px.colors.qualitative.Plotly,
    update_layout: bool = True,
) -> go.Figure:
    """
    Plot the dataset using Plotly.
    """
    if fig is None:
        fig = go.Figure()
    df = df[df["label"] == PHASE_LABELS.index(phase)]
    grouped = df.groupby("num_atoms")
    for (num_atoms, group), color in zip(grouped, colors, strict=True):
        min_radius = group["radius"].min()
        avg_radius = group["radius"].mean()
        max_radius = group["radius"].max()

        fig.add_shape(
            type="rect",
            x0=min_radius,
            x1=max_radius,
            y0=0,
            y1=1,
            xref="x",
            yref="paper",
            opacity=0.2,
            fillcolor=color,
            line={"color": color, "width": 1},
        )
        fig.add_shape(
            type="line",
            x0=avg_radius,
            x1=avg_radius,
            y0=0,
            y1=1,
            xref="x",
            yref="paper",
            line={"color": color, "width": 2},
            name=f"{NEIGHBOR_TABLE_FCC[num_atoms]}",
            showlegend=True,
        )

    if update_layout:
        fig.update_layout(
            xaxis_title="Distance [Å]",
            legend_title="Number of Atoms",
            template="plotly_white",
            xaxis={
                "linecolor": "black",
                "linewidth": 1,
                "mirror": True,
                "range": [0, df["radius"].max() + 1],
            },
            yaxis={
                "linecolor": "black",
                "linewidth": 1,
                "mirror": True,
                "range": [0, 1],
            },
        )
    return fig


def main(args: dict[str, any]) -> pd.DataFrame:
    """Main function to run the TensorFlow Datasets tests."""

    info, df = load(args)

    filename = DATA_DIR / f"radius_v{info.version}.parquet"
    df.to_parquet(filename, index=False)
    logger.info("Evaluation results saved to '%s'.", filename)

    if args.get("show", False):
        fig = plot_dataset(df, phase="fcc")
        fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run TensorFlow Datasets tests.")

    # version is optional
    parser.add_argument(
        "--version",
        type=str,
        default=None,
        nargs="?",
        help="Dataset version to use (default: None, uses latest version)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1,
        help="Random seed for reproducibility (default: 1)",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        help="Dataset split to use (default: 'train')",
        choices=["train", "test"],
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the plot (default: False, saves to file)",
    )
    args = parser.parse_args()
    main(vars(args))
