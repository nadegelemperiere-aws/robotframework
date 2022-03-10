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
syspath.append(path.normpath(path.join(path.dirname(__file__), '../')))
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
