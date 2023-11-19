""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to load deployment state from terraform state
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from os import path, remove
from shutil import rmtree
from subprocess import Popen, PIPE

# Robotframework includes
from robot.api import logger
ROBOT = False

# pylint: disable=R1732, R0201, W0102
class TerraformTools :
    """ Class providing tools to sequence terraform deployment """

    m_region = None

    m_access_key = None
    m_secret_key = None

    def __init__(self):
        """ Constructor """
        self.m_region = None
        self.m_access_key = None
        self.m_secret_key = None

    def initialize(self, region, access_key, secret_key) :
        """ Initialize credentials for deployment
            ---
            access_key (str) : Access key for IAM users authentication in aws
            secret_key (str) : Secret key associated to the previous access key
            region     (str) : AWS region to use
        """
        self.m_region = region
        self.m_access_key = access_key
        self.m_secret_key = secret_key

    def init(self, directory) :
        """ Initialize deployment from a given folder
            ---
            directory (str) : Folder in which deployment is located
        """

        result = True

        tf_data_dir = directory + '/.terraform'
        if path.exists(tf_data_dir) : rmtree(tf_data_dir)
        if path.exists(tf_data_dir + '.lock.hcl') : remove(tf_data_dir + '.lock.hcl')

        cmd = 'terraform init -input=false -backend-config="path=test.tfstate"'
        process = Popen(cmd, cwd=directory, stdout=PIPE, shell=True)
        (output) = process.communicate()
        logger.info(output)
        if process.returncode > 0 : result = False

        return result

    def plan(self, directory, variables = {}) :
        """ Plan deployment from a given folder (init shall have been applied)
            ---
            directory (str)  : Folder in which deployment is located
            variables (dict) : Variables to provide in a .tfvars file
        """

        result = True

        other_parameters = ''
        for key in variables :
            other_parameters = other_parameters + ' -var="' + key + '=' + variables[key] + '"'

        cmd = \
            'terraform plan -no-color -out=tfplan -input=false -state=test.tfstate ' + \
            '-var="region=' + self.m_region + '" -var="access_key=' + self.m_access_key + \
            '" -var="secret_key=' + self.m_secret_key + '"' + other_parameters
        logger.debug(cmd)
        process = Popen(cmd, cwd=directory, stdout=PIPE, shell=True)
        (output) = process.communicate()
        logger.info(output)
        if process.returncode > 0 : result = False

        return result

    def apply(self, directory) :
        """ Apply deployment from a given folder (plan shall have been applied)
            ---
            directory (str)  : Folder in which deployment is located
        """

        result = True

        cmd = 'terraform apply -no-color -input=false tfplan'
        process = Popen(cmd , cwd=directory, stdout=PIPE, shell=True)
        (output) = process.communicate()
        logger.info(output)
        if process.returncode > 0 : result = False

        return result

    def refresh(self, directory, variables = {}) :
        """ Refresh deployment from a given folder
            ---
            directory (str)  : Folder in which deployment is located
            variables (dict) : Variables to provide in a .tfvars file
        """

        result = True

        other_parameters = ''
        for key in variables :
            other_parameters = other_parameters + ' -var="' + key + '=' + variables[key] + '"'

        cmd = \
            'terraform apply -no-color -input=false -refresh-only --auto-approve ' + \
            '-state=test.tfstate -var="region=' + self.m_region + '" -var="access_key=' + \
            self.m_access_key + '" -var="secret_key=' + self.m_secret_key  + '"' + other_parameters
        process = Popen(cmd , cwd=directory, stdout=PIPE, shell=True)
        (output) = process.communicate()
        logger.info(output)
        if process.returncode > 0 : result = False

        return result

    def destroy(self, directory, variables = {}) :
        """ Destroy deployment from a given folder
            ---
            directory (str)  : Folder in which deployment is located
            variables (dict) : Variables to provide in a .tfvars file
        """

        result = True

        other_parameters = ''
        for key in variables :
            other_parameters = other_parameters + ' -var="' + key + '=' + variables[key] + '"'

        cmd = \
            'terraform destroy -no-color -input=false -auto-approve -var="region=' + \
            self.m_region + '" -var="access_key=' + self.m_access_key + '" -var="secret_key=' + \
            self.m_secret_key + '"' + other_parameters
        logger.info(cmd)
        process = Popen(cmd , cwd=directory, stdout=PIPE, shell=True)
        (output) = process.communicate()
        logger.info(output)
        if process.returncode > 0 : result = False

        return result

# pylint: enable=R1732, R0201, W0102
