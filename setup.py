from setuptools import setup

setup(
    name="metaDMG",
    version="21.7.1",
    packages=["metaDMG"],
    author="Christian Michelsen",
    author_email="christianmichelsen@gmail.com",
    url="https://github.com/metaDMG/metaDMG/",
    license="MIT",
    description="metaDMG",
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
