import boto3

import reseval


###############################################################################
# AWS server management
###############################################################################


def create(config):
    """Create an AWS server"""
    # Connect to AWS
    client = boto3.client('elasticbeanstalk')

    # Load database credentials
    environment_file = (
        reseval.EVALUATION_DIRECTORY /
        config['name'] /
        'credentials' /
        '.env')
    with open(environment_file) as file:
        credentials = dict(
            line.strip().split('=') for line in file.readlines())

    # Create the Elastic Beanstalk environment
    response = client.create_environment(
        ApplicationName=config['name'],
        EnvironmentName=config['name'],
        SolutionStackName='64bit Amazon Linux 2023 v4.0.1 running Python 3.9',
        OptionSettings=[
            {
                'Namespace': 'aws:elasticbeanstalk:application:environment',
                'OptionName': key,
                'Value': value
            } for key, value in credentials.items()
        ])

    # Return application URL
    return {'URL': response['EndpointURL']}


def destroy(config, credentials):
    """Destroy an AWS server"""
    # Connect to AWS
    client = boto3.client('elasticbeanstalk')

    # Delete environment
    client.terminate_environment(
        EnvironmentName=config['name'],
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
    else:
        return 'failed'
