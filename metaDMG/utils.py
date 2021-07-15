from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import yaml


def load_config(config=None):
    if config is None:
        config = "config.yaml"
    with open(config, "r") as file:
        config = yaml.safe_load(file)
    return config


def path_endswith(path, s):
    return str(path.name).endswith(s)


def extract_name(filename, max_length=100):
    sample = Path(filename).stem.split(".")[0]
    if len(sample) > max_length:
        sample = sample[:max_length] + "..."
    return sample


def extract_names(file_list):
    return list(map(extract_name, file_list))


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


def extract_alignments(paths):

    alignments = extract_alignment_files(paths)
    samples = extract_names(alignments)

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
