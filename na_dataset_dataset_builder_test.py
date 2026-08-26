"""na_dataset dataset."""

from typing import ClassVar

import tensorflow_datasets as tfds

from na_dataset_dataset_builder import Builder


class NaDatasetTest(tfds.testing.DatasetBuilderTestCase):
    """Tests for na_dataset dataset."""

    DATASET_CLASS = Builder
    # DATASET_CLASS = na_dataset_dataset_builder.Builder
    SPLITS: ClassVar[dict[str, int]] = {
        "train": 3,  # Number of fake train example
        "test": 1,  # Number of fake test example
    }

    # If you are calling `download/download_and_extract` with a dict, like:
    #   dl_manager.download({'some_key': 'http://a.org/out.txt', ...})
    # then the tests needs to provide the fake output paths relative to the
    # fake data directory
    # DL_EXTRACT_RESULT = {'some_key': 'output_file1.txt', ...}
    DL_EXTRACT_RESULT = "data"

    SKIP_CHECKSUMS = True  # Skip checksum checking for the fake data


if __name__ == "__main__":
    tfds.testing.test_main()
