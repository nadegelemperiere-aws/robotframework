""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage cloudtrail tasks
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

class CloudwatchTools(Tool) :
    """ Class providing tools to check AWS cloudwatch compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('cloudwatch')
        self.m_services.append('logs')

    def list_groups(self) :
        """ Returns all loggroups """
        result = []

        if self.m_is_active['logs'] :
            paginator = self.m_clients['logs'].get_paginator('describe_log_groups')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                for group in response['logGroups'] :
                    tags = self.m_clients['logs'].list_tags_log_group( \
                        logGroupName=group['logGroupName'])
                    group['Tags'] = tags['tags']
                    result.append(group)

        return result

    def list_metric_alarms(self) :
        """ Returns all metric alarms """

        result = []

        if self.m_is_active['cloudwatch'] :
            paginator = self.m_clients['cloudwatch'].get_paginator('describe_alarms')
            response_iterator = paginator.paginate(AlarmTypes=['MetricAlarm'])
            for response in response_iterator :
                result = result + response['MetricAlarms']

        return result

    def list_metric_filters(self) :
        """ Returns all metric filters """

        result = []

        if self.m_is_active['logs'] :
            paginator = self.m_clients['logs'].get_paginator('describe_metric_filters')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['metricFilters']

        return result
