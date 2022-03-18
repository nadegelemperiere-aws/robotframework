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
from sys import path as syspath
from os import path
from json import loads

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool

class ECRTools(Tool) :
    """ Class providing tools to check AWS ECR compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('ecr')

    def list_repositories(self) :
        """ List all repositories in that are accessible in environment """

        result = []

        if self.m_is_active['ecr'] :
            paginator = self.m_clients['ecr'].get_paginator('describe_repositories')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                for repository in response['repositories'] :
                    name = repository['repositoryName']
                    arn = repository['repositoryArn']
                    rid = repository['registryId']
                    tags = self.m_clients['ecr'].list_tags_for_resource(resourceArn=arn)
                    policy = self.m_clients['ecr'].get_repository_policy(repositoryName=name, \
                        registryId=rid)
                    lifecycle = self.m_clients['ecr'].get_lifecycle_policy(repositoryName=name, \
                        registryId=rid)
                    repository['Tags'] = tags['tags']
                    repository['Policy'] = loads(policy['policyText'])
                    repository['Lifecycle'] = loads(lifecycle['lifecyclePolicyText'])
                    result.append(repository)

        return result
