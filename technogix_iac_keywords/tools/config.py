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

class ConfigTools(Tool) :
    """ Class providing tools to check AWS codecommit compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('config')

    def list_recorders(self) :
        """ List config recorders in AWS account """

        result = []

        if self.m_is_active['config'] :
            response = self.m_clients['config'].describe_configuration_recorders()
            for recorder in response['ConfigurationRecorders'] :
                status = self.m_clients['config'].describe_configuration_recorder_status(\
                    ConfigurationRecorderNames=[recorder['name']])
                recorder['Status'] = status['ConfigurationRecordersStatus'][0]['recording']

        result = result + response['ConfigurationRecorders']

        return result
