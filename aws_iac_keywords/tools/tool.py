""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Generic tool function containing shared tools structure
# -------------------------------------------------------
# Nadège LEMPERIERE, @17 october 2021
# Latest revision: 17 october 2021
# --------------------------------------------------- """

# System includes
from json import dumps

# Boto3 includes
from boto3 import Session

# Robotframework includes
from robot.api import logger
ROBOT = False

class Tool :
    """ Class providing tools to check AWS account compliance """

    # Session
    m_session = None

    # Services
    m_services = []

    # Services clients
    m_clients = {}

    # Are services active
    m_is_active = {}

    # Is service global
    m_is_global = False

    def __init__(self):
        """ Constructor """
        self.m_session = None
        self.m_client = {}
        self.m_is_service_active = {}
        self.m_services = []

    def initialize(self, profile, access_key, secret_key, region) :
        """ Initialize session  from credentials
            Profile or access_key/secret_key shall be provided
            ---
            services   (str) : List of services to initialize
            profile    (str) : AWS cli profile for SSO users authentication in aws
            access_key (str) : Access key for IAM users authentication in aws
            secret_key (str) : Secret key associated to the previous access key
            region     (str) : AWS region to use
        """

        # Create session
        if profile is not None :
            self.m_session = Session(profile_name=profile, region_name = region)
        elif access_key is not None and secret_key is not None :
            self.m_session = Session(aws_access_key_id=access_key, \
                aws_secret_access_key=secret_key, region_name = region)
        else :
            self.m_session = Session(region_name = region)

        # Create a client for each service if service is available in region
        for service in self.m_services :
            logger.debug(service)
            regions = self.m_session.get_available_regions(service)
            logger.debug(dumps(regions))
            logger.debug(region)
            if not region in regions and not self.m_is_global:
                logger.debug('Client not available for service : ' + service + \
                    ' in region ' + region)
                self.m_is_active[service] = False
                self.m_clients[service] = None
            else :
                logger.debug('Creating client for service : ' + service + \
                    ' in region ' + region)
                self.m_is_active[service] = True
                self.m_clients[service] = self.m_session.client(service)
