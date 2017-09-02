import io
import os
import sys
import shutil
import subprocess
import setuptools


class PublishCommand(setuptools.Command):
    """Support setup.py publish."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            shutil.rmtree(os.path.join(here, 'dist'))
        except FileNotFoundError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


here = os.path.abspath(os.path.dirname(__file__))

setuptools.setup(
    name="mongobar",
    version="0.0.3",
    description="MongoDB Backup and Restore Manager",
    keywords="mongodb backup restore mongodump mongorestore",
    url="https://github.com/chrisantonellis/mongobar",

    author="Christopher Antonellis",
    author_email="christopher.antonellis@gmail.com",
    license="MIT",
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
    },
    # $ setup.py publish support.
    cmdclass={
        'publish': PublishCommand
    }
)
