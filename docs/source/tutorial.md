# Tutorial

This tutorial consist of two parts: a relatively [simple](simple) analysis of a very small alignment file avaliable in repository, and a larger and more real life analysis of the [Kap Copenhagen](KapK) dataset.

(simple)=
## Simple Analysis

### Input data

To run the full suite of commands, i.e. the LCA and fits, `metaDMG` requires the following input files:

1. An aligment file (or a directory containing multiple alignment files).
2. A `names` file, which contains the names of the different accessions in the database.
3. A `nodes` file, which contains the relationship between the different accessions in the database (the graph structure, so to speak).
4. A `acc2tax` file, which is the conversion between accesion number and the tax ID.

To make the introduction to `metaDMG` easy, `metaDMG` is by default shipped with a small data directory containing these.

These files can be loaded by running the following command:
```console
$ metaDMG get-data --output-dir raw_data
```
where `raw_data` is the output directory where you want to store the files.

### Config

Now that the we have the raw data, we can start running `metaDMG`.
For ease of use, `metaDMG` is structured such that we first need to generate a `config` file which contains all of the options that the LCA and fits require.
To compare two different analysis, one simply need to compare the `config` files. As such, the `config` file can thus be seen as all the relevant metadata.

`metaDMG config` should have sensible defaults. The full specification of the avaliable options can be found either by running `metaDMG config --help` or for a more thorough explanation, see [here](command_line_interface_config).

Since the data we have in this example is quite small, we want to run the full Bayesian analysis. As such, we generate the following `config` file:

```console
$ metaDMG config raw_data/alignment.bam \
    --names raw_data/names-mdmg.dmp \
    --nodes raw_data/nodes-mdmg.dmp \
    --acc2tax raw_data/acc2taxid.map.gz \
    --custom-database \
    --bayesian
```

Most of the options should be quite self-explanatory. `--bayesian` indicates that we want to run the full Bayesian model, which is slower than the faster, approximate model that we use by default. The `--custom-database` flag is needed since this database is not the full NCBI one.

After running this command, you should notice a new file in your directory: `config.yaml`. This is a normal `.yaml` file which can be opened and edited with your favorite text editor. In case you wanted to call the config file something different, you can add `--config-file config_simple.yaml`.

### Compute

Now that we have generated a config file with all of the necessary parameters, we can start the actual computation. This is done by running:
```console
$ metaDMG compute
```
or, in the case of another name for the config file:
```console
$ metaDMG compute config_simple.yaml
```

When you enter the command, `metaDMG` will first parse the config file and extract the relevant parameters for the LCA. The C++ part of the program will perform the LCA of the reads in the alignment file and output its intermediary files in `{output-dir}/lca/` (`data/lca` by default). This step can take a while on real datasets. We then load these files and turn them into a mismatch matrix (XXX link here) in a pandas dataframe. Now, having a mismatch matrix for each tax ID, we fit each of these independently. Since we added the `--bayesian` flag previously, we perform the full, Bayesian analysis in addition to the fast, approximate version. For more information, see XXX link here to information. This step can also be quite slow on real datasets, which is also why we do not do this by default.
Finally, after the fits are done, we merge the fit results with some additional information from the mismatch matrices and save the results to disk in `{output-dir}/results/` (`data/results` by default).

(KapK)=
## Kap Copenhagen
