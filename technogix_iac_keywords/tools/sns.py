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
from sys import path as syspath
from os import path
from json import loads

# Robotframework includes
from robot.api import logger
ROBOT = False

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool

class SNSTools(Tool) :
    """ Class providing tools to check AWS SNS compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('sns')

    def list_subscriptions_by_topic(self, arn) :
        """ List subscriptions on a given topic
            ---
            arn (str)       : Topic arn
            ---
            returns (list)  : List of all subscriptions on the provided topic
        """

        result = []

        if self.m_is_active['sns'] :
            paginator = self.m_clients['sns'].get_paginator('list_subscriptions_by_topic')
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

        if self.m_is_active['sns'] :
            paginator = self.m_clients['sns'].get_paginator('list_subscriptions')
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

        if self.m_is_active['sns'] :
            paginator = self.m_clients['sns'].get_paginator('list_topics')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                for topic in response['Topics'] :
                    attributes = self.m_clients['sns'].get_topic_attributes(\
                        TopicArn = topic['TopicArn'])
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
