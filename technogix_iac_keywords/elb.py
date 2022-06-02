""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage load balancer tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from json import dumps
from os import path

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.elb import ELBTools

# Global variable
ELB_TOOLS = ELBTools()

@keyword('Initialize ELB')
def intialize_elb(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    ELB_TOOLS.initialize(profile, access_key, secret_key, region=region)
    logger.info('Initialization performed')

@keyword('Load Balancers Shall Have TLS Certificate')
def load_balancers_shall_have_tls_certificate() :
    """ Check that load balancers have attached TLS certificate """
    result = ELB_TOOLS.list_load_balancers()
    for lb in result :
        logger.info(dumps(lb))
        for listener in lb['Listeners'] :
            if listener['Protocol'] != 'TCP' and len(listener['Certificates']) == 0 :
                raise Exception('Non TCP listener found without associated certificates')

@keyword('Load Balancers Shall Have SSL Policies Enabled')
def load_balancers_shall_have_ssl_policies_enabled() :
    """ Check that load balancers have latest SSL policies enabled """
    result = ELB_TOOLS.list_load_balancers()
    for lb in result :
        logger.info(dumps(lb))
        for listener in lb['Listeners'] :
            logger.info(dumps(listener))
            raise Exception('Should enhance keyword to check SSL policies on listener')

@keyword('Load Balancers Shall Use HTTPS Listener')
def load_balancers_shall_use_https_listener() :
    """ Check that load balancers have http listeners """
    result = ELB_TOOLS.list_load_balancers()
    for lb in result :
        logger.info(dumps(lb))
        for listener in lb['Listeners'] :
            if listener['Protocol'] != 'TCP' and listener['Protocol'] != 'HTTPS' :
                raise Exception('Listeners other than HTTPS and TLS found')

@keyword('Load Balancer Shall Check For Health')
def load_balancers_shall_check_for_health() :
    """ Check that load balancers have healthcheck activated """
    result = ELB_TOOLS.list_load_balancers()
    for lb in result :
        logger.info(dumps(lb))
        raise Exception('Load balancer found : finalize the keyword')

@keyword('Load Balancer Shall Have Logging Enabled')
def load_balancers_shall_have_logging_enabled() :
    """ Check that load balancers have logging enabled """
    result = ELB_TOOLS.list_load_balancers()
    for lb in result :
        logger.info(dumps(lb))
        raise Exception('Load balancer found : finalize the keyword')
