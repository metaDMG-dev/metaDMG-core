# metaDMG: Estimating ancient damage in (meta)genomic DNA rapidly

---

#### Work in progress. Please contact christianmichelsen@gmail.com for further information.

---

You can now see a preview of the [interactive dashboard](https://metadmg.herokuapp.com).

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
or, with Poetry:
```
poetry add "metaDMG[all]"
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
  - `--names`: Path to the (NCBI) `names.dmp.gz`. Mandatory for LCA.
  - `--nodes`: Path to the (NCBI) `nodes.dmp.gz`. Mandator for LCA.
  - `--acc2tax`: Path to the (NCBI) `acc2tax.gz`. Mandatory for LCA.

- LCA parameters:
  - `--simscorelow`: Normalised edit distance (read to reference similarity) minimum. Number between 0-1. Default: 0.95.
  - `--simscorehigh`: Normalised edit distance (read to reference similarity) maximum. Number between 0-1 Default: 1.0.
  - `--editdistmin`: Minimum edit distance (read to reference similarity). Number between 0-10. Default: 0.
  - `--editdistmax`: Maximum edit distance (read to reference similarity). Number between 0-10. Default: 10.
  - `--minmapq`: Minimum mapping quality. Default: 0.
  - `--max-position`: Maximum position in the sequence to include. Default is (+/-) 15 (forward/reverse).
  - `--weighttype`: Method for calculating weights. Default is 1.
  - `--fix-ncbi`: Fix the (ncbi) database. Disable (0) if using a custom database. Default is 1.
  - `--lca-rank`: The LCA rank used in ngsLCA. Can be either `family`, `genus`, `species` or `""` (everything). Default is `""`.

- Non-LCA parameters:
  - `--damage-mode`: `[lca|local|global]`. `lca` is the recommended and automatic setting. If using `local`, it means that damage patterns will be calculated for each chr/scaffold contig. If using `global`, it means one global estimate. Note that when using `[local|global]` all of the parameters in the LCA section above won't matter, except `--max-position`.

- General parameters:
  - `--forward-only`: Only fit the forward strand.
  - `--storage-dir`: Path where the generated output files and folders are stored. Default: `./data/`.
  - `--cores`: The maximum number of cores to use. Default is 1.
  - `--cores-pr-fit`: Number of cores pr. fit. Do not change unless you know what you are doing.
  - `--sample-prefix`: Prefix for the sample names.
  - `--sample-suffix`: Suffix for the sample names.
  - `--config-path`: The name of the generated config file. Default: `config.yaml`.

- Boolean flags (does not take any values, only the flag). Default is false.
  - `--bayesian`: Include a fully Bayesian model (probably better, but also _a lot_ slower, about a factor of 100).
  - `--long-name`: Use the full, long, name for the sample.



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

To run metaDMG in non-LCA mode, an example could be:
```
$ metaDMG config ./raw_data/example.bam --damage-mode local --max-position 15 --bayesian
```

---


# `compute`


The `metaDMG compute` command takes an optional config-file as argument
(defaults to `config.yaml` if not specified).


#### CLI options:

- `--forced`: Forced computation (even though the files already exists). Bool flag.

#### Example:

```console
$ metaDMG compute
```

```console
$ metaDMG compute non-default-config.yaml --forced
```

---

# `dashboard`

You can now see a preview of the [interactive dashboard](https://metadmg.herokuapp.com).


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
$ metaDMG dashboard non-default-config.yaml --port 8050 --host 0.0.0.0
```

---

# Results

The column names in the results and their explanation:

- General parameters:
  - `tax_id`: The tax ID. int64.
  - `tax_name`: The tax name. string.
  - `tax_rank`: The tax rank. string.
  - `sample`: The name of the original sample. string.
  - `N_reads`: The number of reads. int64.
  - `N_alignments`: The number of alignments. int64.

- Fit related parameters:
  - `lambda_LR`: The likelihood ratio between the null model and the ancient damage model. This can be interpreted as the fit certainty, where higher values means higher certainty. float32.
  - `lambda_LR_P`: The likelihood ratio expressed as a probability. float32.
  - `lambda_LR_z`: The likelihood ratio expressed as number of ![](https://latex.codecogs.com/svg.image?%5Csigma). float32.
  - `D_max`: The estimated damage. This can be interpreted as the amount of damage in the specific taxa. float32.
  - `q`: The damage decay rate. float32.
  - `A`: The background independent damage. float32.
  - `c`: The background. float32.
  - `phi`: The concentration for a beta binomial distribution (parametrised by ![](https://latex.codecogs.com/svg.image?%5Cmu) and ![](https://latex.codecogs.com/svg.image?%5Cphi)). float32.
  - `rho_Ac`: The correlation between `A` and `c`. High values of this are often a sign of a bad fit. float32.
  - `valid`: Wether or not the fit is valid (defined by [iminuit](https://iminuit.readthedocs.io/en/stable/)). bool.
  - `asymmetry`: An estimate of the asymmetry of the forward and reverse fits. See below for more information. float32.
  - `XXX_std`: the uncertainty (standard deviation) of the variable `XXX` for `D_max`, `A`, `q`, `c`, and `phi`.
  - `forward__XXX`: The same description as above for variable `XXX`, but only for the forward read.
  - `reverse__XXX`: The same description as above for variable `XXX`, but only for the reverse read.

- Read related parameters
  - `mean_L`: The mean read length of all the individual, unique reads that map to the specific taxa. float64.
  - `std_L`: The standard deviation of the above. float64.
  - `mean_GC`: The mean GC content of all the individual, unique reads that map to the specific taxa. float64.
  - `std_GC`: The standard deviation of the above. float64.
  - `tax_path`: The taxanomic path from the LCA to the root through the phylogenetic tree. string.

- Count related paramters:
  - `N_x=1_forward`: The total number of _"trials"_, ![](https://latex.codecogs.com/svg.image?N), at position ![](https://latex.codecogs.com/svg.image?x=1): ![](https://latex.codecogs.com/svg.image?N(x=1)) in the forward direction. int64.
  - `N_x=1_reverse`:  Same as above, but for the reverse direction. int64.
  - `N_sum_forward`:  The sum of ![](https://latex.codecogs.com/svg.image?N) over all positions in the forward direction. int64.
  - `N_sum_reverse`: Same as above, but for the reverse direction. int64.
  - `N_sum_total`:  The total sum `N_sum_forward` and `N_sum_reverse`. int64.
  - `N_min`: The minimum of ![](https://latex.codecogs.com/svg.image?N) for all positions (forward and reverse alike). int64.
  - `k_sum_forward`:  The total number of _"successes"_, ![](https://latex.codecogs.com/svg.image?k), summed over all positions in the forward direction. int64.
  - `k_sum_reverse`: Same as above, but for the reverse direction. int64..
  - `k_sum_total`: The total sum `k_sum_forward` and `k_sum_reverse`. int64.
  - `k+i`: The number of _"successes"_, ![](https://latex.codecogs.com/svg.image?k) at position ![](https://latex.codecogs.com/svg.image?z=i): ![](https://latex.codecogs.com/svg.image?k(x=1)) in the forward direction. int64.
  - `k-i`: Same as above, but for the reverse direction. int64.
  - `N+i`: The number of _"trials"_, ![](https://latex.codecogs.com/svg.image?N) at position ![](https://latex.codecogs.com/svg.image?z=i): ![](https://latex.codecogs.com/svg.image?N(x=1)) in the forward direction. int64.
  - `N-i`: Same as above, but for the reverse direction. int64.
  - `f+i`: The fraction between ![](https://latex.codecogs.com/svg.image?k) and ![](https://latex.codecogs.com/svg.image?N) at position ![](https://latex.codecogs.com/svg.image?z=i) in the forward direction. int64.
  - `f-i`: Same as above, but for the reverse direction. int64.

---


# `plot`

The `metaDMG plot` command takes first an optional config-file as argument
(defaults to `config.yaml` if not specified) followed by the following CLI options:

#### CLI options:

- `--results-dir`: Direct path to the results directory.
- `--query`: The query string to use for filtering. Follows the [Pandas Query()]([www.link.dk](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#the-query-method)) syntax. Default is `""` which applies no filtering.
- `--samples`: A comma-space seperated string containing the samples to use in the plots. Default is `""` which applies no filtering.
- `--tax-ids`: A comma-space seperated string containing the tax-ids to use in the plots. Default is `""` which applies no filtering.
- `--pdf-out`: The path to the output pdf-file. Defaults to pdf_export.pdf.


#### Example:

```console
$ metaDMG plot
```


```console
$ metaDMG plot --query "100_000 <= N_reads & 8_000 <= phi" --tax-ids "1, 2, 42" --samples "sampleA, another-sample" --pdf-out name-of-plots.pdf
```

---

# `convert`

The `metaDMG convert` command takes first an optional config-file as argument
(defaults to `config.yaml` if not specified) used to infer the results directory
 followed by the following CLI options:

#### CLI options:

- `--output`: Mandatory output path.
- `--results-dir`: Direct path to the results directory.
- `--add-fit-predictions`: Include fit predictions D(x) in the output.

Note that neither the config-file nor `--results-dir` have to be specified
(in which just the default `config.yaml` is used), however,
both cannot be set at the same time.

#### Example:

```console
$ metaDMG convert --output ./directory/to/contain/results.csv
```

```console
$ metaDMG convert non-default-config.yaml --output ./directory/to/contain/results.csv --add-fit-predictions
```

---

# `filter`

The `metaDMG filter` command takes first an optional config-file as argument
(defaults to `config.yaml` if not specified) used to infer the results directory
 followed by the following CLI options:

#### CLI options:

- `--output`: Mandatory output path.
- `--query`: The query string to use for filtering. Follows the [Pandas Query()]([www.link.dk](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#the-query-method)) syntax.
Default is `""` which applies no filtering and is thus similar to the `metaDMG convert` command.
- `--results-dir`: Direct path to the results directory.
- `--add-fit-predictions`: Include fit predictions D(x) in the output.

Note that neither the config-file nor `--results-dir` have to be specified
(in which just the default `config.yaml` is used), however,
both cannot be set at the same time.



#### Example:

```console
$ metaDMG filter --output convert-no-query.csv # similar to metaDMG convert
```

```console
$ metaDMG filter --output convert-test.csv --query "N_reads > 5_000 & sample in ['subs', 'SPL_195_9299'] & tax_name == 'root'" --add-fit-predictions
```

---

# `mismatch-to-mapDamage`

The `metaDMG mismatch-to-mapDamage` command takes a mandatory mismatch-file as argument
and converts it to the mapDamage format `misincorporation.txt`.

#### CLI options:

- `--csv-out`: Output CSV file (misincorporation.txt). Default is `misincorporation.txt`.

#### Example:

```console
$ metaDMG mismatch-to-mapDamage data/mismatches/XXX.mismatches.parquet
```
```console
$ metaDMG mismatch-to-mapDamage data/mismatches/XXX.mismatches.parquet --csv-out misincorporation.txt
```

---
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

---
---

## Updating metaDMG


With pip or Conda:
```console
pip install "metaDMG[all]"  --upgrade
```

With Poetry:
```console
poetry add metaDMG["all"]
```
<!-- poetry add metaDMG-viz@latest -->