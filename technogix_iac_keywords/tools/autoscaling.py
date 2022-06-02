""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Tool functions used by amplify keywords
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

class AutoScalingTools(Tool) :
    """ Class providing tools to check AWS access analyzer compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('autoscaling')

    def list_launch_configuration(self) :
        """ List all launch configurations in organization """

        result = []

        if self.m_is_active['autoscaling'] :
            paginato = self.m_clients['autoscaling'].get_paginator('describe_launch_configurations')
            response_iterator = paginato.paginate()
            for response in response_iterator :
                result = result + response['LaunchConfigurations']

        return result

    def list_autoscaling_groups(self) :
        """ List all autoscaling groups in organization """

        result = []

        if self.m_is_active['autoscaling'] :
            paginator = self.m_clients['autoscaling'].get_paginator('describe_auto_scaling_groups')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['AutoScalingGroups']

        return result
