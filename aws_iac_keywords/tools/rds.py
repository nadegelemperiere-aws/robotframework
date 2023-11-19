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

class RDSTools(Tool) :
    """ Class providing tools to check AWS RDS compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('rds')

    def list_all_databases(self) :
        """ List all existing databases """

        result = []

        if self.m_is_active['rds'] :
            shall_continue = True
            marker = None
            while shall_continue :
                if marker is not None :
                    response = self.m_clients['rds'].describe_db_instances(Marker = marker)
                else :
                    response = self.m_clients['rds'].describe_db_instances()
                for db in response['DBInstances']   : result.append(db)
                if 'Marker' in response             : marker = response['Marker']
                else                                : shall_continue = False

        return result


    def list_event_subscriptions(self) :
        """ Returns all rds alarms """

        result = []

        if self.m_is_active['rds'] :
            paginator = self.m_clients['rds'].get_paginator('describe_event_subscriptions')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['EventSubscriptionsList']

        return result
