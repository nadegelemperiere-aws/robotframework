""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage ec2 tasks
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

class DirectoryTools(Tool) :
    """ Class providing tools to check AWS codecommit compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('ds')

    def list_directories(self) :
        """ List all directories in account """

        result = []

        if self.m_is_active['ds'] :
            paginator = self.m_clients['ds'].get_paginator('describe_directories')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['DirectoryDescriptions']

        return result
