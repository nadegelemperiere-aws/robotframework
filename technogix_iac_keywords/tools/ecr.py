""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Tool functions used by s3 keywords
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from json import loads

# Aws includes
from boto3 import Session

class ECRTools :
    """ Class providing tools to check AWS ECR compliance """

    # ECR session
    m_session = None

    # ECR client
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
        self.m_client = self.m_session.client('ecr')

    def list_repositories(self) :
        """ List all repositories in that are accessible in environment """

        result = []

        paginator = self.m_client.get_paginator('describe_repositories')
        response_iterator = paginator.paginate()
        for response in response_iterator :
            for repository in response['repositories'] :
                name = repository['repositoryName']
                arn = repository['repositoryArn']
                rid = repository['registryId']
                tags = self.m_client.list_tags_for_resource(resourceArn=arn)
                policy = self.m_client.get_repository_policy(repositoryName=name, registryId=rid)
                lifecycle = self.m_client.get_lifecycle_policy(repositoryName=name, registryId=rid)
                repository['Tags'] = tags['tags']
                repository['Policy'] = loads(policy['policyText'])
                repository['Lifecycle'] = loads(lifecycle['lifecyclePolicyText'])
                result.append(repository)

        return result
