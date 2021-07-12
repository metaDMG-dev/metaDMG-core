# metaDMG-fit

---

#### Work in progress. Please contact christianmichelsen@gmail.com for further information.

---



Assumes you have a `config.yaml` file in the path and the executable metaDMG-lca located at the location specified in the `['metaDMG-lca']` key of the config.


Installation:

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


Example yaml:
```yaml
samples:
  subs: raw_data/subs.bam
  SPL_195_9299: raw_data/SPL_195_9299.tmp.bam.merged.sort.bam
metaDMG-lca: ./metaDMG-lca
names: raw_data/names.dmp.gz
nodes: raw_data/nodes.dmp.gz
acc2tax: raw_data/combined_taxid_accssionNO_20200425.gz
simscorelow: 0.95
simscorehigh: 1.0
editdistmin: 0
editdistmax: 10
minmapq: 0
lca_rank: ''
max_position: 15
cores: 8
bayesian: false
verbose: false
dir: data
```
