""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage aws account tasks
# Requires AWS rights on account:*
# -------------------------------------------------------
# Nadège LEMPERIERE, @17 october 2021
# Latest revision: 17 october 2021
# ---------------------------------------------------- """

# System includes
from os import path
from sys import path as syspath

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.account import AccountTools

# Global variable
ACCOUNT_TOOLS = AccountTools()

@keyword("Initialize Account")
def intialize_account(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    ACCOUNT_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword("Security Contact Shall Exist")
def check_security_contact(mgt_account) :
    """ Check that an AWS account has security contact
        ---
        mgt_account (str) : Account to check for security contact
    """
    result = ACCOUNT_TOOLS.list_accounts()
    for account in result :
        test = ACCOUNT_TOOLS.get_security_contact(account['Id'], account['Id'] == mgt_account)
        if len(test) == 0 : raise Exception("No security contact found")
