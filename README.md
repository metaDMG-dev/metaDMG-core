# metaDMG: Estimating ancient damage in (meta)genomic DNA rapidly

---

#### Work in progress. Please contact christianmichelsen@gmail.com for further information.

---


## Installation:

```
conda env create --file environment.yaml
```
or, if you have mamba installed (faster)
```
mamba env create --file environment.yaml
```

or, by using pip:
```
pip install "metaDMG[all]"
```
---

## Workflow:


Create `config.yaml` file:
```console
$ metaDMG config ./raw_data/example.bam \
    --names raw_data/names.dmp.gz \
    --nodes raw_data/nodes.dmp.gz \
    --acc2tax raw_data/combined_taxid_accssionNO_20200425.gz
```
Run actual program:
```console
$ metaDMG compute
```
See the results in the dashboard:
```console
$ metaDMG dashboard
```


---

## Usage:

metaDMG works by first creating a config file using the `config` command. This file contains all of the information related to metaDMG such that you only have to type this once. The config file is saved in the current directory as `config.yaml` and can subsequently be edited in any text editor of your like.

After the config has been created, we run the actual program using the `compute` command. This can take a while depending on the number (and size) of the files.

Finally the results are saved in `{storage-dir}/results` directory (`data/results` by default). These can be viewed with the interactive dashboard using the `dashboard` command.


---

# `config`

#### CLI options:

`metaDMG config` takes a single argument, `samples`, and a bunch of additional options. The `samples` refer to a single or multiple alignment-files (or a directory containing them), all with the file extensions: `.bam`, `.sam`, and `.sam.gz`.

The options are listed below:

- Input files:
  - `--names`: Path to the (NCBI) `names.dmp.gz`. Mandatory.
  - `--nodes`: Path to the (NCBI) `nodes.dmp.gz`. Mandatory.
  - `--acc2tax`: Path to the (NCBI) `acc2tax.gz`. Mandatory.

- LCA parameters:
  - `--simscorelow`: Normalized edit distance (read to reference similarity) minimum. Number between 0-1. Default: 0.95.
  - `--simscorehigh`: Normalized edit distance (read to reference similarity) maximum. Number between 0-1 Default: 1.0.
  - `--editdistmin`: Minimum edit distance (read to reference similarity). Number between 0-10. Default: 0.
  - `--editdistmax`: Maximum edit distance (read to reference similarity). Number between 0-10. Default: 10.
  - `--minmapq`: Minimum mapping quality. Default: 0.
  - `--max-position`: Maximum position in the sequence to include. Default is (+/-) 15 (forward/reverse).
  - `--lca-rank`: The LCA rank used in ngsLCA. Can be either `family`, `genus`, `species` or `""` (everything). Default is `""`.

- General parameters:
  - `--storage_dir`: Path where the generated output files and folders are stored. Default: `./data/`.
  - `--cores`: The maximum number of cores to use. Default is 1.
  - `--config-file`: The name of the generated config file. Default: `config.yaml`.

- Boolean flags (does not take any values, only the flag). Default is false.
  - `--bayesian`: Include a fully Bayesian model (probably better, but also _a lot_ slower, about a factor of 100).



```console
$ metaDMG config ./raw_data/example.bam \
    --names raw_data/names.dmp.gz \
    --nodes raw_data/nodes.dmp.gz \
    --acc2tax raw_data/combined_taxid_accssionNO_20200425.gz \
    --cores 4
```


metaDMG is pretty versatile regarding its input argument and also accepts multiple alignment files:
```console
$ metaDMG config ./raw_data/*.bam [...]
```
or even an entire directory containing alignment files (`.bam`, `.sam`, and `.sam.gz`):
```console
$ metaDMG config ./raw_data/ [...]
```

---


# `compute`


The `metaDMG compute` command takes an optional config-file as argument
(defaults to `config.yaml` if not specified).

#### Example:

```console
$ metaDMG compute
```

```console
$ metaDMG compute config.yaml
```

---

# `dashboard`


The `metaDMG dashboard` command takes first an optional config-file as argument
(defaults to `config.yaml` if not specified) followed by the following CLI options:

#### CLI options:

- `--port`: The port to be used for the dashboard. Default is `8050`.
- `--host`: The dashboard host adress. Default is `0.0.0.0`.
- `--debug`: Boolean flag that allows for debugging the dashboard. Only for internal usage.

#### Example:

```console
$ metaDMG dashboard
```

```console
$ metaDMG dashboard config.yaml --port 8050 --host 0.0.0.0
```


---

# `convert`

The `metaDMG convert` command takes first an optional config-file as argument
(defaults to `config.yaml` if not specified) used to infer the results directory
 followed by the following CLI options:

#### CLI options:

- `--output`: Mandatory output path.
- `--results_dir`: Direct path to the results directory.

Note that neither the config-file nor `--results_dir` have to be specified
(in which just the default `config.yaml` is used), however,
both cannot be set at the same time.

#### Example:

```console
$ metaDMG convert --output ./directory/to/contain/results.csv
```

```console
$ metaDMG convert config.yaml --output ./directory/to/contain/results.csv
```

---

If you only want to install some of the tools, you can run:
```console
pip install "metaDMG[fit]"
```
to only install the fitting part of the tool, or:
```console
pip install "metaDMG[viz]"
```
to only install the interactive plotting tool (requires you to have gotten the results from somewhere else).