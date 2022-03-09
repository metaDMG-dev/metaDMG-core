from pathlib import Path
import yaml
import typer
from logger_tt import logger
import psutil
from functools import partial


def load_config(config_path=None, log_port=None, log_path=None, forced=False):
    if config_path is None:
        config_path = "config.yaml"

    if not Path(config_path).exists():
        logger.error("Error! Please select a proper config file!")
        raise typer.Abort()

    logger.info(f"Opening {config_path} as config file.")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    if "forward_only" not in config:
        config["forward_only"] = False

    if log_port is not None:
        config["log_port"] = log_port

    if log_path is not None:
        config["log_path"] = log_path

    if "cores_pr_fit" not in config:
        config["cores_pr_fit"] = 1

    if forced or config.get("forced"):
        config["forced"] = True
    else:
        config["forced"] = False

    if "damage_mode" not in config:
        config["damage_mode"] = "lca"

    return config


def check_number_of_jobs(config):

    cores = min(config["cores"], len(config["samples"]))
    cores_pr_fit = config["cores_pr_fit"]
    N_jobs = cores * cores_pr_fit
    max_cores = psutil.cpu_count(logical=True)
    max_cores_real = psutil.cpu_count(logical=False)

    if N_jobs > max_cores:
        logger.warning(
            f"The total number of jobs {N_jobs} are higher "
            f"than the number of cores {max_cores}. "
            "Do not do this unless you know what you are doing. "
            "Try decreasing either 'cores' or 'cores-pr-fit'."
        )
    elif N_jobs > max_cores_real:
        logger.info(
            f"The total number of jobs {N_jobs} are higher "
            f"than the real number of cores {max_cores_real} (non-logical). "
            "This might decrease performance. "
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


def get_results_dir(config_path=None, results_dir=None):

    if config_path is not None and results_dir is not None:
        raise AssertionError(
            "Only a single one of 'config' and 'results_dir' can be set"
        )

    results_dir = Path(results_dir) if isinstance(results_dir, str) else results_dir
    config_path = Path(config_path) if isinstance(config_path, str) else config_path

    if isinstance(results_dir, Path):
        return results_dir

    results_dir = Path(load_config(config_path)["dir"]) / "results"
    return results_dir
