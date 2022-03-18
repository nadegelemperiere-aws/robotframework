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
from sys import path as syspath
from os import path
from json import dumps

# Robotframework includes
from robot.api import logger
ROBOT = False

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool

class SSOTools(Tool) :
    """ Class providing tools to check AWS SSO compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('sso-admin')
        self.m_is_global = True

    def list_permission_sets(self, instance) :
        """ List permission sets on a given instance
            ---
            instance (str)  : Instance arn
            ---
            returns (list)  : List of all permission sets on the instance
        """

        result = []

        if self.m_is_active['sso-admin'] :
            shall_continue = True
            marker = None
            while shall_continue :
                if marker is not None :
                    response = self.m_clients['sso-admin'].list_permission_sets(\
                        InstanceArn=instance, NextToken = marker)
                else :
                    response = self.m_clients['sso-admin'].list_permission_sets(\
                        InstanceArn=instance)
                for arn in response['PermissionSets'] :
                    desc = self.m_clients['sso-admin'].describe_permission_set(\
                        InstanceArn=instance, PermissionSetArn=arn)
                    policy = self.m_clients['sso-admin'].get_inline_policy_for_permission_set( \
                        InstanceArn=instance, PermissionSetArn=arn)
                    tags = self.m_clients['sso-admin'].list_tags_for_resource(\
                        InstanceArn=instance, ResourceArn=arn)
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

        if self.m_is_active['sso-admin'] :
            shall_continue = True
            marker = None
            while shall_continue :
                if marker is not None   : response = self.m_clients['sso-admin'].list_instances(\
                    NextToken = marker)
                else                    : response = self.m_clients['sso-admin'].list_instances()
                result = result + response['Instances']
                if 'NextToken' in response  : marker = response['NextToken']
                else                        : shall_continue = False

        return result
