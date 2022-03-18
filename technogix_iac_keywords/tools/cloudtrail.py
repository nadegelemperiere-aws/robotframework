""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
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

class CloudtrailTools(Tool) :
    """ Class providing tools to check AWS cloudtrail compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('cloudtrail')

    def list_trails(self) :
        """ Returns all trails in account"""

        result = []

        if self.m_is_active['cloudtrail'] :
            paginator = self.m_clients['cloudtrail'].get_paginator('list_trails')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                for trail in response['Trails']     :
                    details = self.m_clients['cloudtrail'].describe_trails( \
                        trailNameList = [trail['TrailARN']])
                    details = details['trailList'][0]
                    tags    = self.m_clients['cloudtrail'].list_tags( \
                        ResourceIdList = [trail['TrailARN']])
                    details['Tags'] = tags['ResourceTagList'][0]['TagsList']
                    result.append(details)

        return result

    def get_status(self, trail) :
        """ Returns a specific trail status
            ---
            trail    (str) : Trail to analyze
        """

        result = {}
        if self.m_is_active['cloudtrail'] :
            result = self.m_clients['cloudtrail'].get_trail_status(Name = trail['TrailARN'])
        return result

    def get_events_selectors(self, trail) :
        """ Returns a specific trail events selectors
            ---
            trail    (str) : Trail to analyze
        """

        result = {}

        if self.m_is_active['cloudtrail'] :
            response = self.m_clients['cloudtrail'].get_event_selectors( \
                TrailName = trail['TrailARN'])
            result['basic'] = response['EventSelectors']
            if 'AdvancedEventsSelectors' in response :
                result['advance'] = response['AdvancedEventSelectors']

        return result
