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
    name='technogix_iac_keywords',
    description='A set of robotframework keywords to test AWS infrastructure deployment by terraform',
    author='Technogix',
    author_email='contact.technogix@gmail.com',
    url='https://github.com/technogix-terraform/robotframework/',
    use_scm_version=True,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['robotframework>=5.0.1','boto3>=1.24.1'],
    python_requires=">3.6",
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Testers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License'
    ]
)
