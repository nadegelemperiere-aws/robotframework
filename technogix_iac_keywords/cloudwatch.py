""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage cloudwatch tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path
from datetime import datetime

# Robotframework includec
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.cloudwatch   import CloudwatchTools
from tools.sns          import SNSTools
from tools.compare      import compare_dictionaries, remove_type_from_list

# Global variable
CLOUDWATCH_TOOLS        = CloudwatchTools()
CLOUDWATCH_SNS_TOOLS    = SNSTools()

@keyword("Initialize Cloudwatch")
def intialize_cloudwatch(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    CLOUDWATCH_TOOLS.initialize(profile, access_key, secret_key, region)
    CLOUDWATCH_SNS_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword('Loggroups Shall Exist And Match')
def loggroups_shall_exist_and_match(specs) :
    """ Test that a loggroup exists that matches specifications
    ---
        specs    (list) : List of specifications to consider
    """
    result = CLOUDWATCH_TOOLS.list_groups()
    for spec in specs :
        found = False
        for group in result :
            if compare_dictionaries(spec['data'], group) :
                found = True
                logger.info('Loggroups ' + spec['name'] + ' matches flow ' + group['logGroupName'])
        if not found :
            raise Exception('Loggroups ' + spec['name'] + ' does not match')

@keyword('Metrics Shall Exist And Match')
def metrics_shall_exist_and_match(specs) :
    """ Test that a metric exists that matches specifications
    ---
        specs    (list) : List of specifications to consider
    """

    result = CLOUDWATCH_TOOLS.list_metric_filters()
    for spec in specs :
        found = False
        for metric in result :
            if compare_dictionaries(spec['data'], metric) :
                found = True
                logger.info('Metric ' + spec['name'] + ' matches metric ' + metric['filterName'])
        if not found : raise Exception('Metric ' + spec['name'] + ' does not match')

@keyword('Alarms Shall Exist And Match')
def alarms_shall_exist_and_match(specs) :
    """ Test that an alarm exists that matches specifications
    ---
        specs    (list) : List of specifications to consider
    """
    result = CLOUDWATCH_TOOLS.list_metric_alarms()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for alarm in result :
            if compare_dictionaries(spec['data'], alarm) :
                found = True
                logger.info('Alarm ' + spec['name'] + ' matches alarm ' + alarm['AlarmName'])
        if not found : raise Exception('Alarm ' + spec['name'] + ' does not match')


@keyword('Alarms Shall Be Notified To At Least One Person')
def alarms_shall_be_notified_to_at_least_one_person() :
    """ Test that each alarm has an associated subscriber
    """
    result = CLOUDWATCH_TOOLS.list_metric_alarms()
    result = remove_type_from_list(result, datetime)
    for alarm in result :
        if not alarm['ActionsEnabled'] :
            raise  Exception('Alarm ' + alarm['AlarmName'] + ' has no actions enabled')
        if not 'AlarmActions' in alarm:
            raise  Exception('Alarm ' + alarm['AlarmName'] + ' has no alarm actions enabled')
        for action in alarm['AlarmActions'] :
            topic = CLOUDWATCH_SNS_TOOLS.get_topic(action)
            if int(topic['Attributes']['SubscriptionsConfirmed']) < 1 :
                raise  Exception('Alarm ' + alarm['AlarmName'] + \
                    ' topic have no confirmed subscription')
