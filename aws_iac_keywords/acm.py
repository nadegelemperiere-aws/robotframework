""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage certificates tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path
from datetime import datetime, timezone

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.acm import ACMTools

# Global variable
ACM_TOOLS = ACMTools()

@keyword('Initialize ACM')
def intialize_acm(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    ACM_TOOLS.initialize(profile, access_key, secret_key, region=region)
    logger.info('Initialization performed')

@keyword('SSL Certificates Shall Expire In More Than')
def ssl_certificates_shall_expire_in_more_than(days) :
    """ Retrieve all existing AWS regions other than the input one """

    result = []
    certificates = ACM_TOOLS.list_certificates()
    for cert in certificates :
        remaining_days = (cert['NotAfter'] - datetime.now(timezone.utc)).days
        if remaining_days < int(days) :
            raise Exception('Found certificate that expires in ' + str(remaining_days))

    return result
