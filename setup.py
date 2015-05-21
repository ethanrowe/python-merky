from setuptools import setup
import os

setup(
    name = "merky",
    version = "0.0.1a",
    author = "Ethan Rowe",
    author_email = "ethan@the-rowes.com",
    description = ("JSON-oriented merkle tree utilities"),
    license = "MIT",
    url = "https://github.com/ethanrowe/python-merky",
    packages = ["merky",
                "merky.test",
    ],
    long_description = """
Merky - compute merkle trees for JSON-friendly data.
""",
    test_suite = "nose.collector",
    install_requires = [
                'six >= 1.5',
    ],
    setup_requires = [
        'nose',
        'mock >= 1.0.1',
    ],
    tests_require = [
        'nose',
        'mock >= 1.0.1',
    ],
)
