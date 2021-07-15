from pathlib import Path
from setuptools import setup


# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setup(
    name="metaDMG",
    packages=["metaDMG"],
    author="Christian Michelsen",
    author_email="christianmichelsen@gmail.com",
    description="metaDMG: Estimating ancient damage in (meta)genomic DNA rapidly",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/metaDMG/metaDMG/",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=[
        "numpy",
        "pandas",
        "typer",
        "click_help_colors",
    ],
    extras_require={
        "fit": ["metaDMG-fit"],
        "viz": ["metaDMG-viz"],
        "all": ["metaDMG-fit", "metaDMG-viz"],
    },
    entry_points={"console_scripts": ["metaDMG=metaDMG.cli:cli_main"]},
)
