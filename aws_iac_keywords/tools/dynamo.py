""" -----------------------------------------------------
# Copyright (c) [2022] Nadege Lemperiere
# All rights reserved
# -------------------------------------------------------
# Keywords to manage dynamodb tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @06 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path
from json import loads

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool

class DynamoDBTools(Tool) :
    """ Class providing tools to check AWS codecommit compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('dynamodb')

    def create_item(self, table, item) :
        """ Create an item in a dynamodb table
            ---
            table (str) : Dynamodb table to update
            item  (str) : Item to add in dynamodb
        """

        if self.m_is_active['dynamodb'] :
            json_item = loads(item)
            self.m_clients['dynamodb'].put_item(TableName=table, Item=json_item)

    def remove_item(self, table, item) :
        """ Remove an item from a dynamodb table if it exists
            ---
            table (str) : Dynamodb table to update
            item  (str) : Item to remove from dynamodb
        """
        if self.m_is_active['dynamodb'] :
            json_item = loads(item)
            self.m_clients['dynamodb'].delete_item(TableName=table, Key=json_item)

    def item_exists(self, table, item) :
        """ Test if an item in a dynamodb table
            ---
            table (str) : Dynamodb table to analyze
            item  (str) : Item to look for in dynamodb
        """

        result = False
        if self.m_is_active['dynamodb'] :
            json_item = loads(item)
            response = self.m_clients['dynamodb'].get_item(TableName=table, Key=json_item)
            if 'Item' in response : result = True

        return result

    def list_tables(self) :
        """ List all tables in account """

        result = []

        if self.m_is_active['dynamodb'] :
            paginator = self.m_clients['dynamodb'].get_paginator('list_tables')
            response_iterator = paginator.paginate()
            for response in response_iterator :
                for table in response['TableNames'] :
                    description = self.m_clients['dynamodb'].describe_table(TableName = table)
                    description['Table']['Tags'] = []
                    tags = self.m_clients['dynamodb'].get_paginator('list_tags_of_resource')
                    tag_iterator = tags.paginate(ResourceArn=description['Table']['TableArn'])
                    for tag in tag_iterator :
                        description['Table']['Tags'] = description['Table']['Tags'] + tag['Tags']

                    result.append(description['Table'])

        return result
