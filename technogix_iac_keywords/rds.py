""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage relational database tasks
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
from tools.rds import RDSTools
from tools.sns import SNSTools

# Global variable
RDS_TOOLS = RDSTools()
RDS_SNS_TOOLS = SNSTools()

@keyword("Initialize RDS")
def intialize_rds(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    RDS_TOOLS.initialize(profile, access_key, secret_key, region)
    RDS_SNS_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info('Initialization performed')

@keyword("RDS Databases Shall Be Encrypted")
def rds_database_encrypted() :
    """ Check that all rds databases are encrypted """
    result = RDS_TOOLS.list_all_databases()
    for dbase in result :
        if not dbase['StorageEncrypted'] :
            raise Exception('Database ' + dbase['DBInstanceIdentifier'] + ' is not encrypted')

@keyword("Database Shall Use Multiple Availability Zone")
def rds_database_shall_use_multiple_availability_zone() :
    """ Check that all rds databases use multiple availiblity zone """
    result = RDS_TOOLS.list_all_databases()
    for dbase in result :
        logger.debug(dumps(dbase))
        raise Exception('Database found : should set up the keyword')

@keyword("Database Shall Allow Minor Version Auto Upgrade")
def rds_database_shall_allow_minor_version_auto_upgrade() :
    """ Check that all rds databases allow automatic minor upgrade  """
    result = RDS_TOOLS.list_all_databases()
    for dbase in result :
        logger.debug(dumps(dbase))
        raise Exception('Database found : should set up the keyword')

@keyword("Database Shall Set Backup Retention Policy")
def rds_database_shall_set_backup_retention_policy() :
    """ Check that all rds databases set retention policy  """
    result = RDS_TOOLS.list_all_databases()
    for dbase in result :
        logger.debug(dumps(dbase))
        raise Exception('Database found : should set up the keyword')

@keyword('Database Events Shall Be Notified To At Least One Person')
def database_events_shall_be_notified_to_at_least_one_person() :
    """ Test that each alarm has an associated subscriber
    """
    result = RDS_TOOLS.list_event_subscriptions()
    for alarm in result :
        topic = RDS_SNS_TOOLS.get_topic(alarm['SnsTopicArn'])
        if int(topic['Attributes']['SubscriptionsConfirmed']) < 1 :
            raise  Exception('Event ' + alarm['CustomerAwsId'] + \
                ' topic have no confirmed subscription')

@keyword('Database Events Shall Be Enabled For')
def database_events_shall_be_enabled_for(ltype) :
    """ Test that alarms includes events from instances
    """
    result = RDS_TOOLS.list_event_subscriptions()
    for alarm in result :
        if alarm['SourceType'] == ltype and len(alarm['SourceIdsList']) != 0 :
            raise Exception('Database event ' + alarm['CustomerAwsId'] + \
            ' does not include all database instance')
