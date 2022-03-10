""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage aws users tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path
from datetime import datetime, timezone

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.iam import IAMTools
from tools.compare import compare_dictionaries, remove_type_from_list

# Global variable
IAM_TOOLS = IAMTools()

@keyword("Initialize IAM")
def intialize_iam(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    IAM_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword("Add New User")
def add_new_user(username) :
    """ Add new user to IAM
        ---
        username (str) : Username to add
    """
    IAM_TOOLS.add_user(username)

@keyword("Add User To Group")
def add_user_to_group(username, group) :
    """ Add new user to IAM group
        ---
        username (str) : Username to add
        group    (str) : Group to add user to
    """
    IAM_TOOLS.add_user_to_group(username, group)

@keyword("Remove User")
def remove_user(username) :
    """ Remove user from IAM
        ---
        username (str) : Username to remove
    """
    IAM_TOOLS.remove_user(username)

@keyword("Remove User From Group")
def remove_user_from_group( username, group) :
    """ Remove user from IAM group
        ---
        username (str) : Username to remove
        group    (str) : Group to remove user from
    """
    IAM_TOOLS.remove_user_from_group(username, group)

@keyword("Remove User From All Groups")
def remove_user_from_all_groups(username) :
    """ Remove user from all IAM group
        ---
        username (str) : Username to remove
    """
    IAM_TOOLS.remove_user_from_all_groups(username)

@keyword("User Has No Password")
def no_password(username) :
    """ Check if an IAM user has no password
        ---
        username (str) : Username to remove
    """
    result = IAM_TOOLS.has_password(username)
    if result : raise Exception('Password found for user')

@keyword("No Groups Except Than")
def no_groups_except_than(groups) :
    """ Check if there is no IAM groups other than the ones provided
        ---
        groups (str) : List of allowed groups
    """
    result = IAM_TOOLS.list_groups()
    for group in result :
        if not group['GroupName'] in groups :
            raise Exception('Group ' + ['GroupName'] + ' is not allowed to exist')

@keyword("No Users Other Than")
def no_users_other_than(usernames) :
    """ Check if there is no IAM users other than the ones provided
        ---
        usernames (str) : List of allowed users
    """
    result = IAM_TOOLS.list_users()
    for user in result :
        if not user['UserName'] in usernames :
            raise Exception('User ' + user['UserName'] + ' is not allowed to exist')

@keyword("No Users In Group Other Than")
def check_if_no_user_other_than(usernames, group) :
    """ Check if there is no IAM users in group other than the ones provided
        ---
        usernames (str) : List of allowed users in group
        group     (sdr) : Group to analyze
    """
    result = IAM_TOOLS.list_users_for_group(group)
    for user in result :
        if not user['UserName'] in usernames :
            name = user['UserName']
            raise Exception('User ' + name + ' is not allowed to exist in group ' + group)

@keyword("Root Shall Not Have Access Key")
def no_root_access_key() :
    """ Check that root has no access key """
    result = IAM_TOOLS.get_account_summary()
    if 'AccountAccessKeysPresent' in result['SummaryMap'] and \
        int(result['SummaryMap']['AccountAccessKeysPresent']) > 1 :
        raise Exception("Root access key found")

@keyword("Root Shall Have MFA Enabled")
def root_mfa_enabled() :
    """ Check that root has MFA enabled """
    result = IAM_TOOLS.get_account_summary()
    if not 'AccountMFAEnabled' in result['SummaryMap'] or \
        int(result['SummaryMap']['AccountMFAEnabled']) != 1 :
        raise Exception("Root does not have MFA enabled")

@keyword("Password Length Shall Be Larger Than")
def password_size_test(minimal_size) :
    """ Check that allowed password size is larger than a given size
        ---
        minimal_size (str) : Minimal allowed size
    """
    result = IAM_TOOLS.get_account_password_policy()
    if result['MinimumPasswordLength'] < int(minimal_size) :
        size = str(result['PasswordPolicy']['MinimumPasswordLength'])
        raise Exception('Minimal password size is only ' + size)

@keyword("Password Reuse Shall Not Be Allowed")
def no_password_reuse(number) :
    """ Check that password can not be reused before a given number of changes
        ---
        number (str) : Minimal number of password before reuse
    """
    result = IAM_TOOLS.get_account_password_policy()
    if result['PasswordReusePrevention'] < int(number) :
        num = str(result['PasswordPolicy']['PasswordReusePrevention'])
        raise Exception('Password reuse policy is only ' + num + ' password before reuse allowed')

@keyword("Root Shall Have Hardware MFA Device")
def root_mfa_hardware(account) :
    """ Check that root user have harware MFA
        ---
        account (str) : account to analyze for root
    """
    result = IAM_TOOLS.get_account_summary()
    if not 'AccountMFAEnabled' in result['SummaryMap'] or \
        int(result['SummaryMap']['AccountMFAEnabled']) != 1 :
        raise Exception("Root does not have MFA enabled")
    result = IAM_TOOLS.has_virtual_mfa_devices(account)
    if result : raise Exception("Virtual device found for root")

@keyword("Access Key Number Less Than")
def access_keys_number_less_than(max_number) :
    """ Check that each user does not have more than a given number of access keys
        ---
        max_number (str) : Maximal allowed number of access keys
    """
    result = IAM_TOOLS.list_users()
    for user in result :
        keys = IAM_TOOLS.list_user_access_keys(user['UserName'])
        if len(keys) > int(max_number) :
            raise Exception(str(len(keys)) + ' keys found for user ' + user['UserName'])

@keyword("No Service Credentials")
def no_service_credentials() :
    """ Check that users do not have services credentials (CIS benchmark) """
    result = IAM_TOOLS.list_users()
    for user in result :
        credentials = IAM_TOOLS.list_user_service_credentials(user)
        if len(credentials) > 0 :
            name = credentials[0]['ServiceName']
            raise Exception('User ' + user + ' has credentials for service ' + name)

@keyword("Root Shall Not Have Been Used Since")
def root_shall_not_have_been_used_since( minimal_age) :
    """ Check that root account have not been used since a given delay
        ---
        minimal_age (str) : Maximal delay since root user has not been used
    """
    result = IAM_TOOLS.parse_credential_report()

    for i_row in range(1,len(result['content'])) :
        if result['content'][i_row][result['columns']['user']] == '<root_account>' :

            dates = {}
            ages = []
            password_used = result['content'][i_row][result['columns']['password_last_used']]
            key1_used = result['content'][i_row][result['columns']['access_key_1_last_used_date']]
            key2_used = result['content'][i_row][result['columns']['access_key_2_last_used_date']]

            if not password_used == 'N/A' :
                dates['password_last_used'] = datetime.fromisoformat(password_used)
            if not key1_used == 'N/A' :
                dates['key_1_last_used_date'] = datetime.fromisoformat(key1_used)
            if not key2_used == 'N/A' :
                dates['key_2_last_used_date'] = datetime.fromisoformat(key2_used)

            if 'password_last_used' in dates :
                ages.append((datetime.now(timezone.utc) - dates['password_last_used']).days)
            if 'key_1_last_used_date' in dates :
                ages.append((datetime.now(timezone.utc) - dates['key_1_last_used_date']).days)
            if 'key_2_last_used_date' in dates :
                ages.append((datetime.now(timezone.utc) - dates['key_2_last_used_date']).days)

            min_age = min(ages)
            if min_age < int(minimal_age) :
                raise Exception('Root user used ' + str(min_age) + ' days ago')

@keyword("Console Users Shall Have MFA Enabled")
def user_mfa_enabled() :
    """ Check that all users have MFA activated """
    result = IAM_TOOLS.parse_credential_report()
    for i_row in range(1,len(result['content'])) :
        if result['content'][i_row][result['columns']['password_enabled']] == 'true' and \
            result['content'][i_row][result['columns']['mfa_active']] == 'false' :
            name = result['content'][i_row][result['columns']['user']]
            raise Exception('User ' + name + ' has console password but no MFA enabled' )

@keyword("Users Access Key Shall Not Be Created At User Creation Step")
def access_key_creation_date() :
    """ Check that users access keys creation date is not user creation date """
    result = IAM_TOOLS.list_users()
    for user in result :
        user_creation_date = user['CreateDate']
        keys = IAM_TOOLS.list_user_access_keys(user['UserName'])
        for key in keys :
            delta = abs((user_creation_date - key['CreateDate']).total_seconds())
            if delta < 60 :
                name = user['UserName']
                raise Exception('User ' + name + ' access key has been created on user creation')

# pylint: disable=R0912
@keyword("Credentials Unused For Too Long Shall Be disabled")
def credentials_unused_disabled(delay) :
    """ Check that credentials unused since more than a given delay are disabled
        ---
        delay (str) : Maximal delay since credentials have been unused
    """
    result = IAM_TOOLS.parse_credential_report()
    for i_row in range(1,len(result['content'])) :

        user = result['content'][i_row][result['columns']['user']]
        pass_enabled = result['content'][i_row][result['columns']['password_enabled']]
        pass_last_used = result['content'][i_row][result['columns']['password_last_used']]
        pass_last_changed = result['content'][i_row][result['columns']['password_last_used']]

        key1_enabled = result['content'][i_row][result['columns']['access_key_1_active']]
        key1_last_used = result['content'][i_row][result['columns']['access_key_1_last_used_date']]
        key1_last_changed = result['content'][i_row][result['columns']['access_key_1_last_rotated']]

        key2_enabled = result['content'][i_row][result['columns']['access_key_2_active']]
        key2_last_used = result['content'][i_row][result['columns']['access_key_2_last_used_date']]
        key2_last_changed = result['content'][i_row][result['columns']['access_key_2_last_rotated']]

        if pass_enabled == 'true' :
            if not pass_last_used == "N/A" :
                days = (datetime.now(timezone.utc) - datetime.fromisoformat(pass_last_used)).days
                if days >= int(delay) :
                    raise Exception('User ' + user + ' password has been unused for ' + \
                        str(days) + ' days')
            else :
                days = (datetime.now(timezone.utc) - datetime.fromisoformat(pass_last_changed)).days
                if days >= int(delay) :
                    raise Exception('User ' + user + ' password has been unchanged for ' + \
                        str(days) + ' days')

        if key1_enabled == 'true' :
            if not key1_last_used == 'N/A' :
                days = (datetime.now(timezone.utc) - datetime.fromisoformat(key1_last_used)).days
                if days >= int(delay) :
                    raise Exception('User ' + user + ' access key has been unused for ' + \
                        str(days) + ' days')
            else :
                days = (datetime.now(timezone.utc) - datetime.fromisoformat(key1_last_changed)).days
                if days >= int(delay) :
                    raise Exception('User ' + user + ' access key has been unchanged for ' + \
                        str(days) + ' days')

        if key2_enabled == 'true' :
            if not key2_last_used == 'N/A' :
                days = (datetime.now(timezone.utc) - datetime.fromisoformat(key2_last_used)).days
                if days >= int(delay) :
                    raise Exception('User ' + user + ' access key has been unused for ' + \
                        str(days) + ' days')
            else :
                days = (datetime.now(timezone.utc) - datetime.fromisoformat(key2_last_changed)).days
                if days >= int(delay) :
                    raise Exception('User ' + user + ' access key has been unchanged for ' + \
                        str(days) + ' days')
# pylint: enable=R0912

@keyword("Users Access Key Shall Not Be Older Than")
def access_key_younger(delay) :
    """ Check that user access keys rotate
        ---
        delay (str) : Maximal rotation delay
    """
    result = IAM_TOOLS.list_access_keys()

    for key in result :
        if key['Status'] == 'Active' :
            days = (datetime.now(timezone.utc) - key['CreateDate']).days
            if days >= int(delay) :
                user = result['UserName']
                raise Exception('User ' + user + ' access key has been unchanged for ' + \
                    str(days) + ' days')

@keyword("No Permissions Shall Be Attributed To User Directly")
def user_has_no_permission() :
    """ Check that users have no direct permissions """
    result = IAM_TOOLS.list_users()
    for user in result :
        has_permission = IAM_TOOLS.has_permission(user['UserName'])
        if has_permission : raise Exception('User ' + user['UserName'] + ' has a direct policy')

@keyword("Policy Shall Have Been Attached To A Role")
def policy_shall_have_been_attached_to_a_role(name) :
    """ Check that a policy has been attached to a role
        ---
        name (str) : Policy name
    """
    result = IAM_TOOLS.list_attached_policies()
    found = False
    for policy in result :
        if policy['PolicyName'] == name :
            roles = IAM_TOOLS.list_roles_for_policy(policy)
            if len(roles) > 0 :
                found = True
                logger.info('Policy ' + policy['PolicyName'] + ' gives ' + name + \
                    ' access to entities ' + ','.join([role['RoleName'] for role in roles]))
    if not found :
        raise Exception("No role found for policy " + name)

@keyword("No Expired Certificates Shall Exist")
def no_expired_certificates() :
    """ Check that no expired certificates exist """
    result = IAM_TOOLS.list_expired_certificates()
    if len(result) > 0 :
        raise Exception('Certificates ' + ','.join(result) + ' has expired and not been removed')

@keyword("No Policy Shall Allow Full Administrative Privilege")
def no_full_privilege_policies() :
    """ Check that no policy gives full privilege """
    result = IAM_TOOLS.list_attached_policies()
    for policy in result :
        too_much = IAM_TOOLS.is_giving_full_admin_privileges(policy)
        if too_much :
            name = policy['PolicyName']
            raise Exception('Policy ' + name + ' gives full administrative privileges')

@keyword('Role Shall Exist And Match')
def role_shall_exist_and_match(specs) :
    """ Check that a role exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = IAM_TOOLS.list_roles()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for role in result :
            if compare_dictionaries(spec['data'], role) :
                found = True
                logger.info('Role ' + spec['name'] + ' matches role ' + role['RoleName'])
        if not found : raise Exception('Role ' + spec['name'] + ' does not match')
