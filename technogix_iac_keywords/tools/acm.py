""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage certificates tasks
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

class ACMTools(Tool) :
    """ Class providing tools to check AWS certificates compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('acm')

    def list_certificates(self) :
        """ List existing certificates  """

        result = []

        if self.m_is_active['acm'] :
            paginator = self.m_clients['acm'].get_paginator('list_certificates')
            response_iterator = paginator.paginate(CertificateStatuses=['ISSUED'])
            for response in response_iterator :
                for cert in response['CertificateSummaryList'] :
                    details = self.m_clients['acm'].describe_certificate(\
                        CertificateArn=cert['CertificateArn'])
                    details = details['Certificate']
                    result.append(details)

        return result
