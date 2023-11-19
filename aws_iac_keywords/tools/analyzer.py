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

class AnalyzerTools(Tool) :
    """ Class providing tools to check AWS access analyzer compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('accessanalyzer')

    def list_analyzers(self) :
        """ List all active analyzers """

        result = []

        if self.m_is_active['accessanalyzer'] :
            paginator = self.m_clients['accessanalyzer'].get_paginator('list_analyzers')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                for analyzer in response['analyzers'] :
                    if analyzer['status'] == 'ACTIVE' : result.append(analyzer)

        return result
