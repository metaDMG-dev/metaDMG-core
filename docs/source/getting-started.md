# Getting started

These sections explains very briefly the [requirements](requirements) of `metaDMG` and how to [install](installation) it, and sketches how a typical [workflow](workflow) is organized.

(requirements)=
## Requirements

`metaDMG` is a quite complex piece of software with many dependencies. This is due to it running the LCA in fast C++ code, the fits in optimized Python (with the use of `numba` and `jax`, e.g.), and finally the visualisations of the results in the interactive dashboard.
To make the installation requirements as lean as possible, we allow for custom installation of the different parts of `metaDMG`.

```{note} If you install using the Conda package, you do not have to worry about any of the things in this section and you can skip straight to the [installation section](installation).
```

The C++ requirements for [`metaDMG-cpp`](https://github.com/metaDMG-dev/metaDMG-cpp) are only needed in case you have to compile it yourself - Conda takes care of this for you automatically.
In case you want to compile it yourself, the dependencies are:
- `HTSlib`
- `blas`
- `gsl`
- `eigen`

For more information about `metaDMG-cpp`, see the [`repo`](https://github.com/metaDMG-dev/metaDMG-cpp).

The main part of `metaDMG`, [`metaDMG-core`](https://github.com/metaDMG-dev/metaDMG-core), is writting in Python (version `Python >= 3.9`).

For `metaDMG-core`, the basic dependencies are:
- `typer`
- `click-help-colors`
- `pyyaml`
- `pandas`
- `scipy`
- `pyarrow`

The fit related (`[fit]`) dependencies are:
- `iminuit`
- `numba`
- `numpyro`
- `logger-tt`
- `joblib`
- `psutil`

The visualization related (`[viz]`) dependencies are:
- `matplotlib`
- `plotly`
- `dash`
- `dash-bootstrap-components`
- `orjson`
- `tqdm`


And the GUI related (`[gui]`) dependencies are:
- `customtkinter`

In general, we allow for the custom installion of only the core packages `pip install metaDMG`, core + fit related packages: `pip install "metaDMG[fit]"`, core + visualization related packages: `pip install "metaDMG[viz]"` or core + fit + viz + gui: `pip install "metaDMG[all]"`.

```{warning} metaDMG is not tested on Windows.
```

(installation)=
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

```{note} This is the recommended way of installing metaDMG.
```


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

(workflow)=
## Workflow

Here we sketch how a typical workflow works in `metaDMG`. In short:

1. Create `config` file
2. Compute the LCA and fits
3. Visualize the results

### Create the config file

`metaDMG` works by first creating a config file using the `config` command. This file contains all of the information related to `metaDMG` such that you only have to type this once. The config file is saved in the current directory as `config.yaml` and can subsequently be edited in any text editor of your like.

```console
$ metaDMG config raw_data/alignment.sorted.bam \
    --names raw_data/names-mdmg.dmp \
    --nodes raw_data/nodes-mdmg.dmp \
    --acc2tax raw_data/acc2taxid.map.gz \
    --custom-database
```

If you prefer a more visual approach, the same can also be done using the `config-gui` command:

```console
$ metaDMG config-gui
```

### Run the computation

After the config has been created, we run the actual program using the `compute` command. This can take a while depending on the number (and size) of the files.

```console
$ metaDMG compute config.yaml
```

### Dashboard

The results are saved in `{output-dir}/results` directory (`data/results` by default). These can be viewed with the interactive dashboard using the `dashboard` command.

```console
$ metaDMG dashboard
```
