""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage ec2 tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# Aws includes
from boto3 import Session

class RDSTools :
    """ Class providing tools to check AWS RDS compliance """

    # RDS session
    m_session = None

    # RDS client
    m_client = None

    def __init__(self):
        """ Constructor """
        self.m_session = None
        self.m_client = None

    def initialize(self, profile, access_key, secret_key, region) :
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
        self.m_client = self.m_session.client('rds')

    def list_all_databases(self) :
        """ List all existing databases """

        result = []
        shall_continue = True
        marker = None
        while shall_continue :
            if marker is not None :
                response = self.m_client.describe_db_instances(Marker = marker)
            else :
                response = self.m_client.describe_db_instances()
            for db in response['DBInstances']   : result.append(db)
            if 'Marker' in response             : marker = response['Marker']
            else                                : shall_continue = False

        return result
