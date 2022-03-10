""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage dynamodb tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @06 october 2021
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
from tools.dynamo import DynamoDBTools
from tools.compare import remove_type_from_list, compare_dictionaries

# Global variable
DYNAMODB_TOOLS = DynamoDBTools()

@keyword("Initialize DynamoDB")
def intialize_dynamodb(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    DYNAMODB_TOOLS.initialize(profile, access_key, secret_key, region=region)
    logger.info("Initialization performed")

@keyword("Create DynamoDB Item")
def create_dynamodb_item(table, item) :
    """ Create item in dynamodb table
        ---
        table   (str) : Table to update
        item    (str) : Item to add to table
    """
    DYNAMODB_TOOLS.create_item(table, item)

@keyword("DynamoDB Item Shall Exist")
def dynamodb_item_shall_exist(table, item) :
    """ Verify that an item exist in a dynamodb table
        ---
        table   (str) : Table to check
        item    (str) : Item to look for
    """

    result = DYNAMODB_TOOLS.object_exists(table, item)
    if not result : raise AssertionError(f"'{item}' should exist.")


@keyword("DynamoDB Item Shall Not Exist")
def dynamodb_item_shall_not_exist(table, item) :
    """ Verify that an item does not exist in a dynamodb table
        ---
        table   (str) : Table to check
        item    (str) : Item to look for
    """
    result = DYNAMODB_TOOLS.object_exists(table, item)
    if result : raise AssertionError(f"'{item}' should not exist.")

@keyword("Remove DynamoDB Item")
def remove_dynamodb_item(table, item) :
    """ Remove an item from a dynamodb table if it exists
        ---
        table   (str) : Table to update
        item    (str) : Item to remove
    """
    DYNAMODB_TOOLS.remove_item(table, item)

@keyword('Tables Shall Exist And Match')
def tables_shall_exist_and_match(specs) :
    """ Check that a dynamodb table exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = DYNAMODB_TOOLS.list_tables()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for table in result :
            if compare_dictionaries(spec['data'], table) :
                found = True
                logger.info('Table ' + spec['name'] + ' matches table ' + table['TableName'])
        if not found : raise Exception('Table ' + spec['name'] + ' does not match')
