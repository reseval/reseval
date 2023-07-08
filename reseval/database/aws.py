import os
import time

import boto3

import reseval


###############################################################################
# AWS RDS database management
###############################################################################


def create(name):
    """Create a MySQL database on AWS"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Connect to AWS RDS
    client = connect()

    # Create database
    response = client.create_db_instance(
        DBName=unique,
        DBInstanceIdentifier=unique,
        DBInstanceClass='db.t2.micro',
        Engine='mysql',
        MasterUsername='root',
        MasterUserPassword='password',
        AllocatedStorage=64,
        PubliclyAccessible=True)['DBInstance']

    # Get credentials
    while response['DBInstanceStatus'] == 'creating':
        time.sleep(5)
        response = client.describe_db_instances(
            DBInstanceIdentifier=unique
        )['DBInstances'][0]

    credentials = {
        'MYSQL_DBNAME': unique,
        'MYSQL_HOST': response['Endpoint']['Address'],
        'MYSQL_USER': 'root',
        'MYSQL_PASS': 'password'}

    return credentials


def destroy(name):
    """Destroy a MySQL database on AWS"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Connect to AWS RDS
    client = connect()

    # Delete database
    client.delete_db_instance(
        DBInstanceIdentifier=unique,
        SkipFinalSnapshot=True,
        DeleteAutomatedBackups=True)


###############################################################################
# Utilities
###############################################################################


def connect():
    """Connect to AWS"""
    # Load API keys into environment variables
    reseval.load.api_keys()

    # Add credentials and connect
    return boto3.Session(
        aws_access_key_id=os.environ['AWSAccessKeyId'],
        aws_secret_access_key=os.environ['AWSSecretKey']
    ).client('rds', region_name='us-east-1')
