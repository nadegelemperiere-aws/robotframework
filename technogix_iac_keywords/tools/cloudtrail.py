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

# Boto3 includes
from boto3 import Session

class CloudtrailTools :
    """ Class providing tools to check AWS cloudtrail compliance """

    # Cloudtrail session
    m_session = None

    # Cloudtrail client
    m_client = None

    def __init__(self):
        """ Constructor """
        self.m_session = None
        self.m_client = None

    def initialize(self, profile, access_key, secret_key, region = None) :
        """ Initialize session  from credentials
            Profile or access_key/secret_key shall be provided
            ---
            profile    (str) : AWS cli profile for SSO users authentication in aws
            access_key (str) : Access key for IAM users authentication in aws
            secret_key (str) : Secret key associated to the previous access key
            region     (str) : AWS region to use
        """

        if profile is not None :
            self.m_session = Session(profile_name=profile, region_name=region)
        elif access_key is not None and secret_key is not None :
            self.m_session = Session(aws_access_key_id=access_key, \
                aws_secret_access_key=secret_key, region_name = region)
        else :
            self.m_session = Session(region_name = region)
        self.m_client = self.m_session.client('cloudtrail')

    def list_trails(self) :
        """ Returns all trails in account"""

        result = []

        paginator = self.m_client.get_paginator('list_trails')
        response_iterator = paginator.paginate()
        for response in response_iterator :
            for trail in response['Trails']     :
                details = self.m_client.describe_trails(trailNameList = [trail['TrailARN']])
                details = details['trailList'][0]
                tags    = self.m_client.list_tags(ResourceIdList = [trail['TrailARN']])
                details['Tags'] = tags['ResourceTagList'][0]['TagsList']
                result.append(details)

        return result

    def get_status(self, trail) :
        """ Returns a specific trail status
            ---
            trail    (str) : Trail to analyze
        """

        response = self.m_client.get_trail_status(Name = trail['TrailARN'])
        return response

    def get_events_selectors(self, trail) :
        """ Returns a specific trail events selectors
            ---
            trail    (str) : Trail to analyze
        """

        result = {}

        response = self.m_client.get_event_selectors(TrailName = trail['TrailARN'])
        result['basic'] = response['EventSelectors']
        if 'AdvancedEventsSelectors' in response :
            result['advance'] = response['AdvancedEventSelectors']

        return result
