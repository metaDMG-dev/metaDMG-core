import shutil
from importlib import resources
from pathlib import Path


def get_data(output_dir: Path = Path("raw_data")) -> None:
    """Copies the data file to a new directory

    Parameters
    ----------
    output_dir
        _description_
    """

    files = [
        "alignment.sorted.bam",
        "names-mdmg.dmp",
        "nodes-mdmg.dmp",
        "acc2taxid.map.gz",
    ]

    for file in files:
        with resources.path("metaDMG.data", file) as p:
            file_path = p

        target_path = Path(output_dir) / file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(file_path, target_path)
