import json
import os
import requests
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

    # Load API keys into environment variables
    reseval.load.api_keys()

    # Connect to EC2
    client = boto3.Session(
        aws_access_key_id=os.environ['AWSAccessKeyId'],
        aws_secret_access_key=os.environ['AWSSecretKey']
    ).client('ec2', region_name='us-east-1')

    # Get elastic beanstalk security groups
    security_groups = client.describe_security_groups(
        Filters=[
            {
                'Name': 'tag:elasticbeanstalk:environment-name',
                'Values': [unique]
            }
        ]
    )['SecurityGroups']
    group_ids = [group['GroupId'] for group in security_groups]

    # Add ingress rules for local IP and MySQL
    local_ip = json.loads(
        requests.get('https://api.seeip.org/jsonip?').text
    )['ip']
    for group_id in group_ids:
        client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'IpProtocol': '-1',
                    'IpRanges': [{'CidrIp': f'{local_ip}/32'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                    'FromPort': 3306,
                    'ToPort': 3306
                }
            ]
        )

    # Connect to AWS RDS
    client = connect()

    # Create database
    response = client.create_db_instance(
        DBName=unique,
        DBInstanceIdentifier=unique,
        DBInstanceClass='db.t2.micro',
        AllocatedStorage=64,
        Engine='mysql',
        MasterUsername='root',
        MasterUserPassword='password',
        VpcSecurityGroupIds=group_ids,
        PubliclyAccessible=True)['DBInstance']

    # Get credentials
    while response['DBInstanceStatus'] == 'creating':
        time.sleep(3)
        response = client.describe_db_instances(
            DBInstanceIdentifier=unique
        )['DBInstances'][0]
    credentials = {
        'MYSQL_DBNAME': unique,
        'MYSQL_HOST': response['Endpoint']['Address'],
        'MYSQL_USER': 'root',
        'MYSQL_PASS': 'password',
        'RDS_HOSTNAME': response['Endpoint']['Address'],
        'RDS_PORT': '3306',
        'RDS_DB_NAME': unique,
        'RDS_USERNAME': 'root',
        'RDS_PASSWORD': 'password'}

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
