""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to load deployment state from terraform state
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from glob import glob
from json import load, dumps
from os import path

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.terraform       import TerraformTools

# Global variable
TERRAFORM_TOOLS    = TerraformTools()

@keyword("Initialize Terraform")
def intialize_terraform(region = None, access_key = None, secret_key = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
    """
    TERRAFORM_TOOLS.initialize(region, access_key, secret_key)
    logger.info("Initialization performed")

# pylint: disable=W0102
@keyword("Launch Terraform Deployment")
def launch_terraform_deployment(directory, variables = {}) :
    """ Launch terraform deployment
        ---
        directory (str) : Deployment directory
        variables (str) : List of variables to add to the deployment in a tfvars file
    """

    result = TERRAFORM_TOOLS.init(directory)
    if not result : raise Exception('Terraform initialisation failed')
    result = TERRAFORM_TOOLS.plan(directory, variables)
    if not result : raise Exception('Terraform planification failed')
    result = TERRAFORM_TOOLS.apply(directory)
    if not result : raise Exception('Terraform application failed')


@keyword("Launch And Refresh Terraform Deployment")
def launch_and_refresh_terraform_deployment(directory, variables = {}) :
    """ Launch terraform deployment and then refresh the state
        ---
        directory (str) : Deployment directory
        variables (str) : List of variables to add to the deployment in a tfvars file
    """

    result = TERRAFORM_TOOLS.init(directory)
    if not result : raise Exception('Terraform initialisation failed')
    result = TERRAFORM_TOOLS.plan(directory, variables)
    if not result : raise Exception('Terraform planification failed')
    result = TERRAFORM_TOOLS.apply(directory)
    if not result : raise Exception('Terraform application failed')
    result = TERRAFORM_TOOLS.refresh(directory, variables)
    if not result : raise Exception('Terraform refresh failed')

@keyword("Destroy Terraform Deployment")
def destroy_terraform_deployment(directory, variables = {}) :
    """ Destroy terraform deployment
        ---
        directory (str) : Deployment directory
        variables (str) : List of variables to add to the deployment in a tfvars file
    """
    logger.info(dumps(variables))
    result = TERRAFORM_TOOLS.destroy(directory, variables)
    if not result : raise Exception('Terraform destruction failed')

# pylint: enable=W0102

@keyword("Load Terraform States")
def load_terraform_states(directory, env = '') :
    """ Load terraform states from directory
        ---
        directory (str) : Deployment directory
        env       (str) : Retrieve only states from files .env.tfstate
    """

    result = {}

    try :
        if len(env) != 0 : regexp = '/*.' + env + '.tfstate'
        else : regexp = '/*.tfstate'
        all_state_files = glob(directory + regexp)
        for filename in all_state_files :
            logger.info('loading terraform state file ' + filename)

            topic = path.splitext(path.basename(filename))[0]
            if len(env) != 0 : topic = path.splitext(topic)[0]
            logger.debug(topic)

            with open(filename,'r', encoding='UTF-8') as fid:
                content = load(fid)
            logger.debug(dumps(content))

            result[topic] = content

    except Exception as exc :
        logger.error(str(exc))

    return result
