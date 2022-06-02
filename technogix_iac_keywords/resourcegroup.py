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
from json import dumps

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.resourcegroup import ResourceGroupTools
from tools.compare import compare_dictionaries

# Global variable
RG_TOOLS = ResourceGroupTools()

@keyword('Initialize Resource Group')
def intialize_resource_group(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    RG_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info('Initialization performed')

@keyword('Resource Group Shall Exist And Match')
def resource_group_shall_exist_and_match(specs) :
    """ Check that a resource group exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = RG_TOOLS.list_groups()
    for spec in specs :
        found = False
        for group in result :
            if compare_dictionaries(spec['data'], group) :
                found = True
                logger.info('Resource group ' + spec['name'] + \
                    ' matches resource group ' + group['Name'])
        if not found : raise Exception('Resource group ' + spec['name'] + ' does not match')


@keyword('Resource Group Shall Not Exist And Match')
def resource_group_shall_not_exist_and_match(specs) :
    """ Check that no resource group exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = RG_TOOLS.list_groups()
    for spec in specs :
        found = False
        for group in result :
            if compare_dictionaries(spec['data'], group) :
                found = True
                name = group['Name']
                logger.info('Resource group ' + spec['name'] + 'matches group ' + name)
                raise Exception('Resource group ' + spec['name'] + ' matches group ' + name)
        if not found : logger.info('Resource group ' + spec['name'] + ' does not match')


@keyword('Resources Shall Be Tagged')
def resources_shall_be_tagged() :
    """ Tests that resources are tagged """
    result = RG_TOOLS.list_resources()
    for rsc in result:
        logger.info(dumps(rsc))
        if not 'Tags' in rsc :
            raise Exception('Resource ' + rsc['ResourceARN'] + ' does not have tags')
        if len(rsc['Tags']) == 0 :
            raise Exception('Resource ' + rsc['ResourceARN'] + ' does not have tags')
