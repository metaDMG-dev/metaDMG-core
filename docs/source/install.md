
# Installation

## With conda

```bash
conda env create --file environment.yaml
```
or, if you have mamba installed (faster)
```
mamba env create --file environment.yaml
```
## With pip
```
pip install "metaDMG[all]"
```
## With poetry
```
poetry add "metaDMG[all]"
```

## Updating

With pip or Conda:
```console
pip install "metaDMG[all]"  --upgrade
```

With Poetry:
```console
poetry add metaDMG["all"]
poetry add metaDMG-viz@latest
```