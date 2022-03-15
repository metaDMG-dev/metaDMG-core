#%%
from pathlib import Path
import yaml
import typer
from logger_tt import logger
import psutil
from functools import partial
from typing import Optional, Iterator, Iterable
from itertools import islice


#%%


class Config(dict):
    """Config contains the parameters related to specific alignment file."""

    pass


class Configs(dict):
    """Configs contains the parameters related to config file.
    Inherits from dict. Implements iterations.
    """

    def __iter__(self) -> Iterator[Config]:
        """Iteration

        Yields
        ------
        Iterator[Config]
            Allow for iteration
        """
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
        """Gets the n'th config

        Parameters
        ----------
        n
            The index

        Returns
        -------
        Config
            A single configuration
        """
        return next(islice(self, n, None))

    def get_first(self) -> Config:
        """Get the first config

        Returns
        -------
        Config
            A single configuration
        """
        return self.get_nth(n=0)

    def __len__(self) -> int:
        """The number of configs

        Returns
        -------
        int
            The number of configs
        """
        return len(self["samples"].keys())

    def check_number_of_jobs(self) -> None:
        """Compare the number of configs to the number of cores used."""

        cores = min(self["cores"], len(self["samples"]))
        cores_pr_fit = self["cores_pr_fit"]
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


def make_configs(
    config_path: Optional[Path],
    log_port: Optional[int] = None,
    log_path: Optional[str] = None,
    forced: bool = False,
) -> Configs:
    """Create an instance of Configs from a config file

    Parameters
    ----------
    config_path
        The config file to load
    log_port
        Optional log port, by default None
    log_path
        Optional log path, by default None
    forced
        Whether or not the computations are forced, by default False

    Returns
    -------
        An instance of Configs

    Raises
    ------
    typer.Abort
        If not a proper config file
    """

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

    paths = ["names", "nodes", "acc2tax", "dir", "config_path"]
    for path in paths:
        d[path] = Path(d[path])
    for key, val in d["samples"].items():
        d["samples"][key] = Path(val)

    for key, val in d.items():
        if isinstance(val, str):
            if val.isdigit():
                d[key] = int(key)

    return Configs(d)


#%%


def path_endswith(path: Path, s: str) -> bool:
    return str(path.name).endswith(s)


def extract_name(
    filename: Path,
    max_length: int = 100,
    prefix: str = "",
    suffix: str = "",
    long_name: bool = False,
) -> str:
    """Extract the name from a file

    Parameters
    ----------
    filename
        The input file
    max_length
        The maximum length of the name, by default 100
    prefix
        The prefix to be added to the name, by default ""
    suffix
        The suffix to be added to the name, by default ""
    long_name
        Whether or not to use the full name, by default False

    Returns
    -------
        The name
    """
    name = Path(filename).stem
    if not long_name:
        name = name.split(".")[0]
    if len(name) > max_length:
        name = name[:max_length] + "..."
    name = prefix + name + suffix
    return name


def extract_names(file_list, **kwargs):
    return list(map(partial(extract_name, **kwargs), file_list))


def extract_alignment_files(paths: list[Path]) -> list[Path]:
    """Extract all alignment files from a list of paths.
    Alignment files are expected to be .bam, .sam, or .sam.gz.

    Parameters
    ----------
    paths
        Input list of paths

    Returns
    -------
        Output list of alignment files
    """
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


def extract_alignments(
    paths: list[Path],
    prefix: str = "",
    suffix: str = "",
    long_name: bool = False,
) -> dict:
    """Extract all alignment files from a list of files.
    Truncates the name of the files, controlled by prefix, suffix, and long_name

    Parameters
    ----------
    paths
        List of paths to be extracted
    prefix
        The prefix to be added to the name, by default ""
    suffix
        The suffix to be added to the name, by default ""
    long_name
        Whether or not to use the full name, by default False

    Returns
    -------
        Dictionary with names as keys and files as values.
    """

    alignments = extract_alignment_files(paths)
    samples = extract_names(
        alignments,
        prefix=prefix,
        suffix=suffix,
        long_name=long_name,
    )

    d_alignments = {}
    for sample, path in zip(samples, alignments):
        d_alignments[sample] = str(path)

    return d_alignments


def paths_to_strings(
    d: dict,
    ignore_keys: Optional[Iterable] = None,
) -> dict:
    """Convert all the paths in a dictionary to strings

    Parameters
    ----------
    d
        Input dict to be converted
    ignore_keys
        Ignore the following keys in the iterable, by default None

    Returns
    -------
        Dictionary with strings instead of paths
    """

    if ignore_keys is None:
        ignore_keys = []

    d_out = {}
    for key, val in d.items():
        if val in ignore_keys:
            continue
        elif isinstance(val, list):
            d_out[key] = list(map(str, val))
        elif isinstance(val, tuple):
            d_out[key] = tuple(map(str, val))
        elif isinstance(val, dict):
            d_out[key] = paths_to_strings(val)
        elif isinstance(val, Path):
            d_out[key] = str(val)
        else:
            d_out[key] = val
    return d_out


#%%


def get_results_dir(
    config_path: Optional[Path] = None,
    results_dir: Optional[Path] = None,
) -> Path:
    """Helper function that gets the results directory from either the
    config file or the results directory directly.

    Parameters
    ----------
    config_path
        Config file, by default None
    results_dir
        Results directory, by default None

    Returns
    -------
        Path to the results directory

    Raises
    ------
    AssertionError
        If both config file and results directory are set, raise error
    """

    if config_path is not None and results_dir is not None:
        raise AssertionError("'config_path' and 'results_dir' cannot both be set")

    if results_dir:
        return results_dir

    return make_configs(config_path)["dir"] / "results"
