# Getting started

These sections explains very briefly the dependencies of `metaDMG` and how to install it, and sketches how a typical workflow is organized.

## Requirements

`metaDMG` is a quite complex piece of software with many dependencies. This is due to it both running the LCA in some fast C++ code, the fits are optimized (with the use of `numba` and `jax`, e.g.) and finally it allows for visualisations of the results in the interactive dashboard.
To make the installation requirements as lean as possible, we allow for custom installation of the different parts of `metaDMG`.

If you install using the Conda package, you do not have to worry about any of the things in this section and you can skip straight to the installation section XXX LINK HERE.

The C++ requirements are only needed in case you have to compile it yourself - Conda takes care of this for you automatically.
In case you want to work on the master branch directly, the dependencies are:
- `HTSlib`
- `blas`
- `gsl`
- `eigen`

In Python, the core dependencies are:
- `typer`
- `click-help-colors`
- `pyyaml`
- `pandas`
- `scipy`
- `pyarrow`

The fit-related dependencies are `[fit]`:
- `iminuit`
- `numba`
- `numpyro`
- `logger-tt`
- `joblib`
- `psutil`

And the visualization related dependencies are `[viz]`:
- `matplotlib`
- `plotly`
- `dash`
- `dash-bootstrap-components`
- `orjson`
- `tqdm`

In general, we allow for the custom installion of only the core packages `pip install metaDMG`, core + fit related packages: `pip install "metaDMG[fit]"`, core + visualization related packages: `pip install "metaDMG[viz]"` or core + fit + viz: `pip install "metaDMG[all]"`.

## Installation

The recommended way of installing `metaDMG` is by using Conda. By default, we install everything needed to run all of `metaDMG`'s commands.

### With Conda

To create a new, fresh environment with everything `metaDMG` requires:
```bash
conda env create --file environment.yaml
```
or, if you have Mamba installed (faster)
```
mamba env create --file environment.yaml
```
This is the recommended way of installing `metaDMG`.

### With pip
If you prefer to use pip, you can use:
```
pip install "metaDMG[all]"
```
<!-- ### With poetry
```
poetry add "metaDMG[all]"
``` -->

<!-- ### Updating

With pip or Conda:
```console
pip install "metaDMG[all]"  --upgrade
``` -->

<!-- With Poetry:
```console
poetry add metaDMG["all"]
``` -->

## Workflow

Here we sketch how a typical workflow works in `metaDMG`. In short:

1. Create `config` file
2. Compute the LCA and fits
3. Visualize the results

### Create the config file

`metaDMG` works by first creating a config file using the `config` command. This file contains all of the information related to `metaDMG` such that you only have to type this once. The config file is saved in the current directory as `config.yaml` and can subsequently be edited in any text editor of your like.

```console
$ metaDMG config ./raw_data/alignment.bam \
    --names raw_data/names-mdmg.dmp \
    --nodes raw_data/nodes-mdmg.dmp \
    --acc2tax raw_data/acc2taxid.map.gz
```

### Run the computation

After the config has been created, we run the actual program using the `compute` command. This can take a while depending on the number (and size) of the files.

```console
$ metaDMG compute
```

### Dashboard

The results are saved in `{output-dir}/results` directory (`data/results` by default). These can be viewed with the interactive dashboard using the `dashboard` command.

```console
$ metaDMG dashboard
```
