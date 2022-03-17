from pathlib import Path

from ete3 import NCBITaxa
from joblib import Memory


cachedir = ".memoization"
memory = Memory(cachedir, verbose=0)

# @lru_cache
@memory.cache
def extract_descendant_tax_ids(tax, include_subspecies=True):
    """Given either tax_id or tax_name, extract all the descendants' taxIDs.
    Subspecies are automatically included, but can be disables with
    include_subspecies = False.
    """

    ncbi = NCBITaxa()

    # species
    try:
        descendants = set(ncbi.get_descendant_taxa(tax, collapse_subspecies=True))
    except ValueError:
        return []

    # subspecies
    if include_subspecies:
        try:
            descendants |= set(ncbi.get_descendant_taxa(tax, collapse_subspecies=False))
        except ValueError:
            pass

    if Path("taxdump.tar.gz").exists():
        Path("taxdump.tar.gz").unlink()

    return list(descendants)


def include_subspecies(subspecies):
    if len(subspecies) == 1:
        return True
    return False


def apply_tax_id_descendants_filter(d_filter, tax_name, sidebar_left_tax_id_subspecies):
    if tax_name is None:
        return None

    tax_ids = extract_descendant_tax_ids(
        tax_name,
        include_subspecies=include_subspecies(sidebar_left_tax_id_subspecies),
    )
    N_tax_ids = len(tax_ids)
    if N_tax_ids != 0:
        if "tax_id" in d_filter:
            d_filter["tax_ids"].extend(tax_ids)
        else:
            d_filter["tax_ids"] = tax_ids
