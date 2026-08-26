"""
NaDataset Builder
"""

from pathlib import Path
from typing import ClassVar

import numpy as np
import tensorflow_datasets as tfds
from etils import epath

import na_dataset_util as nads_util


class Builder(tfds.core.GeneratorBasedBuilder):
    """DatasetBuilder for na_dataset dataset."""

    VERSION = "0.0.0"
    pkg_dir_path = epath.Path(__file__).resolve().parent

    RELEASE_NOTES: ClassVar[dict[str, str]] = {
        "0.0.0": "Initial release.",
    }

    def _info(self) -> tfds.core.DatasetInfo:
        """Returns the dataset metadata."""
        return self.dataset_info_from_configs(
            features=tfds.features.FeaturesDict(
                {
                    # These are the features of your dataset like images, labels ...
                    "atoms": tfds.features.Tensor(
                        shape=(nads_util.DEFAULT_NUM_ATOMS, 3), dtype=np.float32
                    ),
                    "label": tfds.features.ClassLabel(names=nads_util.PHASE_LABELS),
                    "temperature": tfds.features.Scalar(dtype=np.float32),
                }
            ),
            homepage=None,
            supervised_keys=None,
        )

    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        """Returns SplitGenerators."""
        extract_paths = dl_manager.download_and_extract(
            "file://" + str(Path(__file__).parent / f"na_dataset.{self.VERSION}.zip")
        )

        return {
            "train": self._generate_examples(extract_paths / "train.txt"),
            "test": self._generate_examples(extract_paths / "test.txt"),
        }

    def _generate_examples(self, path: Path):
        """Yields examples."""
        import tensorflow as tf

        with tf.io.gfile.GFile(path, "r") as f:
            for line in f:
                filename = Path(line.strip())
                with tf.io.gfile.GFile(path.parent / filename, "rb") as gf:
                    idx = filename.stem
                    data = np.load(gf)
                    yield (
                        idx,
                        {
                            "atoms": data["atoms"],
                            "label": str(data["label"]),
                            "temperature": data["temperature"],
                        },
                    )
