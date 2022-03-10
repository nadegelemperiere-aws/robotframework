""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage cloudtrail tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path
from datetime import datetime, timezone
from re import split

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), '../')))
from tools.cloudtrail import CloudtrailTools
from tools.s3         import S3Tools
from tools.cloudwatch import CloudwatchTools
from tools.sns        import SNSTools
from tools.compare    import compare_dictionaries

# Global variable
CLOUDTRAIL_TOOLS                = CloudtrailTools()
CLOUDTRAIL_S3_TOOLS             = S3Tools()
CLOUDTRAIL_CLOUDWATCH_TOOLS     = CloudwatchTools()
CLOUDTRAIL_SNS_TOOLS            = SNSTools()

# pylint: disable=R1702, R0914, R0912
@keyword("Initialize Cloudtrail")
def intialize_cloudtrail(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    CLOUDTRAIL_TOOLS.initialize(profile, access_key, secret_key, region)
    CLOUDTRAIL_S3_TOOLS.initialize(profile, access_key, secret_key, region)
    CLOUDTRAIL_CLOUDWATCH_TOOLS.initialize(profile, access_key, secret_key, region)
    CLOUDTRAIL_SNS_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword("Cloudtrail Shall Be Activated In All Regions")
def cloudtrail_activated() :
    """ Test that cloudtrail is activated in all regions (CIS benchmark) """
    result = CLOUDTRAIL_TOOLS.list_trails()
    is_management_events_activated = False
    for trail in result :
        status = CLOUDTRAIL_TOOLS.get_status(trail)
        events = CLOUDTRAIL_TOOLS.get_events_selectors(trail)
        if not trail['IsMultiRegionTrail'] :
            raise Exception('Trail ' + trail['Name'] + ' is not multi-regions')
        if not status['IsLogging'] :
            raise Exception('Trail ' + trail['Name'] + ' is not logging')
        for event in events['basic'] :
            if event['IncludeManagementEvents'] and event['ReadWriteType'] == 'All' :
                is_management_events_activated = True

    if not is_management_events_activated :
        raise Exception('Management events has not been activated')

@keyword("Cloudtrail Logfile Validation Shall Be Enabled")
def logfile_validation_activated() :
    """ Test that cloudtrail logfile validation is enabled (CIS benchmark) """
    result = CLOUDTRAIL_TOOLS.list_trails()
    for trail in result :
        if not trail['LogFileValidationEnabled'] :
            raise Exception('Trail ' + trail['Name'] + ' logfile validation is not activated')

@keyword("Cloudtrail Shall Deliver To Loggroup")
def cloudtrail_to_loggrop() :
    """ Test that cloudtrail correctly delivers log into loggroup """
    result = CLOUDTRAIL_TOOLS.list_trails()
    for trail in result :
        if not 'CloudWatchLogsLogGroupArn' in trail :
            raise Exception('Trail ' + trail['Name'] + ' is not associated to a loggroup')
        status = CLOUDTRAIL_TOOLS.get_status(trail)
        if not 'LatestCloudWatchLogsDeliveryTime' in status :
            raise Exception('Trail ' + trail['Name'] + ' has never deliver log')
        days = (datetime.now(timezone.utc) - status['LatestCloudWatchLogsDeliveryTime']).days
        if days > 1 :
            raise Exception('Trail ' + trail['Name'] + ' last log delivery to loggroup is too old')

@keyword("Cloudtrail Bucket Shall Not Be Publicly Available")
def bucket_not_publicly_available(account) :
    """ Test that cloudtrail bucket is not publicly available
    ---
        account (str) : Account on which to look for bucket
    """

    user_url = 'acs.amazonaws.com/groups/global/AllUsers'
    auth_user_url = 'acs.amazonaws.com/groups/global/AuthenticatedUsers'
    result = CLOUDTRAIL_TOOLS.list_trails()
    for trail in result :
        name = trail['S3BucketName']
        grants = CLOUDTRAIL_S3_TOOLS.get_acls(name, account)
        for grantee in grants :
            if 'URI' in grantee['Grantee'] and grantee['Grantee']['URI'].find(user_url) >= 0 :
                raise Exception('Logging bucket ' + name + ' grants access to any user')
            if 'URI' in grantee['Grantee'] and grantee['Grantee']['URI'].find(auth_user_url) >= 0 :
                raise Exception('Logging bucket ' + name + ' grants access to any auth users')
        policy = CLOUDTRAIL_S3_TOOLS.get_policy(name, account)
        public_access = CLOUDTRAIL_S3_TOOLS.get_public_access_block(name, account)
        if not CLOUDTRAIL_S3_TOOLS.is_preventing_anonymous_access(policy) :
            raise Exception('Logging bucket ' + name + ' is allowing anonymous access')
        if (not public_access['BlockPublicAcls'] or \
            not public_access['IgnorePublicAcls'] or \
            not public_access['BlockPublicPolicy'] or \
            not public_access['RestrictPublicBuckets']):
            raise Exception('Logging bucket ' + name + ' is publicly available')

@keyword("Cloudtrail Bucket Accesses Shall Be Logged")
def bucket_access_shall_be_logged(account) :
    """ Test that cloudtrail bucket access are logged
    ---
        account (str) : Account on which to look for bucket
    """
    result = CLOUDTRAIL_TOOLS.list_trails()
    for trail in result :
        logging = CLOUDTRAIL_S3_TOOLS.get_logging(trail['S3BucketName'], account)
        if not 'TargetBucket' in logging :
            raise Exception('Logging is not enabled for bucket ' + trail['S3BucketName'])

@keyword("Cloudtrail Logs Shall Be Encrypted")
def logs_shall_be_encrypted() :
    """ Test that cloudtrail logs are encrypted """
    result = CLOUDTRAIL_TOOLS.list_trails()
    for trail in result :
        if not 'KmsKeyId' in trail :
            raise Exception('Logs encryption is not set for trail ' + trail['S3BucketName'])

@keyword("S3 Object Actions Logging Shall Be Enabled")
def bucket_shall_block_public_access() :
    """ Test that S3 actions are logged using cloudtrail """
    result = CLOUDTRAIL_TOOLS.list_trails()
    found = False
    for trail in result :
        events = CLOUDTRAIL_TOOLS.get_events_selectors(trail)
        for event in events['basic'] :
            for resource in event['DataResources'] :
                if resource['Type'] == "AWS::S3::Object" :
                    for value in resource['Values'] :
                        if value == "arn:aws:s3" : found = True

    if not found :
        raise Exception('Trail that logs S3 events not found')


# pylint: disable=C0301
@keyword("Cloudtrail Alarm Shall Exist For Unauthorized API Calls")
def cloudtrail_alarm_shall_exist_for_unauthorized_api_calls() :
    """ Test that cloudtrail alarms exist for unauthorized API calls """

    cloudtrail_alarm_shall_exist_for_filter(
        'UnauthorizedApiCall',
        '{ (($.errorCode="*UnauthorizedOperation") || ($.errorCode="AccessDenied*")) && ($.sourceIPAddress!="delivery.logs.amazonaws.com") && ($.eventName!="HeadBucket") }')

@keyword("Cloudtrail Alarm Shall Exist For Console SignIn Without MFA")
def cloudtrail_alarm_shall_exist_for_sign_in_without_mfa() :
    """ Test that cloudtrail alarms exist for signing in without MFA"""

    cloudtrail_alarm_shall_exist_for_filter(
        'SignIn without MFA',
        '{ ($.eventName = "ConsoleLogin") && ($.additionalEventData.MFAUsed != "Yes") }')

@keyword("Cloudtrail Alarm Shall Exist For Root Account Usage")
def cloudtrail_alarm_shall_exist_for_root_account_usage() :
    """ Test that cloudtrail alarms exist for root account usage """

    cloudtrail_alarm_shall_exist_for_filter(
        'Root Account Usage',
        '{ $.userIdentity.type = "Root" && $.userIdentity.invokedBy NOT EXISTS && $.eventType != "AwsServiceEvent" }')

@keyword("Cloudtrail Alarm Shall Exist For IAM Policy Change")
def cloudtrail_alarm_shall_exist_for_iam_policy_change() :
    """ Test that cloudtrail alarms exist for IAM policy change """

    cloudtrail_alarm_shall_exist_for_filter(
        'IAM policy change',
        '{($.eventName="DeleteGroupPolicy")||($.eventName="DeleteRolePolicy")||($.eventName="DeleteUserPolicy")||($.eventName="PutGroupPolicy")||($.eventName="PutRolePolicy")||($.eventName="PutUserPolicy")||($.eventName="CreatePolicy")||($.eventName="DeletePolicy")||($.eventName="CreatePolicyVersion")||($.eventName="DeletePolicyVersion")||($.eventName="AttachRolePolicy")||($.eventName="DetachRolePolicy")||($.eventName="AttachUserPolicy")||($.eventName="DetachUserPolicy")||($.eventName="AttachGroupPolicy")||($.eventName="DetachGroupPolicy")}')

@keyword("Cloudtrail Alarm Shall Exist For Cloudtrail Configuration Change")
def cloudtrail_alarm_shall_exist_for_cloudtrail_configuration_change() :
    """ Test that cloudtrail alarms exist for cloudtrail configuration change """

    cloudtrail_alarm_shall_exist_for_filter(
        'Cloudtrail configuration change',
        '{ ($.eventName = "CreateTrail") || ($.eventName = "UpdateTrail") || ($.eventName = "DeleteTrail") || ($.eventName = "StartLogging") || ($.eventName = "StopLogging") }')


@keyword("Cloudtrail Alarm Shall Exist For AWS Management Console Authentication Failures")
def cloudtrail_alarm_shall_exist_for_aws_management_console_authentication_failures() :
    """ Test that cloudtrail alarms exist for console authentication failures """

    cloudtrail_alarm_shall_exist_for_filter(
        'AWS console authentication failures',
        '{ ($.eventName ="ConsoleLogin") && ($.errorMessage = "Failed authentication") }')


@keyword("Cloudtrail Alarm Shall Exist For Disabling Customer Keys")
def cloudtrail_alarm_shall_exist_for_disabling_customer_keys() :
    """ Test that cloudtrail alarms exist for customer keys disabling """

    cloudtrail_alarm_shall_exist_for_filter(
        'Customer keys disabling',
        '{($.eventSource = "kms.amazonaws.com") && (($.eventName="DisableKey")||($.eventName="ScheduleKeyDeletion")) }')

@keyword("Cloudtrail Alarm Shall Exist For S3 Bucket Policy Changes")
def cloudtrail_alarm_shall_exist_for_s3_bucket_policy_changes() :
    """ Test that cloudtrail alarms exist for bucket policy change """

    cloudtrail_alarm_shall_exist_for_filter(
        'S3 bucket policy change',
        '{ ($.eventSource = "s3.amazonaws.com") && (($.eventName = "PutBucketAcl") || ($.eventName = "PutBucketPolicy") || ($.eventName = "PutBucketCors") || ($.eventName = "PutBucketLifecycle") || ($.eventName = "PutBucketReplication") || ($.eventName = "DeleteBucketPolicy") || ($.eventName = "DeleteBucketCors") || ($.eventName = "DeleteBucketLifecycle") || ($.eventName = "DeleteBucketReplication")) }')


@keyword("Cloudtrail Alarm Shall Exist For AWS Config Configuration Change")
def cloudtrail_alarm_shall_exist_for_aws_config_configuration_changes() :
    """ Test that cloudtrail alarms exist for AWS config change """

    cloudtrail_alarm_shall_exist_for_filter(
        'AWS config change',
        '{ ($.eventSource = "config.amazonaws.com") && (($.eventName="StopConfigurationRecorder")||($.eventName="DeleteDeliveryChannel") ||($.eventName="PutDeliveryChannel")||($.eventName="PutConfigurationRecorder")) }')


@keyword("Cloudtrail Alarm Shall Exist For Security Group Change")
def cloudtrail_alarm_shall_exist_for_security_group_changes() :
    """ Test that cloudtrail alarms exist for security groups changes """

    cloudtrail_alarm_shall_exist_for_filter(
        'Security group changes',
        '{ ($.eventName = "AuthorizeSecurityGroupIngress") || ($.eventName = "AuthorizeSecurityGroupEgress") || ($.eventName = "RevokeSecurityGroupIngress") || ($.eventName = "RevokeSecurityGroupEgress") || ($.eventName = "CreateSecurityGroup") || ($.eventName = "DeleteSecurityGroup") }')

@keyword("Cloudtrail Alarm Shall Exist For NACL Change")
def cloudtrail_alarm_shall_exist_for_nacl_changes() :
    """ Test that cloudtrail alarms exist for access control changes """

    cloudtrail_alarm_shall_exist_for_filter(
        'NACL changes',
        '{ ($.eventName = "CreateNetworkAcl") || ($.eventName = "CreateNetworkAclEntry") || ($.eventName = "DeleteNetworkAcl") || ($.eventName = "DeleteNetworkAclEntry") || ($.eventName = "ReplaceNetworkAclEntry") || ($.eventName = "ReplaceNetworkAclAssociation") }')

@keyword("Cloudtrail Alarm Shall Exist For Network Gateways Changes")
def cloudtrail_alarm_shall_exist_for_network_gateways_changes() :
    """ Test that cloudtrail alarms exist for network gateways changes """

    cloudtrail_alarm_shall_exist_for_filter(
        'Network gateways changes',
        '{ ($.eventName = "CreateCustomerGateway") || ($.eventName = "DeleteCustomerGateway") || ($.eventName = "AttachInternetGateway") || ($.eventName = "CreateInternetGateway") || ($.eventName = "DeleteInternetGateway") || ($.eventName = "DetachInternetGateway") }')

@keyword("Cloudtrail Alarm Shall Exist For Route Table Changes")
def cloudtrail_alarm_shall_exist_for_route_table_changes() :
    """ Test that cloudtrail alarms exist for route table changes"""

    cloudtrail_alarm_shall_exist_for_filter(
        'Route table changes',
        '{ ($.eventName = "CreateRoute") || ($.eventName = "CreateRouteTable") || ($.eventName = "ReplaceRoute") || ($.eventName = "ReplaceRouteTableAssociation") || ($.eventName = "DeleteRouteTable") || ($.eventName = "DeleteRoute") || ($.eventName = "DisassociateRouteTable") }')

@keyword("Cloudtrail Alarm Shall Exist For VPC Changes")
def cloudtrail_alarm_shall_exist_for_vpc_changes() :
    """ Test that cloudtrail alarms exist for VPC changes """

    cloudtrail_alarm_shall_exist_for_filter(
        'Vpc changes',
        '{ ($.eventName = "CreateVpc") || ($.eventName = "DeleteVpc") || ($.eventName = "ModifyVpcAttribute") || ($.eventName = "AcceptVpcPeeringConnection") || ($.eventName = "CreateVpcPeeringConnection") || ($.eventName = "DeleteVpcPeeringConnection") || ($.eventName = "RejectVpcPeeringConnection") || ($.eventName = "AttachClassicLinkVpc") || ($.eventName = "DetachClassicLinkVpc") || ($.eventName = "DisableVpcClassicLink") || ($.eventName = "EnableVpcClassicLink") }')


@keyword("Cloudtrail Alarm Shall Exist For AWS Organizations Changes")
def cloudtrail_alarm_shall_exist_for_aws_organizations_changes() :
    """ Test that cloudtrail alarms exist for organizations changes """

    cloudtrail_alarm_shall_exist_for_filter(
        'Organization changes',
        '{ ($.eventSource = "organizations.amazonaws.com") && (($.eventName = "AcceptHandshake") || ($.eventName = "AttachPolicy") || ($.eventName = "CreateAccount") || ($.eventName = "CreateOrganizationalUnit") || ($.eventName = "CreatePolicy") || ($.eventName = "DeclineHandshake") || ($.eventName = "DeleteOrganization") || ($.eventName = "DeleteOrganizationalUnit") || ($.eventName = "DeletePolicy") || ($.eventName = "DetachPolicy") || ($.eventName = "DisablePolicyType") || ($.eventName = "EnablePolicyType") || ($.eventName = "InviteAccountToOrganization") || ($.eventName = "LeaveOrganization") || ($.eventName = "MoveAccount") || ($.eventName = "RemoveAccountFromOrganization") || ($.eventName = "UpdatePolicy") || ($.eventName = "UpdateOrganizationalUnit")) }')

# pylint: enable=C0301

@keyword('Trails Shall Exist And Match')
def trails_shall_exist_and_match(specs) :
    """ Test that trail exist that matches specifications
    ---
        specs    (list) : List of specifications to consider
    """
    result = CLOUDTRAIL_TOOLS.list_trails()
    for spec in specs :
        found = False
        for trail in result :
            if compare_dictionaries(spec['data'], trail) :
                found = True
                logger.info('Trail ' + spec['name'] + ' matches trail ' + trail['Name'])
        if not found :
            raise Exception('Trail ' + spec['name'] + ' does not match')

def cloudtrail_alarm_shall_exist_for_filter(name, filterstring) :
    """ Test that cloudtrail alarms exist for a given log filter
    ---
        name    (str) : Name of the filter to log
        filter  (str) : Log filter to look for
    """

    result = CLOUDTRAIL_TOOLS.list_trails()
    alarms = CLOUDTRAIL_CLOUDWATCH_TOOLS.list_metric_alarms()

    has_metric = False
    metric_name = ''
    has_alarm = False
    has_action = False
    for trail in result :
        group_id = ''
        groups = CLOUDTRAIL_CLOUDWATCH_TOOLS.list_groups()
        for group in groups :
            if group['arn'] == trail['CloudWatchLogsLogGroupArn'] : group_id = group['logGroupName']
        if len(group_id) == 0 :
            raise Exception('Group with arn ' + trail['CloudWatchLogsLogGroupArn'] + ' not found')
        filters = CLOUDTRAIL_CLOUDWATCH_TOOLS.list_metric_filters()
        for filt in filters :
            if 'filterPattern' in filt and \
                filt['logGroupName'] == group_id and \
                are_identical_filter(filt['filterPattern'],filterstring) :
                has_metric = True
                for metric in filt['metricTransformations'] :
                    metric_name = metric['metricName']
                    for alarm in alarms :
                        if alarm['MetricName'] == metric_name :
                            has_alarm = True
                            if 'AlarmActions' in alarm :
                                for action in alarm['AlarmActions'] :
                                    subscriptions = \
                                        CLOUDTRAIL_SNS_TOOLS.list_subscriptions_by_topic(action)
                                    for subscription in subscriptions :
                                        if 'SubscriptionArn' in subscription and \
                                            subscription['SubscriptionArn'].find("arn:aws:sns:") \
                                            >= 0 :
                                            has_action = True

    if not has_metric : raise Exception('No metric for ' + name)
    if not has_alarm : raise Exception('No alarm for ' + name)
    if not has_action : raise Exception('No action for ' + name)

def are_identical_filter(filter1, filter2) :
    """ Filters comparison function
    ---
        filter1 (str) : First filter to check
        filter2 (str) : Second filter to check
    """

    result = True

    split1 = split(r'([(|)|{|}|\s|=])\s*',filter1)
    split2 = split(r'([(|)|{|}|\s|=])\s*',filter2)

    split1_filtered = []
    for str1 in split1 :
        st1 = str1.strip()
        if len(st1) != 0 : split1_filtered.append(str1)
    split2_filtered = []
    for str2 in split2 :
        st2 = str2.strip()
        if len(st2) != 0 : split2_filtered.append(str2)

    if len(split1_filtered) != len(split2_filtered) :
        result = False
    else :
        for i in enumerate(split1_filtered) :
            if split1_filtered[i] != split2_filtered[i] :
                result = False


    return result

# pylint: enable=R1702, R0914, R0912
