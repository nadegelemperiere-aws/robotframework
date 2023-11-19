""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage code artifact tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool

class CodeartifactTools(Tool) :
    """ Class providing tools to check AWS codeartifact compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('codeartifact')

    def list_repositories(self) :
        """ List all code artifact repositories """
        result = []

        if self.m_is_active['codeartifact'] :
            paginator = self.m_clients['codeartifact'].get_paginator('list_repositories')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['repositories']

        return result
