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

# System includes
from sys import path as syspath
from json import dumps
from os import path
from datetime import datetime

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.ec2 import EC2Tools
from tools.compare import compare_dictionaries, remove_type_from_dictionary, remove_type_from_list

# Global variable
EC2_TOOLS = EC2Tools()

@keyword('Initialize EC2')
def intialize_ec2(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    EC2_TOOLS.initialize(profile, access_key, secret_key, region=region)
    logger.info('Initialization performed')

@keyword('Get All Other Regions')
def get_all_regions(regions = None) :
    """ Retrieve all existing AWS regions other than the input one """

    result = []
    all_regions = EC2_TOOLS.list_regions()
    for region in all_regions :
        if regions is None or not region['RegionName'] in regions :
            result.append(region['RegionName'])

    return result

@keyword('EC2 Volumes Shall Be Encrypted')
def ec2_volumes_encrypted() :
    """ Tests if EC2 volumes are encrypted """
    if not EC2_TOOLS.is_ebs_encryption_activated():
        raise Exception('EBS encryption is not activated for current region')

@keyword('VPC Flow Logs Shall Be Active')
def vpc_flow_logs_shall_be_active() :
    """ Check if VPC log flows are all active """
    result = EC2_TOOLS.list_flow_logs()
    for flow in result :
        if 'FlowLogStatus' not in flow or flow['FlowLogStatus'] != 'ACTIVE' :
            raise Exception('Flow ' + flow['FlowLogId'] + ' is inactive')
        if 'DeliverLogsStatus' not in flow or flow['DeliverLogsStatus'] != 'SUCCESS' :
            raise Exception('Flow ' + flow['FlowLogId'] + ' does not deliver logs')

@keyword('No VPC In Regions')
def no_vpc_in_regions(regions, access_key, secret_key) :
    """ Check that no resource exists in regions other than the ones provided
        ---
        resions    (list) : List of regions not allowed for hosting
        access_key (str)  : Access key for IAM users authentication in aws
        secret_key (str)  : Secret key associated to the previous access key
    """
    local_tools = EC2Tools()
    for region in regions :
        local_tools.initialize(None, access_key, secret_key, region = region)
        vpcs = local_tools.list_vpcs()
        if len(vpcs) != 0 : raise Exception('Found vpc ' + dumps(vpcs[0]) + \
            ' in region ' + region)

@keyword('NACL Shall Not Permit Administration Access From Internet')
def nacl_shall_not_permit_administration_access_from_internet() :
    """ Check that access control list do not allow internet access """
    result = EC2_TOOLS.list_network_acls()
    for nacl in result :
        for entry in nacl['Entries'] :
            if EC2_TOOLS.nacl_allow_remote_administration_access(entry) :
                raise Exception('acl rule ' + str(entry['RuleNumber']) + ' for acl ' + \
                    nacl['NetworkAclId'] + ' allows administration access from the internet')

@keyword('Security Group Shall Not Permit Administration Access From Internet')
def security_group_shall_not_permit_administration_access_from_internet() :
    """ Check that security groups do not allow internet access """
    result = EC2_TOOLS.list_security_groups_rules()
    for rule in result :
        logger.info(dumps(rule))
        name = str(rule['SecurityGroupRuleId'])
        if EC2_TOOLS.rule_allow_remote_administration_access(rule) :
            raise Exception('Security group ' + name + ' for group ' + rule['GroupId'] + \
                 ' allows administration access from the internet')

@keyword('Default Security Group Shall Block All Traffic')
def default_security_group_shall_block_all_traffic() :
    """ Check that default security groups block all traffic by default """
    result = EC2_TOOLS.list_vpc_default_security_groups()
    for group in result :
        logger.info(dumps(group))
        name = str(group['GroupId'])
        if len(group['IpPermissions']) > 0 :
            raise Exception('Default security group ' + name + ' contains ingress rules')
        if len(group['IpPermissionsEgress']) > 0 :
            raise Exception('Default security group ' + name + ' contains egress rules')

@keyword('Peering Network Routes Shall Be Specific')
def peering_network_routes_shall_be_specific() :
    """ Check that peering network routes are specific """
    result = EC2_TOOLS.list_route_tables()
    for table in result :
        logger.info(dumps(table))
        for route in table['Routes'] :
            if 'gatewayId' in route and \
                route['GatewayId'][0:2] == 'pcx' :
                #If peering route
                if route['DestinationCidrBlock'] != '' :
                    name = route['DestinationCidrBlock']
                    raise Exception('Invalid peering route destination for route ' + name)
            elif    'EgressOnlyInternetGatewayId' in route and \
                    route['EgressOnlyInternetGatewayId'][0:2] == 'pcx' :
                #If peering route
                if route['DestinationCidrBlock'] != '' :
                    name = route['DestinationCidrBlock']
                    raise Exception('Invalid peering route destination for route ' + name)

@keyword('Subnets Shall Exist')
def subnets_shall_exist(subnets) :
    """ Check that subnets exist
        ---
        subnets  (list) : List of subnets to look for
    """
    for subnet in subnets :
        result = EC2_TOOLS.subnet_exists(subnet)
        if not result : raise Exception('Subnet ' + subnet + ' does not exist')

@keyword('EC2 IAM Roles Policy Shall Be Enabled')
def ec2_iam_roles_policy_shall_be_enabled() :
    """ Check that EC2 instances IAM roles policy is set
    """
    result = EC2_TOOLS.list_instances()
    for instance in result :
        logger.info(dumps(instance))
        raise Exception('Instance found : should finalize keyword')

@keyword('Subnets Shall Exist And Match')
def subnets_shall_exist_and_match(specs) :
    """ Check that a subnet exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """

    result = EC2_TOOLS.list_subnets()
    for spec in specs :
        found = False
        for subnet in result :
            if compare_dictionaries(spec['data'], subnet) :
                found = True
                logger.info('Subnet ' + spec['name'] + ' matches subnet ' + subnet['SubnetId'])
        if not found : raise Exception('Subnet ' + spec['name'] + ' does not match')

@keyword('NACL Shall Exist')
def nacl_shall_exist(nacls) :
    """ Check that a nacl exists
        ---
        nacls    (list) : List of nacls to look for
    """
    for nacl in nacls :
        result = EC2_TOOLS.nacl_exists(nacl)
        if not result : raise Exception('NACL ' + nacl + ' does not exist')

@keyword('Customer Images Shall Not Be Public')
def customer_images_shall_not_be_public(accounts) :
    """ Check that self owned images are not public
    ---
    accounts (list) : AWS accounts owning the images
    """

    result = EC2_TOOLS.list_images(owners=accounts)
    for image in result :
        if image['OwnerId'] in accounts and image['Public'] :
            raise Exception('Image ' + image['ImageId'] + ' is public')


@keyword('NACL Shall Exist And Match')
def nacl_shall_exist_and_match(specs) :
    """ Check that a nacl exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = EC2_TOOLS.list_network_acls()
    for spec in specs :
        found = False
        for nacl in result :
            if compare_dictionaries(spec['data'], nacl) :
                found = True
                logger.info('NACL ' + spec['name'] + ' matches nacl ' + nacl['NetworkAclId'])
        if not found : raise Exception('NACL ' + spec['name'] + ' does not match')

@keyword('VPC Shall Exist And Match')
def vpc_shall_exist_and_match(specs) :
    """ Check that a vpc exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = EC2_TOOLS.list_vpcs()
    for spec in specs :
        found = False
        for vpc in result :
            if compare_dictionaries(spec['data'], vpc) :
                found = True
                logger.info('VPC ' + spec['name'] + ' matches nacl ' + vpc['VpcId'])
        if not found : raise Exception('VPC ' + spec['name'] + ' does not match')

@keyword('Route Table Shall Exist And Match')
def route_table_shall_exist_and_match(specs) :
    """ Check that a route table exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = EC2_TOOLS.list_route_tables()
    for spec in specs :
        found = False
        for route in result :
            if compare_dictionaries(spec['data'], route) :
                found = True
                name = route['RouteTableId']
                logger.info('Route table ' + spec['name'] + ' matches route table ' + name)
        if not found : raise Exception('Route table ' + spec['name'] + ' does not match')

@keyword('Security Group Shall Exist And Match')
def security_group_shall_exist_and_match(specs) :
    """ Check that a security group exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = EC2_TOOLS.list_vpc_security_groups()
    for spec in specs :
        found = False
        for sgr in result :
            if compare_dictionaries(spec['data'], sgr) :
                found = True
                name = sgr['GroupId']
                logger.info('Security Group ' + spec['name'] + ' matches security group ' + name)
        if not found : raise Exception('Security Group ' + spec['name'] + ' does not match')


@keyword('Internet Gateway Shall Exist And Match')
def internet_gateway_shall_exist_and_match(specs) :
    """ Check that an internet gateway exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = EC2_TOOLS.list_internet_gateways()
    for spec in specs :
        found = False
        for gateway in result :
            if compare_dictionaries(spec['data'], gateway) :
                found = True
                name = gateway['InternetGatewayId']
                logger.info('Gateway ' + spec['name'] + ' matches gateway ' + name)
        if not found : raise Exception('Internet gateway ' + spec['name'] + ' does not match')

@keyword('Endpoints Shall Exist And Match')
def endpoints_shall_exist_and_match(specs) :
    """ Check that a service endpoint exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = EC2_TOOLS.list_vpc_endpoints()
    for spec in specs :
        found = False
        for endpoint in result :
            if 'CreationTimestamp' in endpoint : del endpoint['CreationTimestamp']
            if compare_dictionaries(spec['data'], endpoint) :
                found = True
                name = endpoint['ServiceName']
                logger.info('Endpoint ' + spec['name'] + ' matches endpoint ' + name)
        if not found : raise Exception('Endpoint ' + spec['name'] + ' does not match')

@keyword('Flow Logs Shall Exist And Match')
def flow_logs_shall_exist_and_match(specs) :
    """ Check that a flow log exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = EC2_TOOLS.list_flow_logs()
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for flow in result :
            if compare_dictionaries(spec['data'], flow) :
                found = True
                logger.info('Flow ' + spec['name'] + ' matches flow ' + flow['FlowLogId'])
        if not found : raise Exception('Flow ' + spec['name'] + ' does not match')

@keyword('Instances Shall Exist And Match')
def instances_shall_exist_and_match(specs) :
    """ Check that an instance exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = EC2_TOOLS.list_instances()
    for spec in specs :
        found = False
        for instance in result :
            instance = remove_type_from_dictionary(instance, datetime)
            if compare_dictionaries(spec['data'], instance) :
                found = True
                name = instance['InstanceId']
                logger.info('Instance ' + spec['name'] + ' matches instance ' + name)
        if not found : raise Exception('Instance ' + spec['name'] + ' does not match')

@keyword('Network Interfaces Shall Exist And Match')
def network_interfaces_shall_exist_and_match(specs) :
    """ Check that a network interfaces exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = EC2_TOOLS.list_network_interfaces()
    for spec in specs :
        found = False
        for interface in result :
            interface = remove_type_from_dictionary(interface, datetime)
            if compare_dictionaries(spec['data'], interface) :
                found = True
                name = interface['PrivateDnsName']
                logger.info('Interface ' + spec['name'] + ' matches interface ' + name)
        if not found : raise Exception('Interface ' + spec['name'] + ' does not match')

@keyword('Volumes Shall Exist And Match')
def volumes_shall_exist_and_match(specs) :
    """ Check that a network volume exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = EC2_TOOLS.list_volumes()
    for spec in specs :
        found = False
        for volume in result :
            volume = remove_type_from_dictionary(volume, datetime)
            if compare_dictionaries(spec['data'], volume) :
                found = True
                logger.info('Volume ' + spec['name'] + ' matches volume ' + volume['VolumeId'])
        if not found : raise Exception('Volume ' + spec['name'] + ' does not match')
