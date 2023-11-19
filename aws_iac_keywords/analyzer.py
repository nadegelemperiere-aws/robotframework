""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage aws account tasks
# Requires AWS rights on account:*
# -------------------------------------------------------
# Nadège LEMPERIERE, @17 october 2021
# Latest revision: 17 october 2021
# --------------------------------------------------- """

# System includes
from os import path
from sys import path as syspath

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.analyzer import AnalyzerTools

# Global variable
ANALYZER_TOOLS = AnalyzerTools()

@keyword("Initialize Analyzer")
def intialize_analyzer(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    ANALYZER_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword("One Access Analyzer Shall Exist Per Region")
def one_analyzer_per_region(regions) :
    """ Check that an AWS account has security contact
        ---
        regions (str) : List of region to test
    """
    results = {}
    for region in regions :
        results[region] = False

    response = ANALYZER_TOOLS.list_analyzers()
    for analyzer in response :
        for region in regions :
            if analyzer['arn'].find(':' + region + ':') >= 0 :
                results[region] = True

    for region in regions :
        if not results[region] : raise Exception('Could not find analyzer for region ' + region)
