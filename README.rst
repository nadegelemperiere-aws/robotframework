.. image:: docs/imgs/logo.png
   :alt: Logo

===========================================
Technogix terraform robotframework keywords
===========================================

About The Project
=================

This project provides a set of robotframework keywords used to check the results of terraform deployments.

.. image:: https://badgen.net/github/checks/technogix-terraform/robotframework
   :target: https://github.com/technogix-terraform/robotframework/actions/workflows/release.yml
   :alt: Status
.. image:: https://img.shields.io/static/v1?label=license&message=MIT&color=informational
   :target: ./LICENSE
   :alt: License
.. image:: https://badgen.net/github/commits/technogix-terraform/robotframework/main
   :target: https://github.com/technogix-terraform/robotframework
   :alt: Commits
.. image:: https://badgen.net/github/last-commit/technogix-terraform/robotframework/main
   :target: https://github.com/technogix-terraform/robotframework
   :alt: Last commit

Built With
----------

.. image:: https://img.shields.io/static/v1?label=robotframework&message=4.1.3&color=informational
   :target: http://robotframework.org/
   :alt: Robotframework
.. image:: https://img.shields.io/static/v1?label=boto3&message=1.21.7&color=informational
   :target: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
   :alt: Boto3

Principle
=========

The keywords provided here enables to build easily a set of tests for terraform deployments and/or module. The global principle is the following :

* You've got to have an infrastructure that is up and running. In case you are testing a module, the *terraform* keyword will provide tools to easily set up test infrastructure for the test and remove it once the test is done.

* We provide keywords relying on boto3 to retrieve the infrastructure configuration and test that it matches your expectations.

* Keywords can be logical keywords, that test a simple or complex condition on the infrastructure, such as *Does the bucket exist* or *Does it allow public access* or it can be a comparison keyword that compare the infrastructure to a set of requirements you describe as a dictionary.

One of the key complexity to dealing with secured infrastructure is to provide the test with the adequate credentials. We use keepass as a vault because it enables us to share credentials between a lot of application, to manage our secrets configuration, and it provided an ergonomic HMI to manage secrets. The *keepass* keyword also ease the use of a keepass database for the testing.

Prerequisites
=============

Python and robotframework shall have been installed using pip for example.

The tests shall be able to access the infrastructure for the duration of the test, so it's got to be supplied with a vault. We currently use keepass. You then got to provide temporarily a keepass database and a key file.

Examples
========

The following steps enables to build a robotframework test case using the provided keywords. This deployment tests a terraform module by :

* Building a test deployment using the module

* Testing the resulting infrastructure by comparing it to a target requirement

* Remove the deployment

Loading keywords
----------------

Load the required keywords in the test case :

.. code:: robotframework

    *** Settings ***
    Library         technogix_iac_keywords.terraform
    Library         technogix_iac_keywords.keepass
    Library         technogix_iac_keywords.<keyword>
    # Load other keywords, for example the one provided your expected infrastructure description
    Library         ./data.py

Declaring tests case parameters
-------------------------------

Set up the global variables that will be useful all along the tests. They can be constants, or can be provided by the robotframework command line with the syntax --variable variablename:variable_value

.. code:: robotframework

    *** Variables ***
    # From the command line
    ${KEEPASS_DATABASE}                 ${vaultdatabase}
    ${KEEPASS_KEY}                      ${vaultkey}
    ${KEEPASS_PRIVILEGED_KEY_ENTRY}     /keepass/aws/key/entry/path
    # Constants
    ${KEEPASS_PRIVILEGED_USERNAME}      /keepass/aws/username/entry/path
    ${KEEPASS_ACCOUNT}                  /keepass/aws/account/entry/path
    ${REGION}                           eu-west-1

Preparing environment
---------------------

Prepare environment for all test by retreiving secrets, initializing keywords with credentials, configure deployment

.. code:: robotframework

    *** Test Cases ***
    Prepare Environment
        [Documentation]         Retrieve privileged credential from database and initialize python tests keywords
    # Load secrets from keepass database
        ${privileged_access}    Load Keepass Database Secret      ${KEEPASS_DATABASE}     ${KEEPASS_KEY}  ${KEEPASS_PRIVILEGED_KEY_ENTRY}    username
        ${privileged_secret}    Load Keepass Database Secret      ${KEEPASS_DATABASE}     ${KEEPASS_KEY}  ${KEEPASS_PRIVILEGED_KEY_ENTRY}    password
        ${privileged_name}      Load Keepass Database Secret      ${KEEPASS_DATABASE}     ${KEEPASS_KEY}  ${KEEPASS_PRIVILEGED_USERNAME}     username
        ${account}              Load Keepass Database Secret      ${KEEPASS_DATABASE}     ${KEEPASS_KEY}  ${KEEPASS_ACCOUNT}          password
    # Provide credentials to keyword as initialization. You can provide them as username / access key or as aws cli profile name
        Initialize Terraform    ${REGION}   ${privileged_access}   ${privileged_secret}
        Initialize <Keyword>    None        ${privileged_access}   ${privileged_secret}    ${REGION}
        Initialize KMS          None        ${privileged_access}   ${privileged_secret}    ${REGION}
    # Build the dictionary of variables that will be provided to the terraform test deployment
        ${TF_PARAMETERS}=       Create Dictionary   account=${account}    service_principal=${privileged_name}
    # Export the information the other tests will use
        Set Global Variable     ${TF_PARAMETERS}

Sequence tests
--------------

Perform the test by deploying infrastructure, retrieve terraform test, load expected infrastructure data, compare the real infrastructure to the expected one and remove the test infrastructure


.. code:: robotframework

    Test Infrastructure
        [Documentation]         Launch Test Deployment And Check That The AWS Infrastructure Match Specifications
    # Build a .tfvars file containing the variables described in ${TF_PARAMETERS} directory and launch the terraform deployment described in ${DEPLOYMENT_DIR}
        Launch Terraform Deployment                 ${DEPLOYMENT_DIR}   ${TF_PARAMETERS}
    # Load the resulting tfstate content
        ${states}   Load Terraform States           ${DEPLOYMENT_DIR}
    # Build the required infrastructure state as a dictionary
        ${specs}    Load Multiple Test Data         ${states['test']['outputs']['repositories']['value']}
    # Compare each part of the expected infrastructure to the deployed infrastructure
        Repository Shall Exist And Match            ${specs['repositories']}
        Key Shall Exist And Match                   ${specs['keys']}
    # Destroy test infrastructure
        [Teardown]  Destroy Terraform Deployment    ${CURDIR}/../data/multiple    ${TF_PARAMETERS}


Organization
============

* The *keyword* directory contains the robotframework keywords associated to each infrastructure service. They are built to be easily understandable and modifiable, and use by a wide community.

* The *tools* directory contains the python functions on which the keywords rely to fulfill their missions. They can be more complex.

Issues
======

.. image:: https://img.shields.io/github/issues/technogix-terraform/robotframework.svg
   :target: https://github.com/technogix-terraform/robotframework/issues
   :alt: Open issues
.. image:: https://img.shields.io/github/issues-closed/technogix-terraform/robotframework.svg
   :target: https://github.com/technogix-terraform/robotframework/issues
   :alt: Closed issues

Known limitations
=================

Those keywords are intended for relatively small infrastructures, since it most of the times retrieve all elements for analyze and does use pagination to perform a batch analysis.

Roadmap
=======

Contributing
============

.. image:: https://contrib.rocks/image?repo=technogix-terraform/robotframework
   :alt: GitHub Contributors Image

We welcome contributions, do not hesitate to contact us if you want to contribute.

License
=======

This code is under MIT license

Contact
=======

Nadege LEMPERIERE - nadege.lemperiere@technogix.io

Acknowledgments
===============

N.A.