#!/usr/bin/env python3
# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

import argparse
import logging
import pathlib
import re
import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from common import DATA_DIR, LAMMPS_OUTPUT_DIR

from na_dataset_util.const import PHASE_LABELS

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
handler.setLevel(logging.INFO)
logger.propagate = False

pio.renderers.default = "browser"


def load_rdf_data(base_path: pathlib.Path) -> pd.DataFrame:
    """
    Load RDF data from a file and return it as a DataFrame.

    Args:
        file_path (pathlib.Path): Path to the RDF data file.

    Returns:
        pd.DataFrame: DataFrame containing the RDF data.
    """
    if not base_path.is_dir():
        logger.error(f"Base path {base_path} is not a directory.")
        sys.exit(1)

    # Find data.{temperature}K files in the base directory
    data_files = list(base_path.rglob("rdf*K.txt"))
    if not data_files:
        logger.error("No data files found in the specified directory.")
        logger.error("Did you execute 'make rdf' in lammps directory?")
        sys.exit(1)

    rdf_list = []

    for data_file in data_files:
        match = re.match(r"rdf(\d+)K\.txt", data_file.name)
        if not match:
            logger.error(f"Filename {data_file.name} does not match expected pattern.")
            sys.exit(1)
        phase = data_file.parent.name
        if phase not in PHASE_LABELS:
            logger.error(f"Invalid phase label: {phase} not in {PHASE_LABELS}")
            sys.exit(1)
        temperature = float(match.group(1))
        rdf = np.loadtxt(data_file, comments="#", skiprows=4)
        logger.info(f"Processing {data_file} at {temperature}K")
        _idx, x, g_r, pair_count = rdf.T

        for x_i, g_r_i, pair_count_i in zip(x, g_r, pair_count, strict=True):
            rdf_list.append(
                {
                    "x": x_i,
                    "g_r": g_r_i,
                    "pair_count": pair_count_i,
                    "temperature": temperature,
                    "phase": phase,
                }
            )

    # Convert the dictionary to a DataFrame for easier manipulation
    rdf_df = pd.DataFrame.from_dict(rdf_list)
    return rdf_df


def plot_rdf(
    df: pd.DataFrame,
    *,
    phase: str,
    fig: go.Figure | None = None,
    update_layout: bool = True,
) -> go.Figure:
    """
    Plot the RDF data from the DataFrame.

    Args:
        rdf_df (pd.DataFrame): DataFrame containing the RDF data.

    Returns:
        go.Figure: Plotly figure object.
    """
    rdf_df = df[df["phase"] == phase]
    rdf_df_sorted = rdf_df.sort_values("temperature")
    unique_temps = rdf_df_sorted["temperature"].unique()

    if fig is None:
        fig = go.Figure()
    offset_step = 1.5

    for i, temp in enumerate(unique_temps):
        temp_df = rdf_df_sorted[rdf_df_sorted["temperature"] == temp]
        temp_df = temp_df.sort_values("x")

        x = temp_df["x"]
        y = temp_df["g_r"] + i * offset_step

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name=f"{temp} K",
                showlegend=False,
                line={"color": "black"},
            )
        )

        fig.add_annotation(
            x=0,
            y=y.iloc[0],
            text=f"{temp} K",
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
        )

    if update_layout:
        fig.update_layout(
            xaxis_title="Distance (Å)",
            yaxis_title="Radial Distribution Function [arbitrary units]",
            template="plotly_white",
            xaxis={
                "linecolor": "black",
                "linewidth": 1,
                "mirror": True,
                "range": [0, round(rdf_df_sorted["x"].max())],
            },
            yaxis={
                "linecolor": "black",
                "linewidth": 1,
                "mirror": True,
                "showticklabels": False,
            },
        )
    return fig


def main(base_path: str, show: bool = False):
    """
    Main function to read RDF data files, process them, and plot the results.
    """
    base_path = pathlib.Path(base_path)
    rdf_df = load_rdf_data(base_path)
    logger.info("RDF: \n%s", rdf_df)

    filename = DATA_DIR / "rdf.parquet"
    rdf_df.to_parquet(filename, index=False)
    logger.info("RDF data saved to %s", filename)

    if show:
        # Grouped by phase
        figs = []
        for phase in PHASE_LABELS:
            fig = plot_rdf(rdf_df, phase=phase)
            figs.append((phase, fig))

        for _, fig in figs:
            fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate RDF from LAMMPS data files."
    )
    parser.add_argument(
        "--base_path",
        type=str,
        help="Base directory containing LAMMPS data files.",
        default=None,
    )
    parser.add_argument(
        "--show", action="store_true", help="Show the plot in the browser."
    )
    args = parser.parse_args()
    main(base_path=args.base_path or LAMMPS_OUTPUT_DIR, show=args.show)
