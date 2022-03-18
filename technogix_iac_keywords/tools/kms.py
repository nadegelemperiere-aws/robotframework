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
from sys import path as syspath
from os import path
from json import loads

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool

# pylint: disable=R1702
class KMSTools(Tool) :
    """ Class providing tools to check AWS KMS compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('kms')

    def list_keys(self) :
        """ List all keys for account """

        result = []

        if self.m_is_active['kms'] :
            paginator = self.m_clients['kms'].get_paginator('list_keys')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                for key in response['Keys']     :
                    details = self.m_clients['kms'].describe_key(KeyId = key['KeyId'])
                    details = details['KeyMetadata']
                    policy = self.m_clients['kms'].get_key_policy(KeyId = key['KeyId'], \
                        PolicyName='default')
                    tags = []
                    if details['KeyManager'] == 'CUSTOMER' :
                        # If not, the service principal will not have the right to retrieve tags
                        shall_continue = True
                        marker = None
                        while shall_continue :
                            kid = key['KeyId']
                            if marker is not None   :
                                response = self.m_clients['kms'].list_resource_tags(KeyId = kid, \
                                    NextToken = marker)
                            else :
                                response = self.m_clients['kms'].list_resource_tags(KeyId = kid)
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
            key (dict) : Key to analyze
        """

        response = {}
        if self.m_is_active['kms'] :
            response = self.m_clients['kms'].get_key_rotation_status(KeyId = key['KeyId'])

        return response

# pylint: enable=R1702
