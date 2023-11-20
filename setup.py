""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Robotframework module setup file
# -------------------------------------------------------
# Nadège LEMPERIERE, @17 october 2022
# Latest revision: 19 november 2023
# --------------------------------------------------- """

from setuptools import setup, find_packages

setup(
    name='aws_iac_keywords',
    description='A set of robotframework keywords to test AWS infrastructure deployment by terraform',
    author='Nadege Lemperiere',
    author_email='nadege.lemperiere@gmail.com',
    url='https://github.com/nadegelemperiere-aws/robotframework/',
    use_scm_version=True,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['robotframework>=6.1.1','boto3>=1.29.3'],
    python_requires=">3.12",
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Testers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License'
    ]
)
