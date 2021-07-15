from setuptools import setup

setup(
    name="metaDMG",
    packages=["metaDMG"],
    author="Christian Michelsen",
    author_email="christianmichelsen@gmail.com",
    url="https://github.com/metaDMG/metaDMG/",
    license="MIT",
    description="metaDMG",
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
