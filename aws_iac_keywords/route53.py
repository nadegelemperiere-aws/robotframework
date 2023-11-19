""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage aws route53 tasks
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
from tools.route53 import Route53Tools
from tools.compare import compare_dictionaries, remove_type_from_list

# Global variable
ROUTE53_TOOLS = Route53Tools()

@keyword("Initialize Route53")
def intialize_route53(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    ROUTE53_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword('Record Shall Exist And Match')
def record_shall_exist_and_match(specs) :
    """ Check that an route53 record exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = ROUTE53_TOOLS.list_records()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for record in result :
            if compare_dictionaries(spec['data'], record) :
                found = True
                logger.info('Record ' + spec['name'] + ' matches app ' + record['Name'])
        if not found : raise Exception('Record ' + spec['name'] + ' does not match')
