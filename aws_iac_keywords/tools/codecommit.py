""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage s3 tasks
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

class CodecommitTools(Tool) :
    """ Class providing tools to check AWS codecommit compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('codecommit')

    def create_repository(self, repository) :
        """ Create repository in codecommit """

        if self.m_is_active['codecommit'] :
            self.m_clients['codecommit'].create_repository(repositoryName=repository)

    def remove_repository_if_exists(self, repository) :
        """ Remove repository in codecommit if it exists, does not return error if not found"""

        response = self.list_repositories()
        for repo in response :
            if repo['repositoryName'] == repository :
                self.m_clients['codecommit'].delete_repository(repositoryName=repository)

    def repository_exists(self, repository) :
        """ Test if a repository exist in codecommit """
        result = False

        response = self.list_repositories()
        for repo in response :
            if repo['repositoryName'] == repository :
                result = True

        return result

    def list_repositories(self) :
        """ List all code commit repositories """
        result = []

        if self.m_is_active['codecommit'] :
            paginator = self.m_clients['codecommit'].get_paginator('list_repositories')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                result = result + response['repositories']

        return result
