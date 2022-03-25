# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""

    pass


class metadamageError(Error):
    """Raised when we get an error with the metadamage part of the program"""

    pass


class AlignmentFileError(Error):
    """Raised when the alignment file is invalid"""

    pass


class FittingError(Error):
    """Raised when we get an error with the fit of a specific Tax ID"""

    pass


class MismatchFileError(Error):
    """Raised when the {sample}.mismatches.txt does not contain any data"""

    pass


class BadDataError(Error):
    """Raised when the {sample}.mismatches.txt does not contain any useful damage data"""

    pass
