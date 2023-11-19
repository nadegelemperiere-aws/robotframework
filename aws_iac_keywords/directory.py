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
from datetime import datetime
from json import dumps

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.directory import DirectoryTools
from tools.compare import compare_dictionaries, remove_type_from_dictionary

# Global variable
DIRECTORY_TOOLS = DirectoryTools()

@keyword('Initialize Directory')
def intialize_directory(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    DIRECTORY_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info('Initialization performed')

@keyword('Directory Shall Exist And Match')
def directory_shall_exist_and_match(specs) :
    """ Check that a directory exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = DIRECTORY_TOOLS.list_directories()
    for spec in specs :
        found = False
        for directory in result :
            directory = remove_type_from_dictionary(directory,datetime)
            if compare_dictionaries(spec['data'], directory) :
                found = True
                logger.info('Directory ' + spec['name'] + ' matches directory ' + directory['Name'])
        if not found : raise Exception('Directory ' + spec['name'] + ' does not match')

@keyword('No Directory In Regions')
def no_directory_in_regions(regions, access_key, secret_key) :
    """ Check that no resource exists in regions other than the ones provided
        ---
        resions    (list) : List of regions not allowed for hosting
        access_key (str)  : Access key for IAM users authentication in aws
        secret_key (str)  : Secret key associated to the previous access key
    """
    local_tools = DirectoryTools()
    for region in regions :
        local_tools.initialize(None, access_key, secret_key, region = region)
        directories = local_tools.list_directories()
        if len(directories) != 0 : raise Exception('Found key ' + dumps(directories[0]) + \
            ' in region ' + region)
