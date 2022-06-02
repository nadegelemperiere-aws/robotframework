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

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool

class ConfigTools(Tool) :
    """ Class providing tools to check AWS codecommit compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('config')

    def list_recorders(self) :
        """ List config recorders in AWS account """

        result = []

        if self.m_is_active['config'] :
            response = self.m_clients['config'].describe_configuration_recorders()
            for recorder in response['ConfigurationRecorders'] :
                status = self.m_clients['config'].describe_configuration_recorder_status(\
                    ConfigurationRecorderNames=[recorder['name']])
                recorder['Status'] = status['ConfigurationRecordersStatus'][0]['recording']
                result.append(recorder)

        return result

    def list_resources(self) :
        """ List all AWS resources """

        result = []

        resources = ["AWS::EC2::CustomerGateway", "AWS::EC2::EIP", "AWS::EC2::Host", \
             "AWS::EC2::Instance", "AWS::EC2::InternetGateway", "AWS::EC2::NetworkAcl", \
             "AWS::EC2::NetworkInterface", "AWS::EC2::RouteTable", "AWS::EC2::SecurityGroup", \
             "AWS::EC2::Subnet", "AWS::CloudTrail::Trail", "AWS::EC2::Volume", "AWS::EC2::VPC", \
             "AWS::EC2::VPNConnection", "AWS::EC2::VPNGateway", "AWS::EC2::RegisteredHAInstance", \
             "AWS::EC2::NatGateway", "AWS::EC2::EgressOnlyInternetGateway", \
             "AWS::EC2::VPCEndpoint", "AWS::EC2::VPCEndpointService", "AWS::EC2::FlowLog", \
             "AWS::EC2::VPCPeeringConnection", "AWS::IAM::Group", "AWS::IAM::Policy", \
             "AWS::IAM::Role", "AWS::IAM::User", "AWS::ElasticLoadBalancingV2::LoadBalancer", \
             "AWS::ACM::Certificate", "AWS::RDS::DBInstance", "AWS::RDS::DBParameterGroup", \
             "AWS::RDS::DBOptionGroup", "AWS::RDS::DBSubnetGroup", "AWS::RDS::DBSecurityGroup", \
             "AWS::RDS::DBSnapshot", "AWS::RDS::DBCluster", "AWS::RDS::DBClusterParameterGroup", \
             "AWS::RDS::DBClusterSnapshot", "AWS::RDS::EventSubscription", "AWS::S3::Bucket", \
             "AWS::S3::AccountPublicAccessBlock", "AWS::Redshift::Cluster", \
             "AWS::Redshift::ClusterSnapshot", "AWS::Redshift::ClusterParameterGroup", \
             "AWS::Redshift::ClusterSecurityGroup", "AWS::Redshift::ClusterSubnetGroup", \
             "AWS::Redshift::EventSubscription", "AWS::SSM::ManagedInstanceInventory", \
             "AWS::CloudWatch::Alarm", "AWS::CloudFormation::Stack", \
             "AWS::ElasticLoadBalancing::LoadBalancer", "AWS::AutoScaling::AutoScalingGroup", \
             "AWS::AutoScaling::LaunchConfiguration", "AWS::AutoScaling::ScalingPolicy", \
             "AWS::AutoScaling::ScheduledAction", "AWS::DynamoDB::Table", \
             "AWS::CodeBuild::Project", "AWS::WAF::RateBasedRule", "AWS::WAF::Rule", \
             "AWS::WAF::RuleGroup", "AWS::WAF::WebACL", "AWS::WAFRegional::RateBasedRule", \
             "AWS::WAFRegional::Rule", "AWS::WAFRegional::RuleGroup", "AWS::WAFRegional::WebACL", \
             "AWS::CloudFront::Distribution", "AWS::CloudFront::StreamingDistribution", \
             "AWS::Lambda::Alias", "AWS::Lambda::Function", "AWS::ElasticBeanstalk::Application", \
             "AWS::ElasticBeanstalk::ApplicationVersion", "AWS::ElasticBeanstalk::Environment", \
             "AWS::MobileHub::Project", "AWS::XRay::EncryptionConfig", \
             "AWS::SSM::AssociationCompliance", "AWS::SSM::PatchCompliance", \
             "AWS::Shield::Protection", "AWS::ShieldRegional::Protection", \
             "AWS::Config::ResourceCompliance", "AWS::LicenseManager::LicenseConfiguration", \
             "AWS::ApiGateway::DomainName", "AWS::ApiGateway::Method", "AWS::ApiGateway::Stage", \
             "AWS::ApiGateway::RestApi", "AWS::ApiGatewayV2::DomainName", \
             "AWS::ApiGatewayV2::Stage", "AWS::ApiGatewayV2::Api", "AWS::CodePipeline::Pipeline", \
             "AWS::ServiceCatalog::CloudFormationProvisionedProduct", \
             "AWS::ServiceCatalog::CloudFormationProduct", "AWS::ServiceCatalog::Portfolio"]
        for resource in resources:

            paginator = self.m_clients['config'].get_paginator('list_discovered_resources')
            response_iterator = paginator.paginate(resourceType=resource)
            for response in response_iterator :
                result = result + response['resourceIdentifiers']

        return result

    def list_rules(self) :
        """ List all AWS config rules """

        result = []

        if self.m_is_active['config'] :
            paginator = self.m_clients['config'].get_paginator('describe_config_rules')
            response_iterator = paginator.paginate()
            for rule in response_iterator :
                result = result + rule['ConfigRules']

        return result
