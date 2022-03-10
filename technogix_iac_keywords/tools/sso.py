""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage SSO tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from json import dumps

# Aws includes
from boto3 import Session

# Robotframework includes
from robot.api import logger
ROBOT = False

class SSOTools :
    """ Class providing tools to check AWS SSO compliance """

    # SSO session
    m_session = None

    # SSO client
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
        self.m_client = self.m_session.client('sso-admin')

    def list_permission_sets(self, instance) :
        """ List permission sets on a given instance
            ---
            instance (str)  : Instance arn
            ---
            returns (list)  : List of all permission sets on the instance
        """

        result = []

        shall_continue = True
        marker = None
        while shall_continue :
            if marker is not None :
                response = self.m_client.list_permission_sets(InstanceArn=instance, \
                    NextToken = marker)
            else :
                response = self.m_client.list_permission_sets(InstanceArn=instance)
            for arn in response['PermissionSets'] :
                desc = self.m_client.describe_permission_set(InstanceArn=instance, \
                    PermissionSetArn=arn)
                policy = self.m_client.get_inline_policy_for_permission_set( InstanceArn=instance, \
                    PermissionSetArn=arn)
                tags = self.m_client.list_tags_for_resource(InstanceArn=instance, ResourceArn=arn)
                data = desc['PermissionSet']
                data['InlinePolicy'] = policy['InlinePolicy']
                data['Tags'] = tags['Tags']
                del data['CreatedDate']
                result.append(data)
            if 'NextToken' in response  : marker = response['NextToken']
            else                        : shall_continue = False

        logger.info(dumps(result))

        return result

    def list_instances(self) :
        """ List existing sso instances  """

        result = []

        shall_continue = True
        marker = None
        while shall_continue :
            if marker is not None   : response = self.m_client.list_instances(NextToken = marker)
            else                    : response = self.m_client.list_instances()
            result = result + response['Instances']
            if 'NextToken' in response  : marker = response['NextToken']
            else                        : shall_continue = False

        return result
