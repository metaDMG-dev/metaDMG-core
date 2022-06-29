from enum import Enum
from typing import Iterable, Optional

import typer
from click import Context, Group
from click_help_colors import HelpColorsCommand, HelpColorsGroup


#%%


class CustomHelpColorsCommand(HelpColorsCommand):
    """Colorful command line main help. Colors one of:
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white", "reset",
    "bright_black", "bright_red", "bright_green", "bright_yellow",
    "bright_blue", "bright_magenta", "bright_cyan", "bright_white"
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.help_headers_color = "yellow"
        self.help_options_color = "blue"


class CustomHelpColorsGroup(HelpColorsGroup):
    # colorfull command line for subcommands
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.help_headers_color = "yellow"
        self.help_options_color = "blue"


class ColorfulApp(typer.Typer):
    def __init__(self, *args, cls=CustomHelpColorsGroup, **kwargs) -> None:
        super().__init__(*args, cls=cls, **kwargs)

    def command(
        self, *args, cls=CustomHelpColorsCommand, **kwargs
    ) -> typer.Typer.command:
        return super().command(*args, cls=cls, **kwargs)


class OrderedCommands(Group):
    def list_commands(self, ctx: Context) -> Iterable[str]:
        return self.commands.keys()


def get_cli_app():
    cli_app = ColorfulApp(cls=OrderedCommands)
    # cli_app = ColorfulApp(cls=OrderedCommands, chain=True)
    return cli_app


def version_callback(value: bool):
    from metaDMG.__version__ import __version__

    if value:
        typer.echo(f"metaDMG CLI, version: {__version__}")
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


class DAMAGE_MODE(str, Enum):
    "Damage mode allowed in the LCA"

    LCA = "lca"
    LOCAL = "local"
    GLOBAL = "global"


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
