""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage ec2 tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# Aws includes
from boto3 import Session

class ResourceGroupTools :
    """ Class providing tools to check AWS resource groups compliance """

    # Resource group session
    m_session = None

    # Resource group client
    m_client = None

    def __init__(self):
        """ Constructor """
        self.m_session = None
        self.m_client = None

    def initialize(self, profile, access_key, secret_key, region = None) :
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
        self.m_client = self.m_session.client('resource-groups')

    def list_groups(self) :
        """ List all resource groups """

        result = []

        paginator = self.m_client.get_paginator('list_groups')
        group_iterator = paginator.paginate()
        for response in group_iterator :
            for group in response['Groups'] :
                group['Resources'] = []
                paginator2 = self.m_client.get_paginator('list_group_resources')
                resource_iterator = paginator2.paginate(Group = group['GroupArn'])
                for resource in resource_iterator :
                    group['Resources'] = group['Resources'] + resource['Resources']

                result.append(group)

        return result
