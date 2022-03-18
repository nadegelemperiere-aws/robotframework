""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage keys tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from json import dumps
from os import path
from datetime import datetime

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.kms      import KMSTools
from tools.compare  import compare_dictionaries, remove_type_from_dictionary, remove_type_from_list

# Global variable
KMS_TOOLS    = KMSTools()

@keyword("Initialize KMS")
def intialize_kms(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    KMS_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword("Keys Shall Rotate")
def keys_shall_rotate() :
    """ Test if keys are configured to be rotated """
    result = KMS_TOOLS.list_keys()
    for key in result :
        key = remove_type_from_dictionary(key,datetime)
        logger.info(dumps(key))
        if key['Enabled'] and key['KeyManager'] != 'AWS':
            rotation = KMS_TOOLS.get_rotation(key)
            if not ('KeyRotationEnabled' in rotation and rotation['KeyRotationEnabled']) :
                raise Exception('Key ' + key['KeyId'] + ' does not rotate')

@keyword('Key Shall Exist And Match')
def key_shall_exist_and_match(specs) :
    """ Check that a key exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = KMS_TOOLS.list_keys()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for key in result :
            if compare_dictionaries(spec['data'], key) :
                found = True
        if not found : raise Exception('Key ' + spec['name'] + ' does not match')

@keyword('Enabled Key Shall Be Limited')
def enabled_keys_shall_be_limited(maximal_number) :
    """ Check that active keys are limited
        ---
        maximal_number    (list) : Maximal number of allowed key
    """
    number = 0
    result = KMS_TOOLS.list_keys()
    result = remove_type_from_list(result, datetime)
    for key in result :
        if key['KeyState'] == 'Enabled' and key['KeyManager'] != 'AWS':
            number = number + 1
            logger.debug(dumps(key))

    if number > int(maximal_number) :
        raise Exception(str(number) + ' keys found instead of ' + str(maximal_number))

@keyword('No Key In Regions')
def no_key_in_regions(regions, access_key, secret_key) :
    """ Check that no resource exists in provided regions
        ---
        resions    (list) : List of regions not allowed for hosting
        access_key (str)  : Access key for IAM users authentication in aws
        secret_key (str)  : Secret key associated to the previous access key
    """
    logger.info(dumps(regions))
    local_tools = KMSTools()
    for region in regions :
        local_tools.initialize(None, access_key, secret_key, region = region)
        keys = local_tools.list_keys()
        keys = remove_type_from_list(keys,datetime)
        for key in keys :
            if key['KeyManager'] != 'AWS' :
                if (region != 'eu-west-3' or key['KeyState'] == 'Enabled') :
                    # Exception for eu-west-3, I tried some testing in it, and
                    # therefore there are remaining keys waiting for deletion
                    raise Exception('Found key ' + dumps(key) + \
                        ' in region ' + region)
