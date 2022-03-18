""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
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

class ResourceGroupTools(Tool) :
    """ Class providing tools to check AWS resource group compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('resource-groups')

    def list_groups(self) :
        """ List all resource groups """

        result = []

        if self.m_is_active['resource-groups'] :
            paginator = self.m_client.get_paginator('list_groups')
            group_iterator = paginator.paginate()
            for response in group_iterator :
                for group in response['Groups'] :
                    group['Resources'] = []
                    paginator2 = self.m_client.get_paginator('list_group_resources')
                    resource_iterator = paginator2.paginate(Group = group['GroupArn'])
                    for resource in resource_iterator :
                        group['Resources'] = group['Resources'] + resource['Resources']

                    result.append(group)

        return result
