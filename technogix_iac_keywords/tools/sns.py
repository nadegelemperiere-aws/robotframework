""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage sns tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from json import loads

# Aws includes
from boto3 import Session

# Robotframework includes
from robot.api import logger
ROBOT = False

class SNSTools :
    """ Class providing tools to check AWS SNS compliance """

    # SNS session
    m_session = None

    # SNS client
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
            self.m_session = Session(profile_name=profile, region_name = region)
        elif access_key is not None and secret_key is not None :
            self.m_session = Session(aws_access_key_id=access_key, \
                aws_secret_access_key=secret_key, region_name = region)
        else :
            self.m_session = Session(region_name = region)
        self.m_client = self.m_session.client('sns')

    def list_subscriptions_by_topic(self, arn) :
        """ List subscriptions on a given topic
            ---
            arn (str)       : Topic arn
            ---
            returns (list)  : List of all subscriptions on the provided topic
        """

        result = []

        paginator = self.m_client.get_paginator('list_subscriptions_by_topic')
        response_iterator = paginator.paginate(TopicArn = arn)
        for response in response_iterator :
            result = result + response['Subscriptions']

        return result

    def list_subscriptions(self) :
        """ List subscriptions
            ---
            returns (list)  : List of all subscriptions
        """

        result = []

        paginator = self.m_client.get_paginator('list_subscriptions')
        response_iterator = paginator.paginate()
        for response in response_iterator :
            for subscription in response['Subscriptions'] :
                logger.debug('Subscription arn : ' + subscription['SubscriptionArn'])
                result.append(subscription)

        return result

    def list_topics(self) :
        """ List topics
            ---
            returns (list)  : List of all topics
        """

        result = []

        paginator = self.m_client.get_paginator('list_topics')
        response_iterator = paginator.paginate()
        for response in response_iterator :
            for topic in response['Topics'] :
                attributes = self.m_client.get_topic_attributes(TopicArn = topic['TopicArn'])
                topic['Attributes'] = attributes['Attributes']
                if 'Policy' in topic['Attributes'] :
                    topic['Attributes']['Policy'] = loads(topic['Attributes']['Policy'])
                if 'EffectiveDeliveryPolicy' in topic['Attributes'] :
                    topic['Attributes']['EffectiveDeliveryPolicy'] = \
                        loads(topic['Attributes']['EffectiveDeliveryPolicy'])
                if 'DeliveryPolicy' in topic['Attributes'] :
                    topic['Attributes']['DeliveryPolicy'] = \
                        loads(topic['Attributes']['DeliveryPolicy'])
                result.append(topic)

        return result
