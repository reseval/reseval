import os

import boto3

import reseval


###############################################################################
# AWS server management
###############################################################################


def create(name, detach=True):
    """Create an AWS server"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Connect to AWS
    client = connect()
    import pdb; pdb.set_trace()

    # Load database credentials
    environment_file = (
        reseval.EVALUATION_DIRECTORY /
        name /
        'credentials' /
        '.env')
    with open(environment_file) as file:
        credentials = dict(
            line.strip().split('=') for line in file.readlines())

    # Create the Elastic Beanstalk environment
    response = client.create_environment(
        ApplicationName=unique,
        EnvironmentName=unique,
        SolutionStackName='64bit Amazon Linux 2 v5.8.2 running Node.js 18',
        OptionSettings=[
            {
                'Namespace': 'aws:elasticbeanstalk:application:environment',
                'OptionName': key,
                'Value': value
            } for key, value in credentials.items()
        ])

    # Return application URL
    return {'URL': response['EndpointURL']}


def destroy(name, credentials):
    """Destroy an AWS server"""
        # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Connect to AWS
    client = connect()

    # Delete environment
    client.terminate_environment(
        EnvironmentName=unique,
        TerminateResources=True,
        ForceTerminate=True)


###############################################################################
# Utilities
###############################################################################


def status(name):
    """Get current build status. One of ['succeeded', 'failed', 'pending']"""
    # Connect to AWS
    client = boto3.client('elasticbeanstalk')

    # Get environment info
    status = client.describe_environments(
        ApplicationName=name,
        EnvironmentNames=[name]
    )['Environments'][0]['Status']

    # Convert status descriptions to common format
    if status == 'Ready':
        return 'success'
    elif status == 'Launching':
        return 'pending'
    return 'failed'


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
    ).client('elasticbeanstalk', region_name='us-east-1')
