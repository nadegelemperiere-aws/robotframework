""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage aws cloudfront tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @17 october 2021
# Latest revision: 17 october 2021
# ---------------------------------------------------- """

# System includes
from os import path
from sys import path as syspath
from datetime import datetime

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.cloudfront import CloudfrontTools
from tools.compare import compare_dictionaries, remove_type_from_list

# Global variable
CLOUDFRONT_TOOLS = CloudfrontTools()

@keyword("Initialize Cloudfront")
def intialize_cloudfront(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    CLOUDFRONT_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword('Distribution Shall Exist And Match')
def distribution_shall_exist_and_match(specs) :
    """ Check that an cloudfront distibution exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = CLOUDFRONT_TOOLS.list_distributions()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for distribution in result :
            if compare_dictionaries(spec['data'], distribution) :
                found = True
                logger.info('Distribution ' + spec['name'] + ' matches app ' + distribution['Id'])
        if not found : raise Exception('Distribution ' + spec['name'] + ' does not match')
