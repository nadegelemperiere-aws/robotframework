""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage aws cloudfront tasks
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
from tools.cloudfront import CloudfrontTools
from tools.compare import compare_dictionaries, remove_type_from_list

# Global variable
CLOUDFRONT_TOOLS = CloudfrontTools()

@keyword("Initialize Cloudfront")
def intialize_cloudfront(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    CLOUDFRONT_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword('Distribution Shall Exist And Match')
def distribution_shall_exist_and_match(specs) :
    """ Check that an cloudfront distibution exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = CLOUDFRONT_TOOLS.list_distributions()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for distribution in result :
            if compare_dictionaries(spec['data'], distribution) :
                found = True
                logger.info('Distribution ' + spec['name'] + ' matches app ' + distribution['Id'])
        if not found : raise Exception('Distribution ' + spec['name'] + ' does not match')

          @keyword('Cloudfront Shall Connect With Origin Using TLS')
def cloudfront_shall_connect_with_origin_using_tls(minimal):
    """ Check that cloudfront connection to origin ensure minimal TLS version
        ---
        minimal    (str) : Minimal allowed version
    """
    result = CLOUDFRONT_TOOLS.list_distributions()
    result = remove_type_from_list(result, datetime)
    for distribution in result :
        for origin in distribution['DistributionConfig']['Origins']['Items'] :
            for protocol in origin['CustomOriginConfig']['OriginSslProtocols']['Items'] :
                version=protocol[4:len(protocol)]
                if float(version) < float(minimal) :
                    raise Exception('Distribution ' + distribution['Id'] + \
                        ' does not match the required minimal TLS version')

@keyword('Cloudfront Viewer Shall Redirect Http To Https')
def cloudfront_viewer_shall_redirect_http_to_https():
    """ Check that cloudfront viewer redirects http to https
    """
    result = CLOUDFRONT_TOOLS.list_distributions()
    result = remove_type_from_list(result, datetime)
    for distribution in result :
        protoc = distribution['DistributionConfig']['DefaultCacheBehavior']['ViewerProtocolPolicy']
        if protoc not in ('redirect-to-https', 'https-only') :
            raise Exception('Distribution ' + distribution['Id'] + \
                ' does not redirect http to https')

@keyword('Cloudfront Shall Enforce Https To Its Origin')
def cloudfront_shall_enforce_https_to_its_origin():
    """ Check that cloudfront traffic with its origin is https
    """
    result = CLOUDFRONT_TOOLS.list_distributions()
    result = remove_type_from_list(result, datetime)
    for distribution in result :
        for origin in distribution['DistributionConfig']['Origins']['Items'] :
            if origin['CustomOriginConfig']['OriginProtocolPolicy'] != 'https-only' :
                raise Exception('Distribution ' + distribution['Id'] + \
                    ' communicate with one of its origin without https ')


@keyword('Cloudfront Shall Have Logging Enabled')
def cloudfront_shall_have_logging_enabled():
    """ Check that cloudfront distribution allows logging
    """
    result = CLOUDFRONT_TOOLS.list_distributions()
    result = remove_type_from_list(result, datetime)
    for distribution in result :
        logger.info(dumps(distribution))
        if not 'Logging' in distribution['DistributionConfig'] :
            raise Exception('Distribution ' + distribution['Id'] + \
                ' does not have logging activated')
        if not 'Enabled' in distribution['DistributionConfig']['Logging'] :
            raise Exception('Distribution ' + distribution['Id'] + \
                ' does not have logging activated')
        if not distribution['DistributionConfig']['Logging']['Enabled'] :
            raise Exception('Distribution ' + distribution['Id'] + \
                ' does not have logging activated')
