(command_line_interface)=
# Command Line Interface

`metaDMG` has the following commands:
- [`config`](command_line_interface_config)
- [`compute`](command_line_interface_compute)
- [`dashboard`](command_line_interface_dashboard)
- [`get-data`](command_line_interface_get_data)
- [`convert`](command_line_interface_convert)
- [`filter`](command_line_interface_filter)
- [`plot`](command_line_interface_plot)

---

(command_line_interface_config)=
## Config

`metaDMG config` takes a single argument, `samples`, and a bunch of additional options and flags.
The `samples` refer to a single or multiple alignment-files (or a directory containing them), all with the file extensions: `.bam`, `.sam`, and `.sam.gz`.

### Parameters

#### Damage mode

- `--damage-mode`: `[lca|local|global]`. `lca` is the recommended and automatic setting. If using `local`, it means that damage patterns will be calculated for each chr/scaffold contig. If using `global`, it means one global estimate. Note that when using `[local|global]` the LCA parameters won't matter.

#### LCA
- Options:

  - `--names`: Path to the (NCBI) `names-mdmg.dmp`. Mandatory for LCA.
  - `--nodes`: Path to the (NCBI) `nodes-mdmg.dmp`. Mandator for LCA.
  - `--acc2tax`: Path to the (NCBI) `acc2tax.gz`. Mandatory for LCA.
  - `--min-similarity-score`: Normalised edit distance (read to reference similarity) minimum. Number between 0-1. Default: 0.95.
  - `--max-similarity-score`: Normalised edit distance (read to reference similarity) maximum. Number between 0-1 Default: 1.0.
  - `--min-edit-dist`: Minimum edit distance (read to reference similarity). Number between 0-10. Default: 0.
  - `--max-edit-dist`: Maximum edit distance (read to reference similarity). Number between 0-10. Default: 10.
  - `--min-mapping-quality`: Minimum mapping quality. Default: 0.
  - `--lca-rank`: The LCA rank used in ngsLCA. Can be either `family`, `genus`, `species` or `""` (everything). Default is `""`.

- Flags:
  - `--custom-database`: Using a custom database or the NCBI. If NCBI, automatically corrects for a couple of bad taxa. Default is False.

#### General

- Options:
  - `--output-dir`: Path where the generated output files and folders are stored. Default: `./data/`.
  - `--config-file`: The name of the generated config file. Default: `config.yaml`.
  - `--metaDMG-cpp`: The command needed to run the `metaDMG-cpp` program.
  - `--max-position`: Maximum position in the sequence to include. Default is (+/-) 15 (forward/reverse).
  - `--parallel-samples`: The number of samples to run in parallel. Default is running in seriel.
  - `--cores-per-sample`: Number of cores to use pr. sample. Do not change unless you know what you are doing.
  - `--sample-prefix`: Prefix for the sample names.
  - `--sample-suffix`: Suffix for the sample names.
  - `--weight-type`: Method for calculating weights. Default is 1. Do not change unless you know what you are doing.

- Flags:
  - `--forward-only`: Only fit the forward strand.
  - `--bayesian`: Include a fully Bayesian model (probably better, but also _a lot_ slower, about a factor of 100).
  - `--long-name`: Use the full, long, name for the sample.
  - `--overwrite`: Overwrite config file without user confirmation.



### Examples

```console
$ metaDMG config raw_data/alignment.bam \
    --names raw_data/names-mdmg.dmp \
    --nodes raw_data/nodes-mdmg.dmp \
    --acc2tax raw_data/acc2taxid.map.gz \
    --parallel-samples 4
```

`metaDMG` is pretty versatile regarding its input argument and also accepts multiple alignment files:
```console
$ metaDMG config raw_data/*.bam [...]
```
or even an entire directory containing alignment files (`.bam`, `.sam`, and `.sam.gz`):
```console
$ metaDMG config raw_data/ [...]
```

To run `metaDMG` in non-LCA mode, an example could be:
```
$ metaDMG config raw_data/alignment.bam --damage-mode local --max-position 15 --bayesian
```

---

(command_line_interface_compute)=
## Compute

The `metaDMG compute` command takes an optional config-file as argument
(defaults to `config.yaml` if not specified).

### Parameters

- Flags:
  - `--force`: Forced computation (even though the files already exists).


### Examples

```console
$ metaDMG compute
```

```console
$ metaDMG compute non-default-config.yaml --force
```

---

(command_line_interface_dashboard)=
## Dashboard

You can now see a preview of the [interactive dashboard](https://metadmg.herokuapp.com).

The `metaDMG dashboard` command takes first an optional config-file as argument
(defaults to `config.yaml` if not specified).

### Parameters

- Options:
  - `--results`: Path to the results directory.
  - `--port`: The port to be used for the dashboard. Default is `8050`.
  - `--host`: The dashboard host adress. Default is `0.0.0.0`.

- Flags:
  - `--debug`: Allow for easier debugging the dashboard. For internal usage.


### Examples

```console
$ metaDMG dashboard
```

```console
$ metaDMG dashboard non-default-config.yaml --port 8050 --host 0.0.0.0
```

---

(command_line_interface_get_data)=
## Get Data

The `metaDMG get-data` command gets test data and saves it in the output-dir. Useful for e.g. the online tutorial.

### Parameters

- Options:
  - `--output-dir`: Path to the output directory.

### Examples

```console
$ metaDMG get-data --output-dir raw_data
```


---

(command_line_interface_convert)=
## Convert

The `metaDMG convert` command takes first an optional config-file as argument
(defaults to `config.yaml` if not specified) used to infer the results directory.

### Parameters

- Options:
  - `--results`: Direct path to the results directory.
  - `--output`: Mandatory output path.

- Flags:
  - `--add-fit-predictions`: Include fit predictions D(x) in the output.


Note that neither the config-file nor `--results` have to be specified
(in which just the default `config.yaml` is used), however,
both cannot be set at the same time.

### Examples

```console
$ metaDMG convert --output ./directory/to/contain/results.csv
```

```console
$ metaDMG convert non-default-config.yaml --output ./directory/to/contain/results.csv --add-fit-predictions
```

---
(command_line_interface_filter)=
## Filter

The `metaDMG filter` command takes first an optional config-file as argument
(defaults to `config.yaml` if not specified) used to infer the results directory.

### Parameters

- Options:
  - `--results`: Direct path to the results directory.
  - `--output`: Mandatory output path.
  - `--query`: The query string to use for filtering. Follows the [Pandas Query()](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#the-query-method) syntax. Default is `""` which applies no filtering and is thus similar to the `metaDMG convert` command.

- Flags:
  - `--add-fit-predictions`: Include fit predictions D(x) in the output.


Note that neither the config-file nor `--results` have to be specified
(in which just the default `config.yaml` is used), however,
both cannot be set at the same time.

### Examples

```console
$ metaDMG filter --output convert-no-query.csv # similar to metaDMG convert
```

```console
$ metaDMG filter --output convert-test.csv --query "N_reads > 5_000 & sample in ['subs', 'SPL_195_9299'] & tax_name == 'root'" --add-fit-predictions
```


---

(command_line_interface_plot)=
## Plot

The `metaDMG plot` command takes first an optional config-file as argument
(defaults to `config.yaml` if not specified).


### Parameters

- Options:
  - `--results`: Direct path to the results directory.
  - `--query`: The query string to use for filtering. Follows the [Pandas Query()](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#the-query-method) syntax. Default is `""` which applies no filtering.
  - `--samples`: A comma-space seperated string containing the samples to use in the plots. Default is `""` which applies no filtering.
  - `--tax-ids`: A comma-space seperated string containing the tax-ids to use in the plots. Default is `""` which applies no filtering.
  - `--output`: The path to the output pdf-file. Defaults to `pdf_export.pdf`.


### Examples

```console
$ metaDMG plot
```

```console
$ metaDMG plot --query "100_000 <= N_reads & 8_000 <= phi" --tax-ids "1, 2, 42" --samples "sampleA, another-sample" --pdf-out name-of-plots.pdf
```

---

## mismatch-to-mapDamage

The `metaDMG mismatch-to-mapDamage` command takes a mandatory mismatch-file as argument
and converts it to the mapDamage format `misincorporation.txt`.

### Parameters

- Options:
  -  `--csv-out`: Output CSV file (`misincorporation.txt`). Default is `misincorporation.txt`.

### Examples

```console
$ metaDMG mismatch-to-mapDamage data/mismatches/XXX.mismatches.parquet
```
```console
$ metaDMG mismatch-to-mapDamage data/mismatches/XXX.mismatches.parquet --csv-out misincorporation.txt
```
