# Neighbor Atoms Dataset

The Neighbor Atoms Dataset is a collection of molecular structures and their corresponding neighbor atom information.
It is designed to facilitate research in molecular modeling, machine learning, and computational chemistry.

## Dataset generation procedure
Before building the dataset, please install LAMMPS and TensorFlow Datasets (TFDS).

For LAMMPS installation, please refer to the [official LAMMPS documentation](https://docs.lammps.org/Build.html) and make sure  `lmp` executable is available in your PATH.
For building LAMMPS, you can use the following command at the root directory of lammps source code:
```bash
cmake ./cmake -G Ninja -B build \
  -D CMAKE_BUILD_TYPE=Release \
  -D BUILD_MPI=yes \
  -D PKG_KOKKOS=yes \
  -D PKG_EXTRA-DUMP=yes \
  -D PKG_MANYBODY=yes \
  -D PKG_PTM=yes \
  -D Kokkos_ARCH_<HOSTARCH>=yes \
  -D Kokkos_ARCH_<GPUARCH>=yes \
  -D Kokkos_ENABLE_CUDA=yes \
  -D Kokkos_ENABLE_OPENMP=yes \
cmake --build build
cmake --install build
```

The `<HOSTARCH>` and `<GPUARCH>` should be replaced with your host and GPU architecture, respectively.
The available architectures can be found in the [Lammps Kokkos documentation](https://docs.lammps.org/Build_extras.html#available-architecture-settings).


For TFDS installation, you can use pip:
```bash
pip install -U .[build]
```

### Step 1. Run LAMMPS to generate a trajectory file of a molecular system.
This command will generate a trajectory files into `lammps/output` directory.
```bash
make -f ./lammps/Makefile
```

### Step 2. Generate npz files
This command will generate npz files into `na_dataset.${__version__}` directory.
```bash
./generate_data.py lammps/output/
```

### Step 3. Build tfds
```bash
tfds build .
```
