""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage ec2 tasks
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
from tools.sso import SSOTools
from tools.compare import compare_dictionaries

# Global variable
SSO_TOOLS = SSOTools()

@keyword('Initialize SSO')
def intialize_ec2(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    SSO_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info('Initialization performed')

@keyword('Permission Set Shall Exist And Match')
def permission_set_shall_exist_and_match(specs) :
    """ Check that a permission exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = SSO_TOOLS.list_instances()
    logger.debug(dumps(result))
    if len(result) != 1 :
        raise Exception( str(len(result)) + ' SSO instances found')
    instance = result[0]['InstanceArn']
    for spec in specs :
        found = False
        result = SSO_TOOLS.list_permission_sets(instance)
        for permission in result :
            if compare_dictionaries(spec['data'], permission) :
                found = True
                name = permission['Name']
                logger.info('Permission set ' + spec['name'] + ' matches permission ' + name)
    if not found : raise Exception('Permission does not match')
