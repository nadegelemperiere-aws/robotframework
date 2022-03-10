""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage service tasks
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
from tools.sns       import SNSTools
from tools.compare   import compare_dictionaries, remove_type_from_list

# Global variable
SNS_TOOLS    = SNSTools()

@keyword("Initialize SNS")
def intialize_sns(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    SNS_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")


@keyword('Subscriptions Shall Exist And Match')
def subscriptions_shall_exist_and_match(specs) :
    """ Check that a subscription exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = SNS_TOOLS.list_subscriptions()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for subscription in result :
            if compare_dictionaries(spec['data'], subscription) :
                found = True
                name = subscription['SubscriptionArn']
                logger.info('Subscription ' + spec['name'] + ' matches subscription ' + name)
        if not found : raise Exception('Subscription ' + spec['name'] + ' does not match')


@keyword('Topics Shall Exist And Match')
def topics_shall_exist_and_match(specs) :
    """ Check that a topic exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = SNS_TOOLS.list_topics()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for topic in result :
            if compare_dictionaries(spec['data'], topic) :
                found = True
                logger.info('Topic ' + spec['name'] + ' matches topic ' + topic['TopicArn'])
        if not found : raise Exception('Topic ' + spec['name'] + ' does not match')
