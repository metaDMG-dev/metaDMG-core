from metaDMG import utils


def test_split_string():
    assert utils.split_string("1, 2, 42") == ["1", "2", "42"]

    assert utils.split_string("1,2,42") == ["1", "2", "42"]

    assert utils.split_string("1 2 42") == ["1", "2", "42"]
