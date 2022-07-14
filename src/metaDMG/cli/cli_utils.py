from enum import Enum
from functools import partial
from pathlib import Path
from typing import Iterable, Optional

import click
import typer
import yaml
from rich import print


#%%


output_dir_default = Path("./data/")
# results_dir_default = output_dir_default / "results"
config_file_default = Path("config.yaml")


#%%


# class OrderedCommands(Group):
class OrderedCommands(typer.core.TyperGroup):
    def list_commands(self, ctx: click.Context) -> Iterable[str]:
        return self.commands.keys()


def get_cli_app():
    cli_app = typer.Typer(cls=OrderedCommands, rich_markup_mode="rich")
    return cli_app


def version_callback(value: bool):
    from metaDMG.__version__ import __version__

    if value:
        print(f"metaDMG CLI, version: {__version__}")
        raise typer.Exit()


def is_in_range_or_None(
    x: Optional[float], val_min: float, val_max: float
) -> Optional[float]:
    """Confirms that x is val_min <= x <= val_max

    Parameters
    ----------
    x
        Value to check
    val_min
        Minimum
    val_max
        Maximum

    Returns
    -------
        Confirmed value

    Raises
    ------
    typer.BadParameter
        If x is outside bounds
    """

    if x is None:
        return x

    if x < val_min or val_max < x:
        raise typer.BadParameter(
            f"x has to be between {val_min} and {val_max}. Got: {x}"
        )
    return x


def is_positive_int_or_None(x: Optional[int]) -> Optional[int]:
    """Confirms that x is 0 <= x

    Parameters
    ----------
    x
        Value to check

    Returns
    -------
        Confirmed value

    Raises
    ------
    typer.BadParameter
        If x is outside bounds
    """

    if x is None:
        return x

    if x < 0:
        raise typer.BadParameter(f"x has to be positive. Got: {x}")

    return x


#%%
class RANKS(str, Enum):
    "Ranks allowed in the LCA"

    family = "family"
    genus = "genus"
    species = "species"
    none = ""

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def str_list(cls):
        return [c if c != "" else "none" for c in cls.list()]


class DAMAGE_MODE(str, Enum):
    "Damage mode allowed in the LCA"

    LCA = "lca"
    LOCAL = "local"
    GLOBAL = "global"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def upper_list(cls):
        return [c.upper() for c in cls.list()]


#%%


def set_min_max_similarity_score_edit_dist(
    min_similarity_score: Optional[float],
    max_similarity_score: Optional[float],
    min_edit_dist: Optional[int],
    max_edit_dist: Optional[int],
) -> dict[str, float]:

    if any([min_similarity_score, max_similarity_score]) and any(
        [min_edit_dist, max_edit_dist]
    ):
        raise typer.BadParameter(
            f"You cannot use both similarity scores and edit distances at the same time."
        )

    # edit distances
    if any([min_edit_dist, max_edit_dist]):

        if all([min_edit_dist, max_edit_dist]):

            if min_edit_dist > max_edit_dist:
                raise typer.BadParameter(
                    f"min-edit-dist ({min_edit_dist}) "
                    f"has to be lower than max-edit-dist ({max_edit_dist})"
                )

            return {
                "min_edit_dist": min_edit_dist,
                "max_edit_dist": max_edit_dist,
            }

        else:
            raise typer.BadParameter(
                f"If using (absolute) edit distances, you have to set "
                "both `min_edit_dist` and `max_edit_dist`."
            )

    # similarity scores

    if min_similarity_score is None:
        min_similarity_score = 0.95

    if max_similarity_score is None:
        max_similarity_score = 1.0

    if min_similarity_score > max_similarity_score:
        raise typer.BadParameter(
            f"min-similarity-score ({min_similarity_score}) "
            f"has to be lower than max-similarity-score ({max_similarity_score})"
        )

    return {
        "min_similarity_score": min_similarity_score,
        "max_similarity_score": max_similarity_score,
    }


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


def extract_samples(
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


def save_config_file(
    config: dict,
    config_file: Path,
    overwrite_config: bool = False,
    verbose: bool = True,
) -> None:
    """Save the config file.
    Does not overwrite if file already exists, unless explicitly specified.

    Parameters
    ----------
    config
        Input dict
    config_file
        Save location

    Raises
    ------
    typer.Abort
        Do not overwrite automatically
    """

    if not overwrite_config:
        if config_file.is_file():
            s = "Config file already exists. Do you want to overwrite it?"
            confirmed = typer.confirm(s)
            if not confirmed:
                print("Exiting")
                raise typer.Abort()

    with open(config_file, "w") as file:
        yaml.dump(config, file, sort_keys=False)
    if verbose:
        print(f"{str(config_file)} was created")


#%%


def get_config_dict(
    samples: list[Path],
    names: Optional[Path] = None,
    nodes: Optional[Path] = None,
    acc2tax: Optional[Path] = None,
    min_similarity_score: Optional[float] = None,
    max_similarity_score: Optional[float] = None,
    min_edit_dist: Optional[int] = None,
    max_edit_dist: Optional[int] = None,
    min_mapping_quality: int = 0,
    custom_database: bool = False,
    lca_rank: RANKS = RANKS.none,
    metaDMG_cpp: str = "./metaDMG-cpp",
    max_position: int = 15,
    min_reads: int = 0,
    weight_type: int = 1,
    forward_only: bool = False,
    bayesian: bool = False,
    output_dir: Path = output_dir_default,
    parallel_samples: int = 1,
    cores_per_sample: int = 1,
    config_file: Path = config_file_default,
    sample_prefix: str = "",
    sample_suffix: str = "",
    long_name: bool = False,
    damage_mode: DAMAGE_MODE = DAMAGE_MODE.LCA,
    __version__: str = "",
) -> dict:

    config = paths_to_strings(
        {
            "samples": extract_samples(
                samples,
                prefix=sample_prefix,
                suffix=sample_suffix,
                long_name=long_name,
            ),
            #
            "metaDMG_cpp": metaDMG_cpp,
            "names": names,
            "nodes": nodes,
            "acc2tax": acc2tax,
            **set_min_max_similarity_score_edit_dist(
                min_similarity_score, max_similarity_score, min_edit_dist, max_edit_dist
            ),
            "min_mapping_quality": min_mapping_quality,
            "lca_rank": lca_rank.lower(),
            "max_position": max_position,
            "min_reads": min_reads,
            "weight_type": weight_type,
            "custom_database": custom_database,
            "forward_only": forward_only,
            #
            "output_dir": output_dir,
            "parallel_samples": parallel_samples,
            "cores_per_sample": cores_per_sample,
            "bayesian": bayesian,
            "config_file": str(config_file),
            "damage_mode": damage_mode.lower(),
            "version": __version__,
        }
    )

    return config
