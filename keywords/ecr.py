""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage s3 tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path
from datetime import datetime

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), '../')))
from tools.ecr import ECRTools
from tools.compare import compare_dictionaries, remove_type_from_list

# Global variable
ECR_TOOLS = ECRTools()

@keyword("Initialize ECR")
def intialize_s3(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    ECR_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword('Repository Shall Exist And Match')
def repositories_shall_exist_and_match(specs) :
    """ Check that a repository exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = ECR_TOOLS.list_repositories()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for repository in result :
            if compare_dictionaries(spec['data'], repository) :
                found = True
                logger.info('Repository ' + spec['name'] + \
                    ' matches repository ' + repository['repositoryName'])
        if not found : raise Exception('Repository ' + spec['name'] + ' does not match')
