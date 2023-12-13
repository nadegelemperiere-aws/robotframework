""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage aws sso groups tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @12 december 2023
# Latest revision: 12 december 2023
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
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.identitystore import IdentityStoreTools
from tools.compare import compare_dictionaries, remove_type_from_list

# Global variable
IS_TOOLS = IdentityStoreTools()

@keyword("Initialize Identity Store")
# pylint: disable=C0301
def initialize_identity_store(profile = None, access_key = None, secret_key = None, region = None, store = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
        store      (str) : AWS identity center store id
    """
    IS_TOOLS.initialize(profile, access_key, secret_key, region)
    IS_TOOLS.set_identity_store(store)
    logger.info("Initialization performed")
# pylint: enable=C0301

@keyword('Group Shall Exist And Match')
def group_shall_exist_and_match(specs) :
    """ Check that a group exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = IS_TOOLS.list_groups()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for group in result :
            if compare_dictionaries(spec['data'], group) :
                found = True
                logger.info('Group ' + spec['name'] + ' matches group ' + group['DisplayName'])
        if not found : raise Exception('Group ' + spec['name'] + ' does not match')
