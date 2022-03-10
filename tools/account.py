""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Tool functions used by analyzer keywords
# -------------------------------------------------------
# Nadège LEMPERIERE, @17 october 2021
# Latest revision: 17 october 2021
# --------------------------------------------------- """

# Boto3 includes
from boto3 import Session

class AccountTools :
    """ Class providing tools to check AWS account compliance """

    # Account session
    m_session = None

    # Account client
    m_account_client = None
    m_organization_client = None

    def __init__(self):
        """ Constructor """
        self.m_session = None
        self.m_account_client = None
        self.m_organization_client = None

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
        self.m_account_client = self.m_session.client('account')
        self.m_organization_client = self.m_session.client('organizations')

    def list_accounts(self) :
        """ List all accounts in organization """

        result = []

        shall_continue = True
        marker = None
        while shall_continue :
            if marker is not None   :
                response = self.m_organization_client.list_accounts( NextToken = marker)
            else                    :
                response = self.m_organization_client.list_accounts()
            for account in response['Accounts'] : result.append(account)
            if 'nextToken' in response  : marker = response['nextToken']
            else                        : shall_continue = False

        return result

    def get_security_contact(self, account, is_management = False) :
        """ Get security contact associated to account """

        result = ""

        try :
            if is_management :
                response = self.m_account_client.get_alternate_contact(\
                    AlternateContactType='SECURITY')
                if 'AlternateContact' in response :
                    result = response['AlternateContact']['EmailAddress']
            else :
                response = self.m_account_client.get_alternate_contact(AccountId=account, \
                    AlternateContactType='SECURITY')
                if 'AlternateContact' in response :
                    result = response['AlternateContact']['EmailAddress']

        except self.m_account_client.exceptions.ResourceNotFoundException :
            result = ""

        return result
