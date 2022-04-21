""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Tool functions used by route53 keywords
# -------------------------------------------------------
# Nadège LEMPERIERE, @17 october 2021
# Latest revision: 17 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path
from json import dumps

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool

class Route53Tools(Tool) :
    """ Class providing tools to check AWS access analyzer compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('route53')
        self.m_is_global = True

    def list_zones(self) :
        """ List all zones in organization """

        result = []

        if self.m_is_active['route53'] :
            paginator = self.m_clients['route53'].get_paginator('list_hosted_zones')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['HostedZones']

        return result

    def list_records(self) :
        """ List all records in organization """

        zones = self.list_zones()
        result = []

        for zone in zones :
            print(dumps(zone))
            if self.m_is_active['route53'] :
                paginator = self.m_clients['route53'].get_paginator('list_resource_record_sets')
                response_iterator = paginator.paginate(HostedZoneId=zone['Id'])
                for response in response_iterator :
                    result = result + response['ResourceRecordSets']


        return result
