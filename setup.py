import subprocess
import setuptools

setuptools.setup(
    name="mongobar",
    version="0.0.1",
    description="MongoDB Backup and Restore Manager",
    url="https://github.com/chrisantonellis/mongobar",

    author="Christopher Antonellis",
    author_email="christopher.antonellis@gmail.com",

    packages=[
        "mongobar"
    ],
    # https://stackoverflow.com/a/5899643/1671562
    package_data={
        "mongobar": [
            "data/nouns.txt",
            "data/verbs.txt"
        ]
    },
    scripts=[
        "mongobar/scripts/mongobar"
    ],
    install_requires=[
        "pymongo",
        "colorama",
        "argcomplete",
        "terminaltables",
        "python-dateutil"
    ],
    extras_require={
        "tests": [
            "green",
            "coverage"
        ],
    }
)
