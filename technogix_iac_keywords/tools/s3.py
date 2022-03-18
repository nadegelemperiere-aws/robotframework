""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Tool functions used by s3 keywords
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path
from json import loads, dumps

# Robotframework includes
from robot.api import logger
ROBOT = False

# Local include
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tool import Tool

# pylint: disable=R0916, R0201, R0912, R0915, C0301, R1702
class S3Tools(Tool) :
    """ Class providing tools to check AWS S3 compliance """

    def __init__(self):
        """ Constructor """
        super().__init__()
        self.m_services.append('s3')
        self.m_services.append('macie')

    def upload_file(self, bucket, filename, s3object) :
        """ Upload file to an s3 bucket
            ---
            bucket   (str) : Bucket to update
            filename (str) : Name of the file to add to bucket
            s3object (str) : Object to give to file in bucket
        """

        if self.m_is_active['s3'] :
            self.m_clients['s3'].upload_file(filename, bucket, s3object)

    def remove_object(self, bucket, s3object) :
        """ Remove an object from bucket if it exists
            ---
            bucket   (str) : Bucket to update
            s3object (str) : Object to remove in bucket
        """

        if self.m_is_active['s3'] :
            paginator = self.m_clients['s3'].get_paginator('list_objects')
            response_iterator = paginator.paginate(Bucket=bucket)
            shall_continue = True
            for response in response_iterator :
                if shall_continue :
                    if 'Contents' in response :
                        for obj in response['Contents'] :
                            if obj['Key'] == s3object :
                                self.m_clients['s3'].delete_object(Bucket=bucket, Key=s3object)
                                shall_continue = False

    def empty_bucket(self, bucket) :
        """ Empty a bucket
            ---
            bucket   (str) : Bucket to empty
        """

        if self.m_is_active['s3'] :
            paginator = self.m_clients['s3'].get_paginator('list_object_versions')
            response_iterator = paginator.paginate(Bucket=bucket)
            for response in response_iterator :
                if 'Versions' in response :
                    for obj in response['Versions'] :
                        key = obj['Key']
                        vid = obj['VersionId']
                        self.m_clients['s3'].delete_object(Bucket=bucket, Key=key, VersionId=vid)
                if 'DeleteMarkers' in response :
                    for obj in response['DeleteMarkers'] :
                        key = obj['Key']
                        vid = obj['VersionId']
                        self.m_clients['s3'].delete_object(Bucket=bucket, Key=key, VersionId=vid)

    def remove_bucket(self, bucket) :
        """ Remove an existing bucket
            ---
            bucket   (str) : Bucket to delete
        """
        if self.m_is_active['s3'] :
            self.m_clients['s3'].delete_bucket(Bucket=bucket)

    def list_buckets(self, account) :
        """ List all buckets in that are accessible in environment
            ---
            account   (str) : Account to analyze
            ---
            returns  (list) : List of all the account buckets
        """

        result = []

        if self.m_is_active['s3'] :
            response = self.m_clients['s3'].list_buckets()
            for bkt in response['Buckets'] :
                name = bkt['Name']
                try :
                    is_accessible = self.m_clients['s3'].head_bucket(Bucket=name)
                except Exception : is_accessible = False
                if is_accessible :
                    try :
                        lifecycle = self.m_clients['s3'].get_bucket_lifecycle_configuration(Bucket=name)
                    except Exception : lifecycle = {'Rules' : []}
                    bkt['Rules'] = lifecycle['Rules']
                    try :
                        policy = self.m_clients['s3'].get_bucket_policy(Bucket = name)
                    except Exception : policy = {'Policy' : '{}'}
                    bkt['Policy'] = loads(policy['Policy'])
                    try :
                        encryption = self.m_clients['s3'].get_bucket_encryption(Bucket = name)
                    except Exception : encryption = {'ServerSideEncryptionConfiguration' : {}}
                    bkt['ServerSideEncryptionConfiguration'] = \
                        encryption['ServerSideEncryptionConfiguration']
                    try :
                        public = self.m_clients['s3'].get_public_access_block(Bucket = name, \
                            ExpectedBucketOwner = account)
                    except Exception : public = {'PublicAccessBlockConfiguration' : {}}
                    bkt['PublicAccessBlockConfiguration'] = public['PublicAccessBlockConfiguration']
                    try :
                        acl = self.m_clients['s3'].get_bucket_acl(Bucket = name, \
                            ExpectedBucketOwner = account)
                    except Exception : acl = {'Grants' : {}}
                    bkt['Grants'] = acl['Grants']
                    try :
                        public = self.m_clients['s3'].get_bucket_policy_status(Bucket = name, \
                            ExpectedBucketOwner = account)
                    except Exception : public = {'PolicyStatus' : {}}
                    bkt['PolicyStatus'] = public['PolicyStatus']
                    try :
                        tags = self.m_clients['s3'].get_bucket_tagging(Bucket = name, \
                            ExpectedBucketOwner = account)
                    except Exception : tags = {'TagSet' : {}}
                    bkt['Tags'] = tags['TagSet']
                    try :
                        log = self.m_clients['s3'].get_bucket_logging(Bucket = name, \
                            ExpectedBucketOwner = account)
                    except Exception : log = {'LoggingEnabled' : {}}
                    if 'LoggingEnabled' in log : bkt['LoggingEnabled'] = log['LoggingEnabled']
                    else : bkt['LoggingEnabled'] =  {}

                    result.append(bkt)

        return result

    def list_objects(self, bucket, number) :
        """ List all objects in bucket
            ---
            bucket   (str)  : Bucket to analyze
            number   (int)  : Maximal number of object to retrieve in bucket
            ---
            returns  (list) : List of the n first bucket objects
        """

        result = []

        if self.m_is_active['s3'] :
            paginator = self.m_clients['s3'].get_paginator('list_objects')
            response_iterator = paginator.paginate(Bucket=bucket)
            shall_continue = True
            for response in response_iterator :
                if shall_continue :
                    if 'Contents' in response :
                        for obj in response['Contents'] :
                            if len(result) < number and obj["Size"] != 0 : result.append(obj)
                            else : shall_continue = False

        return result


    def object_exists(self, bucket, s3object) :
        """ Test if a file exists in bucket
            ---
            bucket   (str)  : Bucket to analyze
            s3object (str)  : Object to look for in bucket
            ---
            returns  (bool) : True if objects exists in bucket, False otherwise
        """

        result = False

        if self.m_is_active['s3'] :
            paginator = self.m_clients['s3'].get_paginator('list_objects')
            response_iterator = paginator.paginate(Bucket=bucket, Prefix=s3object)
            for response in response_iterator :
                if 'Contents' in response :
                    for obj in response['Contents'] :
                        if obj['Key'] == s3object : result = True

        return result

    def bucket_exists(self, bucket, account) :
        """ Test if a bucket exists
            ---
            bucket   (str)  : Bucket to analyze
            account  (str)  : Account to analyze
            ---
            returns  (bool) : True if bucket exists, False otherwise
        """

        result = False

        result = self.list_buckets(account)
        for bkt in result :
            if bkt['Name'] == bucket : result = True

        return result

    def bucket_is_accessible(self, bucket) :
        """ Test if a bucket is accessible by user
            ---
            bucket   (str)  : Bucket to analyze
            ---
            returns  (bool) : True if bucket is accessible, False otherwise
        """
        result = False

        try :
            if self.m_is_active['s3'] :
                is_accessible = self.m_clients['s3'].head_bucket(Bucket=bucket)
                logger.info(dumps(is_accessible))
            result = True
        except Exception : result = False

        return result

    def is_encrypted(self, bucket, account) :
        """ Test if a bucket is encrypted
            ---
            bucket   (str)  : Bucket to analyze
            account  (str)  : Account in which the bucket is located
            ---
            returns  (bool) : True if bucket is encrypted, False otherwise
        """

        result = False


        if self.m_is_active['s3'] :
            response = self.m_clients['s3'].get_bucket_encryption(Bucket = bucket, \
                ExpectedBucketOwner = account)
            if 'ServerSideEncryptionConfiguration' in response :
                for rule in response['ServerSideEncryptionConfiguration'] ['Rules']:
                    if 'ApplyServerSideEncryptionByDefault' in rule :
                        if  rule['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] == 'AES256' or \
                            rule['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] == 'aws:kms' :
                            result = True

        return result

    def object_can_be_downloaded(self, bucket, s3object) :
        """ Test if an object can be downloaded by user
            ---
            bucket   (str)  : Bucket to analyze
            s3object (str)  : Object to download
            ---
            returns  (bool) : True if object can be downloaded by user, False otherwise
        """
        result = False

        if self.m_is_active['s3'] :
            response = self.m_clients['s3'].get_object(Bucket = bucket, Key = s3object)
            if 'LastModified 'in response : del response['LastModified']
            if 'Expires' in response : del response['Expires']
            if 'ObjectLockRetainUntilDate' in response : del response['ObjectLockRetainUntilDate']
            del response['Body']
            logger.info(response['ContentLength'])
            if response['ContentLength'] != 0 : result = True

        return result

    def enforce_mfa_deletion(self, bucket, account) :
        """ Test if user shall be authentified with MFA to destroy a bucket
            ---
            bucket  (str)  : Bucket to analyze
            account (str)  : Account in which the bucket is located
            ---
            returns (bool) : True if MFA is required, False otherwise
        """

        result = False


        if self.m_is_active['s3'] :
            response = self.m_clients['s3'].get_bucket_versioning(Bucket = bucket, \
                ExpectedBucketOwner = account)
            if  'Status' in response and response['Status'] == 'Enabled' and \
                'MFADelete' in response and response['MFADelete'] == 'Enabled' : result = True

        return result

    def get_acls(self, bucket, account) :
        """ Returns bucket access control list
            ---
            bucket  (str)  : Bucket to analyze
            account (str)  : Account in which the bucket is located
            ---
            returns (list) : List of buckets access control lists
        """

        result = []
        if self.m_is_active['s3'] :
            response = self.m_clients['s3'].get_bucket_acl(Bucket = bucket, \
                ExpectedBucketOwner = account)
            logger.debug(response)
            result = response['Grants']

        return result

    def get_policy(self, bucket, account) :
        """ Returns bucket access policy
            ---
            bucket  (str)  : Bucket to analyze
            account (str)  : Account in which the bucket is located
            ---
            returns (dict) : Bucket policy
        """

        result = {}

        if self.m_is_active['s3'] :
            response = self.m_clients['s3'].get_bucket_policy(Bucket = bucket, \
                ExpectedBucketOwner = account)
            result = loads(response['Policy'])

        return result

    def get_public_access_block(self, bucket, account) :
        """ Returns bucket public access configuration
            ---
            bucket  (str)  : Bucket to analyze
            account (str)  : Account in which the bucket is located
            ---
            returns (dict)  : Bucket public access configuration
        """

        result = {}

        if self.m_is_active['s3'] :
            response = self.m_clients['s3'].get_public_access_block(Bucket = bucket, \
                ExpectedBucketOwner = account)
            result = response['PublicAccessBlockConfiguration']

        return result

    def get_logging(self, bucket, account) :
        """ Returns bucket access logging configuration
            ---
            bucket  (str)  : Bucket to analyze
            account (str)  : Account in which the bucket is located
            ---
            returns (dict) : Bucket access logging configuration
        """

        result = {}

        if self.m_is_active['s3'] :
            response = self.m_clients['s3'].get_bucket_logging(Bucket = bucket, \
                ExpectedBucketOwner = account)
            if 'LoggingEnabled' in response :   result =  response['LoggingEnabled']

        return result

    def ensure_macie_is_activated(self, bucket, account) :
        """ Returns bucket macie analysis configuration
            ---
            bucket  (str)  : Bucket to analyze
            account (str)  : Account in which the bucket is located
            ---
            returns (bool) : True if the bucket is analyzed by macie, False otherwise
        """

        result = False

        if self.m_is_active['macie'] :
            response = self.m_clients['macie'].list_s3_resources( memberAccountId=account )
            for bkt in response['s3Resources'] :
                if  bkt['bucketName'] == bucket and \
                    'continuous' in bkt['classificationType'] and \
                    bkt['classificationType']['continuous'] == 'FULL' :
                    result = True

        return result

    def is_preventing_http_access(self, policy) :
        """ Returns policy TLS enforcement
            ---
            policy  (dict) : Policy to analyze
            ---
            returns (bool) : True if the policy allows only https access, False otherwise
        """

        result = False
        content = policy['Statement']
        if isinstance(content,str) :
            if content['Effect'] == 'Deny' :
                if  (   'Action' in content and
                        (   (isinstance(content['Action'],str) and
                                (   content['Action'] == '*' or
                                    content['Action'] == "s3:*")) or \
                            (isinstance(content['Action'],list) and
                                (   '*' in content['Action'] or
                                    's3:*' in content['Action'])))) and \
                    (   'Condition' in content and
                        'Bool' in content['Condition'] and
                        'aws:SecureTransport' in content['Condition']['Bool'] and
                        content['Condition']['Bool']['aws:SecureTransport'] == 'false') :
                    result = True
        elif isinstance(content,list) :
            for statement in content :
                print(dumps(statement))
                if statement['Effect'] == 'Deny' :
                    if  (   'Action' in statement and
                            (   (isinstance(statement['Action'],str) and
                                    (   statement['Action'] == '*' or
                                        statement['Action'] == "s3:*")) or \
                                (isinstance(statement['Action'],list) and
                                    (   '*' in statement['Action'] or
                                        's3:*' in statement['Action'])))) and \
                        (   'Condition' in statement and
                            'Bool' in statement['Condition'] and
                            'aws:SecureTransport' in statement['Condition']['Bool'] and
                            statement['Condition']['Bool']['aws:SecureTransport'] == 'false') :
                        result = True

        return result


    def is_preventing_anonymous_access(self, policy) :
        """ Returns policy anonymous access status
            ---
            policy  (dict) : Policy to analyze
            ---
            returns (bool) : True if the policy allows anonymous access, False otherwise
        """

        result = True
        logger.info(dumps(policy))
        if isinstance(policy,dict) : logger.info('is dict')
        logger.info(str(type(policy)))
        content = policy['Statement']
        logger.info(dumps(content))
        if isinstance(content,str) :
            if content['Effect'] == 'Allow' :
                if  (   'Principal' in content and
                        (   (isinstance(content['Principal'],str) and \
                                content['Principal'] == '*') or \
                            (isinstance(content['Principal'],dict) and \
                                'AWS' in content['Principal'] and \
                                isinstance(content['Principal']['AWS'],str) \
                                and content['Principal']['AWS'] == "*")) or \
                        (isinstance(content['Principal'],dict) and \
                            'AWS' in content['Principal'] and \
                            isinstance(content['Principal']['AWS'],list) and \
                            '*' in content['Principal']['AWS'])) :
                    result = False
        elif isinstance(content,list) :
            for statement in content :
                logger.info(dumps(statement))
                if statement['Effect'] == 'Allow' :
                    if  (   'Principal' in statement and
                        (   (isinstance(statement['Principal'],str) and \
                            statement['Principal'] == '*') or \
                        (isinstance(statement['Principal'],dict) and \
                            'AWS' in statement['Principal'] and \
                            isinstance(statement['Principal']['AWS'],str) and \
                            statement['Principal']['AWS'] == "*")) or \
                        (isinstance(statement['Principal'],dict) and \
                            'AWS' in statement['Principal'] and \
                            isinstance(statement['Principal']['AWS'],list) and \
                            '*' in statement['Principal']['AWS'])) :
                        result = False

        return result

# pylint: enable=R0916, R0201, R0912, R0915, C0301, R1702
