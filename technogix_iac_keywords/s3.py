""" -----------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Keywords to manage s3 tasks
# -------------------------------------------------------
# Nadège LEMPERIERE, @05 october 2021
# Latest revision: 05 october 2021
# --------------------------------------------------- """

# System includes
from sys import path as syspath
from os import path
from datetime import datetime

# Robotframework includes
from robot.api import logger
from robot.api.deco import keyword
ROBOT = False

# Local includes
syspath.append(path.normpath(path.join(path.dirname(__file__), './')))
from tools.s3 import S3Tools
from tools.compare import compare_dictionaries, remove_type_from_list

# Global variable
S3_TOOLS = S3Tools()

@keyword("Initialize S3")
def intialize_s3(profile = None, access_key = None, secret_key = None, region = None) :
    """ Initialize keyword with AWS configuration
        Profile or access_key/secret_key shall be provided
        ---
        profile    (str) : AWS cli profile for SSO users authentication in aws
        access_key (str) : Access key for IAM users authentication in aws
        secret_key (str) : Secret key associated to the previous access key
        region     (str) : AWS region to use
    """
    S3_TOOLS.initialize(profile, access_key, secret_key, region)
    logger.info("Initialization performed")

@keyword("Upload S3 File")
def upload_s3_file(bucket, filename, s3object) :
    """ Upload a file to an S3 bucket
        ---
        bucket   (str) : Bucket to add file to
        filename (str) : Name of the file to upload
        s3object (str) : Object to create with file
    """
    S3_TOOLS.upload_file(bucket, filename, s3object)

@keyword("S3 Object Shall Exist")
def s3_object_shall_exist(bucket, s3object) :
    """ Tests if an object exist in bucket
        ---
        bucket   (str) : Bucket to analyze
        s3object (str) : Object to look for
    """
    result = S3_TOOLS.object_exists(bucket, s3object)
    if not result : raise Exception("S3 object " + s3object + " does not exist in bucket " + bucket)

@keyword("S3 Object Shall Not Exist")
def s3_object_shall_not_exist(bucket, s3object) :
    """ Check that an object does not exist in bucket
        ---
        bucket   (str) : Bucket to analyze
        s3object (str) : Object to look for
    """
    result = S3_TOOLS.object_exists(bucket, s3object)
    if result : raise Exception("S3 object " + s3object + " exists in bucket " + bucket)

@keyword("Can Get S3 Object")
def can_get_s3_object(bucket) :
    """ Tests if objects can be downloaded from bucket
        ---
        bucket   (str) : Bucket to use
    """
    result = S3_TOOLS.list_objects(bucket, 10)
    if len(result) == 0 : raise Exception("No S3 object found")
    result = S3_TOOLS.object_can_be_downloaded(bucket, result[0]['Key'])
    if not result : raise Exception("S3 object can not be downloaded")

@keyword("S3 Bucket Shall Exist")
def s3_bucket_shall_exist(bucket, account) :
    """ Tests if a bucket exist
        ---
        bucket   (str) : Bucket to look for
        account  (str) : Account the bucket is in
    """
    result = S3_TOOLS.bucket_exists(bucket, account)
    if not result : raise Exception("Bucket " + bucket + " does not exist")

@keyword("S3 Bucket Shall Not Exist")
def s3_bucket_shall_not_exist(bucket, account) :
    """ Check that a bucket does not exist
        ---
        bucket   (str) : Bucket to look for
        account  (str) : Account the bucket is in
    """
    result = S3_TOOLS.bucket_exists(bucket, account)
    if result : raise Exception("Bucket " + bucket + " exists")

@keyword("S3 Bucket Shall Be Accessible")
def s3_bucket_shall_be_accessible(bucket) :
    """ Tests if a bucket is accessible
        ---
        bucket   (str) : Bucket to use
    """
    result = S3_TOOLS.bucket_is_accessible(bucket)
    if not result : raise Exception("Bucket " + bucket + " is not accessible")

@keyword("S3 Bucket Shall Not Be Accessible")
def s3_bucket_shall_not_be_accessible(bucket) :
    """ Checks that a bucket is not accessible
        ---
        bucket   (str) : Bucket to use
    """
    result = S3_TOOLS.bucket_is_accessible(bucket)
    if result : raise Exception("Bucket " + bucket + " is accessible")

@keyword("Remove S3 Object")
def remove_s3_object(bucket, s3object) :
    """ Remove an object from an S3 bucket
        ---
        bucket   (str) : Bucket to update
        s3object (str) : Object to remove
    """
    S3_TOOLS.remove_object(bucket, s3object)

@keyword("Remove S3 Bucket")
def remove_s3_bucket(bucket) :
    """ Checks that a bucket is not accessible
        ---
        bucket   (str) : Bucket to use
    """
    S3_TOOLS.remove_bucket(bucket)

@keyword("Empty S3 Bucket")
def empty_s3_bucket(bucket) :
    """ Empty an S3 bucket
        ---
        bucket   (str) : Bucket to empty
    """
    S3_TOOLS.empty_bucket(bucket)

@keyword("Buckets Shall Be Encrypted")
def buckets_shall_be_encrypted(account) :
    """ Checks that all buckets are encrypted
        ---
        account  (str) : Account to check buckets from
    """
    result = S3_TOOLS.list_buckets(account)
    for bkt in result :
        if not S3_TOOLS.is_encrypted(bkt['Name'], account) :
            raise Exception ("Bucket " + bkt['Name'] + " is not encrypted")

@keyword("Buckets Shall Forbid Http Access")
def buckets_shall_forbid_http_access(account) :
    """ Checks that all buckets does not allow http access
        ---
        account  (str) : Account to check buckets from
    """
    result = S3_TOOLS.list_buckets(account)
    for bkt in result :
        if not S3_TOOLS.is_preventing_http_access(bkt['Policy']) :
            raise Exception ("Bucket " + bkt['Name'] + " allow non tls access")

@keyword("Buckets Shall Enforce MFA Enabling For Deletion")
def bucket_shall_enforce_mfa_enabling(account) :
    """ Checks that all buckets required MFA authentication for deletion
        ---
        account  (str) : Account to check buckets from
    """
    result = S3_TOOLS.list_buckets(account)
    for bkt in result :
        if not S3_TOOLS.enforce_mfa_deletion(bkt['Name'], account) :
            raise Exception("Bucket " + bkt['Name'] + " does not require MFA for deletion")

@keyword("Macie Shall Secure All Buckets")
def bucket_shall_be_analyzed_with_macie(account) :
    """ Checks that all buckets are anlyzed using macie
        ---
        account  (str) : Account to check buckets from
    """
    result = S3_TOOLS.list_buckets(account)
    for bkt in result :
        if not S3_TOOLS.ensure_macie_is_activated(bkt['Name'], account) :
            raise Exception("Bucket " + bkt['Name'] + " is not analyzed using Macie")

@keyword("Buckets Shall Forbid Public Access")
def bucket_shall_block_public_access(account) :
    """ Checks that all buckets block public access
        ---
        account  (str) : Account to check buckets from
    """
    result = S3_TOOLS.list_buckets(account)
    for bkt in result :
        if  'PublicAccessBlockConfiguration' in bkt and \
            (   not bkt['PublicAccessBlockConfiguration']['BlockPublicAcls'] or \
                not bkt['PublicAccessBlockConfiguration']['IgnorePublicAcls'] or \
                not bkt['PublicAccessBlockConfiguration']['BlockPublicPolicy'] or \
                not bkt['PublicAccessBlockConfiguration']['RestrictPublicBuckets']) :
            raise Exception("Bucket " + bkt['Name'] + " does not block public access")

@keyword('Buckets Shall Exist And Match')
def buckets_shall_exist_and_match(specs, account) :
    """ Check that a bucket exists that matches the specifications
        ---
        specs    (list) : List of specifications to consider
    """
    result = S3_TOOLS.list_buckets(account)
    result = remove_type_from_list(result, datetime)
    for spec in specs :
        found = False
        for bucket in result :
            if compare_dictionaries(spec['data'], bucket) :
                found = True
                logger.info('Bucket ' + spec['name'] + ' matches bucket ' + bucket['Name'])
        if not found : raise Exception('Bucket ' + spec['name'] + ' does not match')
