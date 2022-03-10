""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Robotframework module setup file
# -------------------------------------------------------
# Nadège LEMPERIERE, @17 october 2021
# Latest revision: 17 october 2021
# --------------------------------------------------- """

from setuptools import setup, find_packages

setup(
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    packages=find_packages(),
    include_package_data=True,
)
