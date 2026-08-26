#!/usr/bin/env python3
# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

"""
This module contains functions to plot the results of the analysis.

Usage:
./plot_thermo.py <input-file0> <input-file1> ... <input-fileN>
"""

import argparse
import logging
import pathlib
import re
import sys

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import yaml
from common import IMAGE_DIR, LAMMPS_OUTPUT_DIR
from plotly.subplots import make_subplots

try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
handler.setLevel(logging.INFO)
logger.propagate = False

pio.renderers.default = "browser"


def load_thermo(base_path: pathlib.Path) -> pd.DataFrame | None:
    """
    Load thermo data from the specified base path.

    Args:
        base_path (pathlib.Path): Base directory containing LAMMPS log files.

    Returns:
        pd.DataFrame: DataFrame containing the thermo data.
    """
    if not base_path.is_dir():
        logger.error(f"Base path {base_path} is not a directory.")
        sys.exit(1)

    # Find log files in the base directory
    log_files = list(base_path.rglob("log.*K"))
    log_files = [f for f in log_files if re.match(r"log\.(\d+)K", f.name)]
    if not log_files:
        logger.error("No log files found in the specified directory.")
        sys.exit(1)

    def load_thermo_file(log_file: pathlib.Path) -> list[dict]:
        """
        Load thermo data from a single log file.
        """
        logger.info(f"Processing {log_file}")
        docs = ""
        with open(log_file, encoding="utf-8") as f:
            for line in f:
                m = re.search(r"^(keywords:.*$|data:$|---$|\.\.\.$|  - \[.*\]$)", line)
                if m:
                    docs += m.group(0) + "\n"

        thermo = list(yaml.load_all(docs, Loader=Loader))
        if not thermo:
            logger.error(f"No thermo data found in {log_file}.")
            return None
        df = pd.DataFrame(
            [row for entry in thermo if "data" in entry for row in entry["data"]],
            columns=thermo[0]["keywords"],
        )
        logger.info("%s", df)
        return df

    thermo_df = pd.DataFrame()
    for log_file in log_files:
        phase = log_file.parent.name
        target_temperature = float(log_file.name.split(".")[1].replace("K", ""))
        logger.info("Phase %s at %sK", phase, target_temperature)
        df = load_thermo_file(log_file)
        if df is None:
            continue
        df["phase"] = phase
        df["target_temperature"] = target_temperature
        thermo_df = pd.concat([thermo_df, df], ignore_index=True)

    return thermo_df


def plot_thermo(df: pd.DataFrame) -> list[dict[go.Figure, str]]:
    """
    Plot the thermo data from the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing the thermo data.

    Returns:
        list[dict[go.Figure, str]]: List of dictionaries containing the figures and their base names.
    """
    if df.empty:
        logger.error("DataFrame is empty. Cannot plot.")
        return []

    # Group by phase and target temperature
    grouped = df.groupby(["phase", "target_temperature"])
    figs = []
    for (phase, target_temperature), group in grouped:
        logger.info("Plotting phase %s at %sK", phase, target_temperature)
        # Make 2 plots vertically stacked
        # 1: Time vs Temperature
        # 2: Time vs Energy
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=(
                "Temperature vs Time",
                "Energy vs Time",
            ),
            vertical_spacing=0.1,
        )
        fig.add_trace(
            go.Scatter(
                x=group["Time"],
                y=group["Temp"],
                mode="lines",
                name="Temperature",
                legendgroup=1,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=group["Time"],
                y=group["PotEng"],
                mode="lines",
                name="Potential Energy",
                legendgroup=2,
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=group["Time"],
                y=group["KinEng"],
                mode="lines",
                name="Kinetic Energy",
                legendgroup=2,
            ),
            row=2,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=group["Time"],
                y=group["TotEng"],
                mode="lines",
                name="Total Energy",
                legendgroup=2,
            ),
            row=2,
            col=1,
        )
        fig.update_layout(
            title=f"Thermo Data for Phase: {phase.upper()}, Target Temperature: {target_temperature}K",
            xaxis={
                "linecolor": "black",
                "linewidth": 1,
                "mirror": True,
            },
            yaxis={
                "linecolor": "black",
                "linewidth": 1,
                "mirror": True,
                "title": "Temperature (K)",
            },
            xaxis2={
                "linecolor": "black",
                "linewidth": 1,
                "mirror": True,
                "title": "Time (fs)",
            },
            yaxis2={
                "linecolor": "black",
                "linewidth": 1,
                "mirror": True,
                "title": "Energy (eV)",
            },
            legend_tracegroupgap=320,
            height=800,
            template="plotly_white",
        )
        figs.append(
            {
                "fig": fig,
                "basename": f"thermo_{phase.lower()}_{int(target_temperature)}K",
            }
        )

    return figs


def main(base_path: str, show: bool = False) -> None:
    """
    Main function to parse arguments and call the plot function.
    """
    base_path = pathlib.Path(base_path)
    df = load_thermo(base_path)
    if df is None or df.empty:
        logger.error("No thermo data found.")
        sys.exit(1)

    figs_info = plot_thermo(df)
    for fig_info in figs_info:
        fig = fig_info["fig"]
        basename = fig_info["basename"]

        filename = f"{IMAGE_DIR}/{basename}.html"
        logger.info("Saving figure to %s", filename)
        fig.write_html(filename)
        if show:
            fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot data from a file.")
    parser.add_argument(
        "--base_path",
        type=str,
        help="Base directory containing LAMMPS log files.",
        default=None,
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the plot in the browser.",
    )
    args = parser.parse_args()
    main(base_path=args.base_path or LAMMPS_OUTPUT_DIR, show=args.show)
