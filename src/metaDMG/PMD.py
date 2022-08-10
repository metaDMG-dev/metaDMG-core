#

import shlex
import subprocess
from pathlib import Path

import pandas as pd


#%%


def iterate_command(command: str):

    p = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    for line in iter(p.stdout.readline, b""):  # type: ignore
        if line:
            line = line.decode("utf-8")
            if line.endswith("\n"):
                line = line[:-1]
            yield line

    # waits for the process to finish and returns the returncode
    yield p.wait()


def compute_PMDs(bam_file: Path, metaDMG_cpp: str):
    """Run the PMD command from metaDMG-cpp and get a DataFrame with the results.

    Parameters
    ----------
    bam_file
        Alignment file to compute the PMD scores on
    metaDMG_cpp
        The metaDMG binary to use
    """

    command = f"{metaDMG_cpp} pmd {bam_file}"

    returncode = 1
    reads = []
    PMDs = []
    for i, line in enumerate(iterate_command(command)):

        # if finished, check returncode
        if isinstance(line, int):
            returncode = line

        else:
            read, PMD = line.split("\tPMD:")
            reads.append(read)
            PMDs.append(float(PMD))

    if returncode != 0:
        raise Exception(f"Error running {command}")

    df = pd.DataFrame({"read": reads, "PMD": PMDs})
    return df
