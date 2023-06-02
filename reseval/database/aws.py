import os
import re

import boto3

import reseval


###############################################################################
# AWS RDS database management
###############################################################################


def create(config):
    """Create a MySQL database on AWS"""
    # Connect to AWS RDS
    client = connect()

    # Remove non-alphanumeric
    pattern = re.compile('[\W_]+')
    name = pattern.sub('', config['name'])

    # TODO - create a unique name to avoid "already exists" during long
    #        deletion process

    # Create database
    response = client.create_db_instance(
        DBName=name,
        DBInstanceIdentifier=config['name'],
        DBInstanceClass='db.t2.micro',
        Engine='mysql',
        MasterUsername='root',
        MasterUserPassword='password',
        AllocatedStorage=64)['DBInstance']
    print(response)
    import pdb; pdb.set_trace()

    # Get credentials
    credentials = {
        'MYSQL_DBNAME': config['name'],
        'MYSQL_HOST': response['Endpoint']['Address'],
        'MYSQL_USER': 'root',
        'MYSQL_PASS': 'password'}

    return credentials


def destroy(config):
    """Destroy a MySQL database on AWS"""
    # Connect to AWS RDS
    client = connect()

    # Delete database
    client.delete_db_instance(
        DBInstanceIdentifier=config['name'],
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
    ).client('rds', region_name='us-east-2')
