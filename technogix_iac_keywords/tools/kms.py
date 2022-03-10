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

# System includes
from json import loads

# Aws includes
from boto3 import Session

class KMSTools :
    """ Class providing tools to check AWS KMS compliance """

    # KMS session
    m_session = None

    # KMS client
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
            self.m_session = Session(profile_name=profile, region_name = region)
        elif access_key is not None and secret_key is not None :
            self.m_session = Session(aws_access_key_id=access_key, \
                aws_secret_access_key=secret_key, region_name = region)
        else :
            self.m_session = Session(region_name = region)
        self.m_client = self.m_session.client('kms')

    def list_keys(self) :
        """ List all keys for account """

        result = []

        paginator = self.m_client.get_paginator('list_keys')
        response_iterator = paginator.paginate()
        for response in response_iterator :
            for key in response['Keys']     :
                details = self.m_client.describe_key(KeyId = key['KeyId'])
                details = details['KeyMetadata']
                policy = self.m_client.get_key_policy(KeyId = key['KeyId'], PolicyName='default')
                tags = []
                if details['KeyManager'] == 'CUSTOMER' :
                    # If not, the service principal will not have the right to retrieve tags
                    shall_continue = True
                    marker = None
                    while shall_continue :
                        kid = key['KeyId']
                        if marker is not None   :
                            response = self.m_client.list_resource_tags(KeyId = kid, \
                                NextToken = marker)
                        else :
                            response = self.m_client.list_resource_tags(KeyId = kid)
                        tags = tags + response['Tags']
                        if 'NextToken' in response          : marker = response['NextToken']
                        else                                : shall_continue = False
                details['Policy'] = loads(policy['Policy'])
                details['Tags'] = tags
                result.append(details)

        return result

    def get_rotation(self, key) :
        """ Get rotation status for key
            ---
            key (dict) : Kay to analyze
        """

        response = self.m_client.get_key_rotation_status(KeyId = key['KeyId'])
        return response
