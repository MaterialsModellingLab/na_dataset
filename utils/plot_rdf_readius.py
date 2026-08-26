#!/usr/bin/env python3
# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

import argparse
import logging
import sys

import pandas as pd
import plotly.io as pio
from common import DATA_DIR, IMAGE_DIR
from eval_radius import plot_dataset
from eval_rdf import plot_rdf

from na_dataset_util import PHASE_LABELS

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
handler.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
logger.propagate = False

pio.renderers.default = "browser"


def main(
    save: bool = True, show: bool = False, width: int = 600, height: int = 800
) -> None:
    """
    Main function to plot evaluation results for a specific phase.

    Args:
        save (bool): Whether to save the plots as PDF files.
        show (bool): Whether to show the plots in a browser.
        width (int): Width of the plot.
        height (int): Height of the plot.
    """

    # Load dataset_v{version}.parquet file
    eval_dataset_files = list(DATA_DIR.glob("radius_v*.parquet"))
    if not eval_dataset_files:
        logger.error("No evaluation radius files found in DATA_DIR.")
        logger.error("Did you execute 'eval_radius.py'?")
        sys.exit(1)
    # If multiple files, take the latest one (just sort by name)
    eval_dataset_file = max(eval_dataset_files, key=lambda x: x.name)
    logger.info("Loading evaluation dataset from %s", eval_dataset_file)
    ds_df = pd.read_parquet(eval_dataset_file)

    rdf_df = pd.read_parquet(DATA_DIR / "rdf.parquet")

    for phase in PHASE_LABELS:
        logger.info("%s RDF info:\n%s", phase.capitalize(), rdf_df)
        fig = plot_dataset(ds_df, phase=phase, update_layout=False)
        fig = plot_rdf(rdf_df, fig=fig, phase=phase, update_layout=True)
        fig.update_layout(legend_title="Model Size")
        if save:
            filename = IMAGE_DIR / f"rdf_dataset_{phase}.pdf"
            fig.write_image(filename, width=width, height=height)
            logger.info("RDF plot for %s saved to '%s'.", phase.capitalize(), filename)
        if show:
            fig.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot evaluation results.")
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the plots in a browser (default: False)",
    )

    args = parser.parse_args()
    main(**vars(args))
