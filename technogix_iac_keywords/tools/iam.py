""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Tool functions used by iam keywords
# -------------------------------------------------------
# Nadège LEMPERIERE, @29 october 2021
# Latest revision: 29 october 2021
# --------------------------------------------------- """

# System includes
from time import sleep
from datetime import datetime, timezone
from sys import path as syspath
from os import path

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool


# pylint: disable=R0916, R0904
class IAMTools(Tool) :
    """ Class providing tools to check AWS IAM compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('iam')
        self.m_is_global = True

    def add_user(self, username) :
        """ Creates new user in aws IAM
            ---
            username (str) : Name of the user to add
        """
        result = {}

        if self.m_is_active['iam'] :
            self.m_clients['iam'].create_user(UserName = username)
            key = self.m_clients['iam'].create_access_key(UserName = username)
            result['access'] = key['AccessKey']['AccessKeyId']
            result['secret'] = key['AccessKey']['SecretAccessKey']

        return result

    def remove_user(self, username) :
        """ Remove user in aws IAM
            ---
            username (str) : Name of the user to remove
        """

        self.remove_user_from_all_groups(username)
        if self.m_is_active['iam'] :
            response = self.m_clients['iam'].list_access_keys(UserName = username)
            for key in response['AccessKeyMetadata'] :
                name = key['UserName']
                kid = key['AccessKeyId']
                self.m_clients['iam'].delete_access_key(UserName = name, AccessKeyId = kid)

        self.m_clients['iam'].delete_user(UserName = username)

    def add_user_to_group(self, username, group) :
        """ Add user to group in aws IAM
            ---
            username (str) : Name of the user to add
            group    (str) : Name of the group to add user to
        """

        if self.m_is_active['iam'] :
            self.m_clients['iam'].add_user_to_group(UserName = username, GroupName = group)
            # Need to sleep for group association  to be spread and recognized when used
            sleep(10)

    def remove_user_from_group( self, username, group) :
        """ Remove user from a given group in aws IAM
            ---
            username (str) : Name of the user to remove
            group    (str) : Name of the group to remove user from
        """

        if self.m_is_active['iam'] :
            paginator = self.m_clients['iam'].get_paginator('list_groups_for_user')
            response_iterator = paginator.paginate(UserName = username)
            for response in response_iterator :
                for grp in response['Groups'] :
                    if group == grp['GroupName'] :
                        self.m_clients['iam'].remove_user_from_group(\
                            UserName = username , GroupName = group)

    def remove_user_from_all_groups(self, username) :
        """ Remove user from all its group in aws IAM
            ---
            username (str) : Name of the user to remove from groups
        """

        if self.m_is_active['iam'] :
            paginator = self.m_clients['iam'].get_paginator('list_groups_for_user')
            response_iterator = paginator.paginate(UserName = username)
            for response in response_iterator :
                for grp in response['Groups'] :
                    grpn = grp['GroupName']
                    self.m_clients['iam'].remove_user_from_group(\
                        UserName = username , GroupName = grpn)

    def get_account_summary(self) :
        """ Retrieve account summary """

        result = {}
        if self.m_is_active['iam'] :
            result = self.m_clients['iam'].get_account_summary()
        return result

    def get_account_password_policy(self) :
        """ Retrieve account summary """

        result = {}
        if self.m_is_active['iam'] :
            response = self.m_clients['iam'].get_account_password_policy()
            result = response['PasswordPolicy']

        return result

    def has_password(self,username) :
        """ Check that user has no password
            ---
            username (str) : Name of the user to analyze
        """
        result = True

        try :
            if self.m_is_active['iam'] :
                profile = self.m_clients['iam'].get_login_profile( UserName=username)
                result = (profile['CreateDate'] is not None)
        except self.m_clients['iam'].exceptions.NoSuchEntityException : result = False

        return result

    def has_virtual_mfa_devices(self, account) :
        """ Check if account has an attached virtual mfa device
            ---
            account (str) : Account to analyze
        """

        result = False

        if self.m_is_active['iam'] :
            paginator = self.m_clients['iam'].get_paginator('list_virtual_mfa_devices')
            response_iterator = paginator.paginate(AssignmentStatus='Assigned')
            for response in response_iterator :
                for device in response['VirtualMFADevices'] :
                    if device['User']['UserId'] == account : result = True

        return result

    def has_permission(self, username) :
        """ Check that user has associated policies
            ---
            username (str) : Name of the user to analyze
        """
        result = False

        if self.m_is_active['iam'] :
            response = self.m_clients['iam'].list_attached_user_policies(UserName=username)
            if len(response['AttachedPolicies']) > 0 : result = True
            response = self.m_clients['iam'].list_user_policies(UserName=username)
            if len(response['PolicyNames']) > 0 : result = True

        return result

    def is_giving_full_admin_privileges(self, policy) :
        """ Check that a policy is giving full administration privilege
            ---
            policy (str) : Name of the policy to analyze
        """

        result = False

        if self.m_is_active['iam'] :
            arn = policy['Arn']
            vid = policy['DefaultVersionId']
            response = self.m_clients['iam'].get_policy_version(PolicyArn=arn,VersionId=vid)
            content = response['PolicyVersion']['Document']['Statement']

            if isinstance(content,str) :
                if content['Effect'] == 'Allow' :
                    if  (   'Resource' in content and
                            (   (isinstance(content['Resource'],str) and \
                                (content['Resource'] == '*')) or \
                                (isinstance(content['Resource'],list) and \
                                    ('*' in content['Resource'])))) and \
                        (   'Action' in content and
                            (   (isinstance(content['Action'],str) and \
                                (content['Action'] == '*')) or \
                                (isinstance(content['Action'],list) and \
                                    ('*' in content['Action'])))) : result = True
            elif isinstance(content,list) :
                for statement in content :
                    if statement['Effect'] == 'Allow' :
                        if  ( 'Resource' in statement and
                                (   (isinstance(statement['Resource'],str) and \
                                    (statement['Resource'] == '*')) or \
                                    (isinstance(statement['Resource'],list) and \
                                        ('*' in statement['Resource'])))) and \
                            (   'Action' in statement and
                                (   (isinstance(statement['Action'],str) and \
                                    (statement['Action'] == '*')) or \
                                    (isinstance(statement['Action'],list) and \
                                        ('*' in statement['Action'])))) : result = True

        return result

    def list_users(self) :
        """ List all users in aws IAM """

        result = []

        if self.m_is_active['iam'] :
            paginator = self.m_clients['iam'].get_paginator('list_users')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['Users']

        return result

    def list_groups(self) :
        """ List all groups in aws IAM """

        result = []

        if self.m_is_active['iam'] :
            paginator = self.m_clients['iam'].get_paginator('list_groups')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['Groups']

        return result

    def list_users_for_group(self, group) :
        """ List all users in aws IAM group
            ---
            group (str) : Name of the group to analyze
        """

        result = []

        users = self.list_users()

        if self.m_is_active['iam'] :
            for user in users :
                paginator = self.m_clients['iam'].get_paginator('list_groups_for_user')
                response_iterator = paginator.paginate(UserName = user['UserName'])
                for response in response_iterator :
                    for grp in response['Groups'] :
                        if grp['GroupName'] == group : result.append(user)

        return result

    def list_attached_policies(self) :
        """ List all attached policies in aws IAM """

        result = []

        if self.m_is_active['iam'] :
            paginator = self.m_clients['iam'].get_paginator('list_policies')
            response_iterator = paginator.paginate(Scope='All', OnlyAttached=True)
            for response in response_iterator :
                result = result + response['Policies']

        return result

    def list_roles_for_policy(self, policy) :
        """ List roles to which policy is attached
            ---
            policy (str) : Name of the policy to analyze
        """

        result = []

        if self.m_is_active['iam'] :
            paginator = self.m_clients['iam'].get_paginator('list_entities_for_policy')
            response_iterator = paginator.paginate(PolicyArn=policy['Arn'])
            for response in response_iterator :
                result = result + response['PolicyRoles']

        return result

    def list_roles(self) :
        """ List roles """

        result = []

        if self.m_is_active['iam'] :
            paginator = self.m_clients['iam'].get_paginator('list_roles')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['Roles']

        return result

    def list_expired_certificates(self) :
        """" List expired certificates """

        result = []

        if self.m_is_active['iam'] :
            paginator = self.m_clients['iam'].get_paginator('list_server_certificates')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                for certificate in response['ServerCertificateMetadataList'] :
                    delay = (certificate['Expiration'] - datetime.now(timezone.utc)).seconds()
                    if delay < 0 : result.append(certificate['ServerCertificateName'])

        return result

    def list_user_access_keys(self, username) :
        """ List all access keys associated to a given user
            ---
            username (str) : Name of the user to analyze
        """

        result = []

        if self.m_is_active['iam'] :
            paginator = self.m_clients['iam'].get_paginator('list_access_keys')
            response_iterator = paginator.paginate(UserName=username)
            for response in response_iterator :
                for key in response['AccessKeyMetadata'] :
                    if key['Status'] == 'Active' :
                        result.append(key)

        return result

    def list_access_keys(self) :
        """ List all access keys """

        result = []

        if self.m_is_active['iam'] :
            paginator = self.m_clients['iam'].get_paginator('list_access_keys')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['AccessKeyMetadata']

        return result

    def list_user_service_credentials(self, username) :
        """ List all service credentials associated to a given user
            ---
            username (str) : Name of the user to analyze
        """

        result = []

        if self.m_is_active['iam'] :
            response = self.m_clients['iam'].list_service_specific_credentials(UserName=username)
            for credential in response['ServiceSpecificCredentials'] :
                result.append(credential)

        return result

    def parse_credential_report(self) :
        """ Generate, retrieve and parse credential report"""

        result = {}

        # Generate and retrieve report
        if self.m_is_active['iam'] :
            # Generate and retrieve report
            self.m_clients['iam'].generate_credential_report()

            is_ready = False
            while not is_ready :
                try :
                    response    = self.m_clients['iam'].get_credential_report()
                except self.m_clients['iam'].exceptions.CredentialReportNotReadyException :
                    is_ready = False
                is_ready = True

            # Decode content
            content_string = str(response['Content'].decode('ascii'))
            content = []
            for row in content_string.split('\n') :
                content.append(row.split(','))
            result['content'] = content

            # Associate header to column index
            columns = {}
            for i_col,col in enumerate(content[0]) :
                columns[col] = i_col
            result['columns'] = columns

        return result

# pylint: enable=R0916, R0904
