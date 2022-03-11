""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage dynamodb tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @06 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from json import loads

# Aws includes
from boto3 import Session

class DynamoDBTools :
    """ Class providing tools to check AWS dynamodb compliance """

    # S3 session
    m_session = None

    # S3 client
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
        self.m_client = self.m_session.client('dynamodb', region_name=region)

    def create_item(self, table, item) :
        """ Create an item in a dynamodb table
            ---
            table (str) : Dynamodb table to update
            item  (str) : Item to add in dynamodb
        """
        json_item = loads(item)
        self.m_client.put_item(TableName=table, Item=json_item)

    def remove_item(self, table, item) :
        """ Remove an item from a dynamodb table if it exists
            ---
            table (str) : Dynamodb table to update
            item  (str) : Item to remove from dynamodb
        """
        json_item = loads(item)
        self.m_client.delete_item(TableName=table, Key=json_item)

    def item_exists(self, table, item) :
        """ Test if an item in a dynamodb table
            ---
            table (str) : Dynamodb table to analyze
            item  (str) : Item to look for in dynamodb
        """

        result = False
        json_item = loads(item)
        response = self.m_client.get_item(TableName=table, Key=json_item)
        if 'Item' in response : result = True

        return result


    def list_tables(self) :
        """ List all tables in account """

        result = []

        paginator = self.m_client.get_paginator('list_tables')
        response_iterator = paginator.paginate()
        for response in response_iterator :
            for table in response['TableNames'] :
                description = self.m_client.describe_table(TableName = table)
                description['Table']['Tags'] = []
                tags = self.m_client.get_paginator('list_tags_of_resource')
                tag_iterator = tags.paginate(ResourceArn=description['Table']['TableArn'])
                for tag in tag_iterator :
                    description['Table']['Tags'] = description['Table']['Tags'] + tag['Tags']

                result.append(description['Table'])

        return result
