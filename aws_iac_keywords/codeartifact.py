""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage CODEARTIFACT tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path
from json import dumps

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.codeartifact import CodeartifactTools

# Global variable
CODEARTIFACT_TOOLS     = CodeartifactTools()

@keyword("Initialize Codeartifact")
def intialize_codeartifact(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    CODEARTIFACT_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword('No Codeartifact Repository In Regions')
def no_codeartifact_repository_in_regions(regions, access_key, secret_key) :
    """ Check that no resource exists in provided regions
        ---
        regions    (list) : List of regions not allowed for hosting
        access_key (str)  : Access key for IAM users authentication in aws
        secret_key (str)  : Secret key associated to the previous access key
    """
    local_tools = CodeartifactTools()
    for region in regions :
        local_tools.initialize(None, access_key, secret_key, region = region)
        repos = local_tools.list_repositories()
        if len(repos) != 0 : raise Exception('Found codeartifact repository ' + dumps(repos[0]) + \
            ' in region ' + region)
