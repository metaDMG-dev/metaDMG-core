#%%
from pathlib import Path
from attr import dataclass
import yaml
import typer
from logger_tt import logger
import psutil
from functools import partial
from typing import Optional
from typing import Iterator
from itertools import islice

#%%


class Config(dict):
    pass


class Configs(dict):
    def __iter__(self) -> Iterator[Config]:
        dir_lca = self["dir"] / "lca"
        samples = self["samples"].keys()
        for sample in samples:
            config = Config(self)
            config["sample"] = sample
            config["bam"] = config["samples"][sample]

            config["path_mismatches_txt"] = dir_lca / f"{sample}.mismatches.txt.gz"

            if config["damage_mode"] == "lca":
                config["path_mismatches_stat"] = (
                    dir_lca / f"{sample}.mismatches.stat.txt.gz"
                )
            else:
                config["path_mismatches_stat"] = dir_lca / f"{sample}.stat.txt"

            config["path_lca"] = dir_lca / f"{sample}.lca.txt.gz"
            config["path_lca_log"] = dir_lca / f"{sample}.log.txt"
            config["path_tmp"] = config["dir"] / "tmp" / sample
            yield config

    def get_nth(self, n: int) -> Config:
        return next(islice(self, n, None))

    def get_first(self) -> Config:
        return self.get_nth(n=0)

    def __len__(self) -> int:
        return len(self["samples"].keys())


def make_configs(
    config_path: Optional[Path],
    log_port: Optional[int] = None,
    log_path: Optional[str] = None,
    forced: bool = False,
) -> Configs:

    if config_path is None:
        config_path = Path("config.yaml")

    if not config_path.exists():
        logger.error("Error! Please select a proper config file!")
        raise typer.Abort()

    logger.info(f"Using {config_path} as config file.")
    with open(config_path, "r") as file:
        d = yaml.safe_load(file)

    d["log_port"] = log_port
    d["log_path"] = log_path
    if forced:
        d["forced"] = True

    d.setdefault("forward_only", False)
    d.setdefault("cores_pr_fit", 1)
    d.setdefault("damage_mode", "lca")
    d.setdefault("forced", False)

    paths = ["metaDMG-lca", "names", "nodes", "acc2tax", "dir"]
    for path in paths:
        d[path] = Path(d[path])

    return Configs(d)


#%%


def check_number_of_jobs(configs: Configs) -> None:

    cores = min(configs["cores"], len(configs["samples"]))
    cores_pr_fit = configs["cores_pr_fit"]
    N_jobs = cores * cores_pr_fit
    max_cores = psutil.cpu_count(logical=True)
    max_cores_real = psutil.cpu_count(logical=False)

    if N_jobs > max_cores:
        logger.warning(
            f"The total number of jobs {N_jobs} are higher "
            f"than the number of cores {max_cores}. "
            f"Do not do this unless you know what you are doing. "
            f"Try decreasing either 'cores' or 'cores-pr-fit'."
        )
    elif N_jobs > max_cores_real:
        logger.info(
            f"The total number of jobs {N_jobs} are higher "
            f"than the real number of cores {max_cores_real} (non-logical). "
            f"This might decrease performance. "
        )


def path_endswith(path, s):
    return str(path.name).endswith(s)


def extract_name(filename, max_length=100, prefix="", suffix="", long_name=False):
    name = Path(filename).stem
    if not long_name:
        name = name.split(".")[0]
    if len(name) > max_length:
        name = name[:max_length] + "..."
    name = prefix + name + suffix
    return name


def extract_names(file_list, **kwargs):
    return list(map(partial(extract_name, **kwargs), file_list))


def extract_alignment_files(paths):

    alignments = []
    suffixes = (".bam", ".sam", ".sam.gz")

    for path in paths:
        # break
        if path.is_file() and any(path_endswith(path, suffix) for suffix in suffixes):
            alignments.append(path)
        elif path.is_dir():

            files = [
                p
                for p in Path(path).glob("*")
                if any(path_endswith(p, suffix) for suffix in suffixes)
            ]

            recursive = extract_alignment_files(files)
            alignments.extend(recursive)

    return alignments


def extract_alignments(paths, prefix="", suffix="", long_name=False):

    alignments = extract_alignment_files(paths)
    samples = extract_names(
        alignments,
        prefix=prefix,
        suffix=suffix,
        long_name=long_name,
    )

    d_alignments = {}
    for sample, path in zip(samples, alignments):
        d_alignments[sample] = path_to_str(path)

    return d_alignments


def path_to_str(p):
    if isinstance(p, Path):
        return str(p)
    else:
        return p


def remove_paths(d, ignore_keys=None):

    if ignore_keys is None:
        ignore_keys = []

    d_out = {}
    for key, val in d.items():
        if val in ignore_keys:
            continue
        elif isinstance(val, list):
            d_out[key] = list(map(path_to_str, val))
        elif isinstance(val, tuple):
            d_out[key] = tuple(map(path_to_str, val))
        elif isinstance(val, dict):
            d_out[key] = remove_paths(val)
        else:
            d_out[key] = path_to_str(val)
    return d_out


#%%


def get_results_dir(
    config_path: Optional[Path] = None,
    results_dir: Optional[Path] = None,
) -> Path:

    if config_path is not None and results_dir is not None:
        raise AssertionError("'config_path' and 'results_dir' cannot both be set")

    if results_dir:
        return results_dir

    return make_configs(config_path)["dir"] / "results"
