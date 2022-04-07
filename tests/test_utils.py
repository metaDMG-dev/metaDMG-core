import pytest
import typer

from metaDMG import utils


def test_split_string():
    assert utils.split_string("1, 2, 42") == ["1", "2", "42"]

    assert utils.split_string("1,2,42") == ["1", "2", "42"]

    assert utils.split_string("1 2 42") == ["1", "2", "42"]


def test_extract_damage_modes():

    assert utils.extract_damage_modes("lca") == ["lca"]
    assert utils.extract_damage_modes("lcA") == ["lca"]

    assert utils.extract_damage_modes("lca, global") == ["lca", "global"]
    assert utils.extract_damage_modes("lca,LOCAL") == ["lca", "local"]

    with pytest.raises(typer.Abort):
        utils.extract_damage_modes("lac")

    with pytest.raises(typer.Abort):
        utils.extract_damage_modes("lca,LOCAL,globlal")
