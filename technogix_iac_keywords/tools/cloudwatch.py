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

class CloudwatchTools :
    """ Class providing tools to check AWS cloudtrail compliance """

    # Cloudwatch session
    m_session = None

    # Cloudwatch log client
    m_log_client = None

    # Cloudwatch client
    m_cloudwatch_client = None

    def __init__(self):
        """ Constructor """
        self.m_session = None
        self.m_log_client = None
        self.m_cloudwatch_client = None

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
        self.m_log_client = self.m_session.client('logs')
        self.m_cloudwatch_client = self.m_session.client('cloudwatch')

    def list_groups(self) :
        """ Returns all loggroups """
        result = []

        paginator = self.m_log_client.get_paginator('describe_log_groups')
        response_iterator = paginator.paginate()
        for response in response_iterator :
            for group in response['logGroups'] :
                tags = self.m_log_client.list_tags_log_group(logGroupName=group['logGroupName'])
                group['Tags'] = tags['tags']
                result.append(group)

        return result

    def list_metric_alarms(self) :
        """ Returns all metric alarms """

        result = []

        paginator = self.m_cloudwatch_client.get_paginator('describe_alarms')
        response_iterator = paginator.paginate(AlarmTypes=['MetricAlarm'])
        for response in response_iterator :
            result = result + response['MetricAlarms']

        return result

    def list_metric_filters(self) :
        """ Returns all metric filters """

        result = []

        paginator = self.m_log_client.get_paginator('describe_metric_filters')
        response_iterator = paginator.paginate()
        for response in response_iterator :
            result = result + response['metricFilters']

        return result
