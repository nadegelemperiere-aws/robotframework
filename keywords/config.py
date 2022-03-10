""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
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

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), '../')))
from tools.config   import ConfigTools
from tools.compare  import compare_dictionaries

# Global variable
CONFIG_TOOLS    = ConfigTools()

@keyword("Initialize Config")
def intialize_config(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    CONFIG_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword("Config Shall Be Enabled")
def config_activated() :
    """ Tests if config is enabled """
    result = CONFIG_TOOLS.list_recorders()
    is_enabled = False
    for recorder in result :
        if recorder['recordingGroup']['allSupported'] and \
           recorder['recordingGroup']['includeGlobalResourceTypes'] :
            is_enabled = True
    if not is_enabled : raise Exception('No recorder enables full analysis')

@keyword('Recorders Shall Exist And Match')
def recorders_shall_exist_and_match(specs) :
    """ Test that a recorder exists that matches specifications
    ---
        specs    (list) : List of specifications to consider
    """
    result = CONFIG_TOOLS.list_recorders()
    for spec in specs :
        found = False
        for recorder in result :
            if compare_dictionaries(spec['data'], recorder) :
                found = True
                logger.info('Recorder ' + spec['name'] + ' matches recorder ' + recorder['name'])
        if not found : raise Exception('Recorder ' + spec['name'] + ' does not match')
