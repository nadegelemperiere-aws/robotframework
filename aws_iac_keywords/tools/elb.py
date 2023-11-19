""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage load balancer tasks
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

class ELBTools(Tool) :
    """ Class providing tools to check AWS codecommit compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('elbv2')

    def list_load_balancers(self) :
        """ List load balancers """

        result = []

        if self.m_is_active['elbv2'] :
            paginator = self.m_clients['elbv2'].get_paginator('describe_load_balancers')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                for lb in response['LoadBalancers'] :
                    listeners = self.m_clients['elbv2'].describe_listeners( \
                        LoadBalancerArn=lb['LoadBalancerArn'])
                    lb['Listeners'] = listeners['Listeners']
                    result.append(lb)

        return result
