""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Tool functions used by cloudfront keywords
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

class CloudfrontTools(Tool) :
    """ Class providing tools to check AWS access analyzer compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('cloudfront')
        self.m_is_global = True

    def list_distributions(self) :
        """ List all distributions in organization """

        result = []

        if self.m_is_active['cloudfront'] :
            paginator = self.m_clients['cloudfront'].get_paginator('list_distributions')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                # Only way to get logging information is to do an additional get_distribution
                for distribution in response['DistributionList']['Items'] :
                    details = self.m_clients['cloudfront'].get_distribution(Id=distribution['Id'])
                    result.append(details['Distribution'])

        return result
