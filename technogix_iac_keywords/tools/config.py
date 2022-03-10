""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage cloudtrail tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# Aws includes
from boto3 import Session

class ConfigTools :
    """ Class providing tools to check AWS config compliance """

    # ConfigService session
    m_session = None

    # ConfigService client
    m_client = None

    def __init__(self):
        """ Constructor """
        self.m_session = None
        self.m_client = None

    def initialize(self, profile, access_key, secret_key, region) :
        """ Initialize session  from credentials
            Profile or access_key/secret_key shall be provided
            ---
            profile    (str) : AWS cli profile for SSO users authentication in aws
            access_key (str) : Access key for IAM users authentication in aws
            secret_key (str) : Secret key associated to the previous access key
            region     (str) : AWS region to use
        """
        if profile is not None :
            self.m_session = Session(profile_name=profile, region_name=region)
        else :
            self.m_session = Session(aws_access_key_id=access_key, \
                aws_secret_access_key=secret_key, region_name=region)
        self.m_client = self.m_session.client('config')

    def list_recorders(self) :
        """ List config recorders in AWS account """

        result = []

        response = self.m_client.describe_configuration_recorders()
        for recorder in response['ConfigurationRecorders'] :
            status = self.m_client.describe_configuration_recorder_status(\
                ConfigurationRecorderNames=[recorder['name']])
            recorder['Status'] = status['ConfigurationRecordersStatus'][0]['recording']

        result = result + response['ConfigurationRecorders']

        return result
