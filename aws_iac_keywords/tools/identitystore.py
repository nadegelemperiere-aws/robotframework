""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Tool functions used by identity store keywords
# -------------------------------------------------------
# Nadège LEMPERIERE, @12 december 2023
# Latest revision: 12 december 2023
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool

# pylint: disable=R0916, R0904
class IdentityStoreTools(Tool) :
    """ Class providing tools to check AWS IAM compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('identitystore')
        self.m_is_global = True
        self.m_is_id = None

    def set_identity_store(self, store) :
        """ Set identity center store id
        ---
        store (str) : AWS identity center store id
        """
        self.m_is_id = store

    def list_groups(self) :
        """ List all groups in AWS sso identity store """

        result = []

        if self.m_is_active['identitystore'] :
            paginator = self.m_clients['identitystore'].get_paginator('list_groups')
            response_iterator = paginator.paginate(IdentityStoreId=self.m_is_id)
            for response in response_iterator :
                result = result + response['Groups']

        return result

# pylint: enable=R0916, R0904
