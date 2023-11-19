""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage codecommit tasks
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
from tools.codecommit   import CodecommitTools

# Global variable
CODECOMMIT_TOOLS     = CodecommitTools()

@keyword("Initialize Codecommit")
def intialize_codecommit(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    CODECOMMIT_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword("Create Repository In CodeCommit")
def create_repository(repository) :
    """ Create codecommit repository
        ---
        repository (str) : Repository to create
    """
    CODECOMMIT_TOOLS.create_repository(repository)

@keyword("CodeCommit Repository Shall Exist")
def codecommit_repository_shall_exist(repository) :
    """ Tests if a codecommit repository exists
        ---
        repository (str) : Repository to look for
    """
    result = CODECOMMIT_TOOLS.repository_exists(repository)
    if not result : raise Exception('Repository ' + repository + ' should exist')

@keyword("CodeCommit Repository Shall Not Exist")
def repository_not_exists(repository) :
    """ Check that a codecommit repository does not exist
        ---
        repository (str) : Repository to look for
    """
    result = CODECOMMIT_TOOLS.repository_exists(repository)
    if result : raise Exception('Repository ' + repository + ' should not exist')

@keyword("Remove Repository In CodeCommit")
def remove_repository(repository) :
    """ Remove codecommit repository
        ---
        repository (str) : Repository to remove
    """
    CODECOMMIT_TOOLS.remove_repository_if_exists(repository)

@keyword('No Codecommit Repository In Regions')
def no_repository_in_regions(regions, access_key, secret_key) :
    """ Check that no resource exists in provided regions
        ---
        resions    (list) : List of regions not allowed for hosting
        access_key (str)  : Access key for IAM users authentication in aws
        secret_key (str)  : Secret key associated to the previous access key
    """
    local_tools = CodecommitTools()
    for region in regions :
        local_tools.initialize(None, access_key, secret_key, region = region)
        repos = local_tools.list_repositories()
        if len(repos) != 0 : raise Exception('Found codecommit repository ' + dumps(repos[0]) + \
            ' in region ' + region)
