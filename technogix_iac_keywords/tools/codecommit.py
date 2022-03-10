""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage s3 tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# Aws includes
from boto3 import Session

class CodecommitTools :
    """ Class providing tools to check AWS codecommit compliance """

    # Cloudwatch session
    m_session = None

    # Codecommit client
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
        self.m_client = self.m_session.client('codecommit')

    def create_repository(self, repository) :
        """ Create repository in codecommit """

        self.m_client.create_repository(repositoryName=repository)

    def remove_repository_if_exists(self, repository) :
        """ Remove repository in codecommit if it exists, does not return error if not found"""

        response = self.m_client.list_repositories()
        for repo in response['repositories'] :
            if repo['repositoryName'] == repository :
                self.m_client.delete_repository(repositoryName=repository)

    def repository_exists(self, repository) :
        """ Test if a repository exist in codecommit """
        result = False

        response = self.m_client.list_repositories()
        for repo in response['repositories'] :
            if repo['repositoryName'] == repository :
                result = True

        return result
