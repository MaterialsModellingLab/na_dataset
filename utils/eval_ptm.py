#!/usr/bin/env python3
# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

import argparse
import logging
import pathlib
import re
import sys

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from common import DATA_DIR, LAMMPS_OUTPUT_DIR

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
handler.setLevel(logging.INFO)
logger.propagate = False

pio.renderers.default = "browser"


def load_yaml(input: str, no_cache: bool = False) -> dict:
    """
    Load a YAML file and return its contents.
    Args:
        input (str): Path to the YAML file.
    Returns:
        dict: Contents of the YAML file.
    Raises:
        ValueError: If the file cannot be read or parsed.
    """
    input = pathlib.Path(input)
    if not input.is_file():
        raise ValueError(f"{input} is not a valid file.")

    input_json = input.with_suffix(".json")
    if input_json.is_file() and not no_cache:
        import json

        logger.info(f"Loading cached JSON file {input_json}")
        with open(input_json) as f:
            return json.load(f)

    logger.warning(f"Parsing YAML file {input} may take some time.")
    with open(input) as f:
        import yaml

        data = yaml.load(f, Loader=yaml.CSafeLoader)
    if not data:
        raise ValueError(f"No data found in {input}.")
    with open(input_json, "w") as f:
        import json

        json.dump(data, f)
        logger.info(f"Cached JSON file saved to {input_json}")
    return data


def load_ptm_data(base_path: str, no_cache: bool = False) -> pd.DataFrame:
    """
    Load PTM data from a file and return it as a DataFrame.

    Args:
        base_path (str): Path to the directory containing PTM data files.
    Returns:
        pd.DataFrame: DataFrame containing the PTM data.
    Raises:
        ValueError: If no PTM files are found or if filenames do not match expected pattern
    """
    base_path = pathlib.Path(base_path)
    if not base_path.is_dir():
        raise ValueError(f"Base path {base_path} is not a directory.")

    ptm_files = list(base_path.rglob("ptm*.yaml"))
    if not ptm_files:
        raise ValueError(f"No PTM files found in {base_path}.")

    df = pd.DataFrame()
    for ptm_file in ptm_files:
        logger.info(f"Processing {ptm_file}...")
        match = re.match(r"ptm(\d+)K\.yaml", ptm_file.name)
        if not match:
            raise ValueError(
                f"Filename {ptm_file.name} does not match expected pattern."
            )
        temperature = float(match.group(1))
        data = load_yaml(ptm_file, no_cache=no_cache)

        header = data["keywords"]
        body = data["data"]

        values = pd.DataFrame(body, columns=header)["c_ptm[1]"].values.ravel()
        ratio = pd.Series(values).value_counts(normalize=True)
        df_local = ratio.to_frame().T.reset_index(drop=True)
        df_local["temperature"] = temperature
        df_local["phase"] = ptm_file.parent.name.upper()
        df = pd.concat([df, df_local], sort=True).fillna(0.0).reset_index(drop=True)

    PHASE_DICT = {
        "LIQUID": 0,
        "FCC": 1,
        "HCP": 2,
        "BCC": 3,
        "ICO": 4,
        "SC": 5,
        "DCUB": 6,
        "DHEX": 7,
        "GRAPHENE": 8,
    }
    acc = df.apply(
        lambda row: row[PHASE_DICT[row["phase"]]],
        axis=1,
    )
    df["accuracy"] = acc
    df["model_name"] = "PTM"
    df = df[["temperature", "phase", "model_name", "accuracy"]]
    return df


def plot_ptm(
    df: pd.DataFrame, *, fig: go.Figure | None = None, update_layout: bool = True
) -> go.Figure:
    """
    Plot the PTM data from the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing the PTM data.

    Returns:
        go.Figure: Plotly figure object.
    """
    if fig is None:
        fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["temperature"],
            y=df["accuracy"],
            mode="markers+lines",
            name="PTM",
        )
    )

    if update_layout:
        fig.update_layout(
            title="PTM Phase Fractions vs Temperature",
            xaxis_title="Temperature (K)",
            yaxis_title="Fraction of Phase",
            yaxis={"range": [0.8, 1.05]},
            xaxis={"range": [df["temperature"].min(), df["temperature"].max()]},
        )

    return fig


def main(base_path: str, show: bool = False, no_cache: bool = False) -> None:
    """
    Main function to load PTM data and plot it.
    Args:
        base_path (str): Path to the directory containing PTM data files.
        show (bool): Whether to display the plot in a browser.
    """
    ptm_df = load_ptm_data(base_path)

    filename = DATA_DIR / "ptm_eval.parquet"
    ptm_df.to_parquet(filename, index=False)
    logger.info("PTM results saved to '%s'.", filename)

    if show:
        fig = plot_ptm(ptm_df)
        fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate PTM data and plot results.")
    parser.add_argument(
        "--base_path",
        type=str,
        help="Path to the directory containing PTM data files.",
        default=None,
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the plot in a browser.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Do not use cached JSON files when loading YAML data.",
    )
    args = parser.parse_args()
    main(
        base_path=args.base_path or LAMMPS_OUTPUT_DIR,
        show=args.show,
        no_cache=args.no_cache,
    )
