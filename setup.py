#!/usr/bin/env python
from setuptools import setup
import tests

with open("VERSION") as version_file:
    VERSION = version_file.read().rstrip()

setup(
    name="doug",
    version=VERSION,
    packages = ["lib", "lib.stroke", "gui"],
    scripts = ["scripts/doug"],
    test_suite="tests.test_suite",
    license="GPL-3"
)
