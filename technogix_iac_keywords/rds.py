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

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.rds import RDSTools

# Global variable
RDS_TOOLS = RDSTools()

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
    logger.info("Initialization performed")

@keyword("RDS Databases Shall Be Encrypted")
def rds_database_encrypted() :
    """ Check that all rds databases are encrypted """
    result = RDS_TOOLS.list_all_databases()
    for dbase in result :
        if not dbase['StorageEncrypted'] :
            raise Exception("Database " + dbase['DBInstanceIdentifier'] + ' is not encrypted')
