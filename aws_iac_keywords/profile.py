""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to create awscli profiles from aws sso
# permission sets
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from os import path, makedirs
from configparser import ConfigParser

# Aws includes
from boto3 import Session

# Robotframework includes
from robot.api.deco import keyword
ROBOT = False

# pylint: disable=R0913, R0914, C0301
@keyword("Append Profiles In Cli Configuration")
def append_profile(filename, sso, url, region, account, access_key = None, secret_key = None, silent = None) :
    """ Append a list of profiles related to the aws sso permission sets in aws cli configuration
        ---
        filename   (str) : aws cli configuration file
        sso        (str) : arn of the sso resource from which to retrieve permission set
        silent     (str) : list of profile to create but not to return
        url        (str) : url of the portal to use for sso authentication
        region     (str) : region to use for sso authentication
        accout     (str) : identifier of the account in which the profile shall apply
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        ---
        returns : The list of added profiles, filtered from the list of profiles in silent
    """

    result = []

    # Retrieve all existing permission sets
    permissions = []
    sso_session = Session(aws_access_key_id=access_key, \
        aws_secret_access_key=secret_key, region_name = region)
    sso_client = sso_session.client('sso-admin')
    response = sso_client.list_permission_sets(InstanceArn=sso)
    for perm in response['PermissionSets'] :
        resp = sso_client.describe_permission_set(InstanceArn=sso,PermissionSetArn=perm)
        permissions.append(resp['PermissionSet']['Name'])

    # Read existing as cli configuration
    config = ConfigParser()
    if path.isfile(filename) : config.read(filename)

    # Create a profile for all permission sets + None
    found = False
    for profile in config :
        if profile == 'profile robotframework-none' : found = True
    if not found : config['profile robotframework-none'] = {
        'sso_start_url' : url,
        'sso_region' : region,
        'sso_account_id' : account,
        'sso_role_name' : 'None',
        'region' : region,
        'output' : 'json'
    }
    if silent and 'robotframework-none' not in silent : result.append('robotframework-none')

    for perm in permissions :
        found = False
        for profile in config :
            if profile == ('profile robotframework-' + perm) : found = True
        if not found : config['profile robotframework-' + perm] = {
            'sso_start_url' : url,
            'sso_region' : region,
            'sso_account_id' : account,
            'sso_role_name' : perm,
            'region' : region,
            'output' : 'json'
        }
        if silent and ('robotframework-' + perm) not in silent :
            result.append('robotframework-' + perm)

    if not path.exists(path.dirname(filename)): makedirs(path.dirname(filename))

    with open(filename,'w', encoding='UTF-8') as fid:
        config.write(fid)

    return result
# pylint: enable=R0913, R0914, C0301

@keyword("Clean Cli Configuration From Test Profiles")
def clean_profile(filename) :
    """ Reinitialize aws cli configuration
        ---
        filename   (str) : aws cli configuration file
    """

    # Read existing configuration
    config = ConfigParser()
    if path.isfile(filename) :

        config.read(filename)

        # Check config for robotframework profile and remove them
        to_remove = []
        for profile in config :
            if profile.startswith('profile robotframework-') : to_remove.append(profile)

        for profile in to_remove :
            config.remove_section(profile)

    if not path.exists(path.dirname(filename)): makedirs(path.dirname(filename))

    with open(filename,'w', encoding='UTF-8') as fid:
        config.write(fid)
