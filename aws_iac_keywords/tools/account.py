""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Tool functions used by analyzer keywords
# -------------------------------------------------------
# Nadège LEMPERIERE, @17 october 2021
# Latest revision: 17 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool

class AccountTools(Tool) :
    """ Class providing tools to check AWS access analyzer compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('account')
        self.m_services.append('organizations')

    def list_accounts(self) :
        """ List all accounts in organization """

        result = []

        if self.m_is_active['organizations'] :
            paginator = self.m_clients['organizations'].get_paginator('list_accounts')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['Accounts']

        return result

    def get_security_contact(self, account, is_management = False) :
        """ Get security contact associated to account """

        result = ""

        try :
            if self.m_is_active['account'] :
                if is_management :
                    response = self.m_clients['account'].get_alternate_contact(\
                        AlternateContactType='SECURITY')
                    if 'AlternateContact' in response :
                        result = response['AlternateContact']['EmailAddress']
                else :
                    response = self.m_clients['account'].get_alternate_contact(AccountId=account, \
                        AlternateContactType='SECURITY')
                    if 'AlternateContact' in response :
                        result = response['AlternateContact']['EmailAddress']

        except self.m_clients['account'].exceptions.ResourceNotFoundException :
            result = ""

        return result
