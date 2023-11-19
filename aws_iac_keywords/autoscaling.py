""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage aws amplify tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @17 october 2021
# Latest revision: 17 october 2021
# ---------------------------------------------------- """

# System includes
from os import path
from sys import path as syspath
from datetime import datetime
from json import dumps

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.autoscaling import AutoScalingTools
from tools.compare import remove_type_from_list

# Global variable
AUTOSCALING_TOOLS = AutoScalingTools()

@keyword("Initialize Autoscaling")
def intialize_autoscaling(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    AUTOSCALING_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword('AutoScaling Group Launch Configuration Shall Use IAM Role')
def autoscaling_group_launch_configuration_shall_use_iam_role() :
    """ Check that an autoscaling group shall use IAM role
    """
    result = AUTOSCALING_TOOLS.list_launch_configuration()
    result = remove_type_from_list(result, datetime)
    for group in result :
        logger.debug(dumps(group))
        raise Exception('Autoscaling launch configuration found : keyword should be developed')

@keyword('AutoScaling Groups Shall Have A Load Balancer')
def autoscaling_group_shall_have_a_load_balancer() :
    """ Check that autoscaling groups have a load balancer """

    result = AUTOSCALING_TOOLS.list_autoscaling_groups()
    result = remove_type_from_list(result, datetime)
    for group in result :
        logger.debug(dumps(group))
        raise Exception('Autoscaling group found : keyword should be developed')

@keyword('AutoScaling Groups Shall Use Multiple Availability Zones')
def autoscaling_group_shall_use_multiple_availability_zones() :
    """ Check that autoscaling groups have multiple availability zones"""

    result = AUTOSCALING_TOOLS.list_autoscaling_groups()
    result = remove_type_from_list(result, datetime)
    for group in result :
        logger.debug(dumps(group))
        raise Exception('Autoscaling group found : keyword should be developed')

@keyword('AutoScaling Groups Shall Use An Approved AMI')
def autoscaling_group_shall_use_an_approved_ami() :
    """ Check that autoscaling groups use approved ami """
    result = AUTOSCALING_TOOLS.list_autoscaling_groups()
    result = remove_type_from_list(result, datetime)
    for group in result :
        logger.debug(dumps(group))
        raise Exception('Autoscaling group found : keyword should be developed')

@keyword('AutoScaling Groups Shall Use A Cloudwatch Agent')
def autoscaling_group_shall_use_a_cloudwatch_agent() :
    """ Check that autoscaling group have a cloudwatch agent """

    result = AUTOSCALING_TOOLS.list_autoscaling_groups()
    result = remove_type_from_list(result, datetime)
    for group in result :
        logger.debug(dumps(group))
        raise Exception('Autoscaling group found : keyword should be developed')
