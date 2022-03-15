# Workflow

## Create the config file

`metaDMG` works by first creating a config file using the `config` command. This file contains all of the information related to metaDMG such that you only have to type this once. The config file is saved in the current directory as `config.yaml` and can subsequently be edited in any text editor of your like.

```console
$ metaDMG config ./raw_data/example.bam \
    --names raw_data/names.dmp.gz \
    --nodes raw_data/nodes.dmp.gz \
    --acc2tax raw_data/combined_taxid_accssionNO_20200425.gz
```

## Run the computation

After the config has been created, we run the actual program using the `compute` command. This can take a while depending on the number (and size) of the files.

```console
$ metaDMG compute
```

## Dashboard

The results are saved in `{storage-dir}/results` directory (`data/results` by default). These can be viewed with the interactive dashboard using the `dashboard` command.

```console
$ metaDMG dashboard
```

