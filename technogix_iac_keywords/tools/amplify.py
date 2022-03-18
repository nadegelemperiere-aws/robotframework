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

class AmplifyTools(Tool) :
    """ Class providing tools to check AWS access analyzer compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('amplify')

    def list_applications(self) :
        """ List all applications in organization """

        result = []

        if self.m_is_active['amplify'] :
            paginator = self.m_clients['amplify'].get_paginator('list_apps')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                for app in response['apps'] :
                    apid = app['appId']
                    branches = self.m_clients['amplify'].list_branches(appId = apid)
                    app['branches'] = branches['branches']
                    webhooks = self.m_clients['amplify'].list_webhooks(appId = apid)
                    app['webhooks'] = webhooks['webhooks']
                    domains = self.m_clients['amplify'].list_domain_associations(appId = apid)
                    app['domains'] = domains['domainAssociations']

                    result.append(app)


        return result
