import json
import os
import shutil
import tempfile
import time
from pathlib import Path

import boto3

import reseval


###############################################################################
# AWS server management
###############################################################################


def create(name, detach=True):
    """Create an AWS server"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Copy client and server to cache
    for path in reseval.ASSETS_DIR.rglob('*'):
        if path.is_dir():
            continue
        destination = reseval.CACHE / path.relative_to(reseval.ASSETS_DIR)
        destination.parent.mkdir(exist_ok=True, parents=True)
        shutil.copy(path, destination)

    # Install npm dependencies to build client
    client_directory = reseval.CACHE / 'client'
    client_directory.mkdir(exist_ok=True, parents=True)
    if not (client_directory / 'node_modules').exists():
        with reseval.chdir(client_directory):
            reseval.npm.install().wait()

    # Build client
    with reseval.chdir(reseval.CACHE / 'client'):
        reseval.npm.build().wait()

    # Connect to AWS
    client = connect()

    # Create server bundle
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        root = directory / 'reseval'
        root.mkdir()
        paths = [
            'client/build',
            'server',
            'package-lock.json',
            'package.json',
            'Procfile',
            'server.ts',
            'tsconfig.json']
        for path in paths:
            try:
                shutil.copytree(reseval.CACHE / path, root / path)
            except NotADirectoryError:
                shutil.copy(reseval.CACHE / path, root / path)

        # Zip
        shutil.make_archive(directory / 'reseval', 'zip', root)

        # Upload tarball
        reseval.storage.aws.upload(name, directory / 'reseval.zip')

        # Wait for upload to complete
        reseval.storage.aws.connect().get_waiter('object_exists').wait(
            Bucket=unique,
            Key='reseval.zip',
            WaiterConfig={'Delay': 2, 'MaxAttempts': 5})

        # Update application
        response = client.create_application_version(
            ApplicationName=unique,
            VersionLabel='Sample',
            SourceBundle={
                'S3Bucket': unique,
                'S3Key': 'reseval.zip'
            },
            AutoCreateApplication=True,
            Process=True)

        # Wait for build to finish
        response = client.describe_application_versions(
            ApplicationName=unique,
            VersionLabels=['Sample']
        )['ApplicationVersions'][0]
        while response['Status'].lower() in ['building', 'processing', 'unprocessed']:
            time.sleep(5)
            response = client.describe_application_versions(
                ApplicationName=unique,
                VersionLabels=['Sample']
            )['ApplicationVersions'][0]

    # Create elastic beanstalk environment
    client.create_environment(
        ApplicationName=unique,
        EnvironmentName=unique,
        SolutionStackName='64bit Amazon Linux 2 v5.8.3 running Node.js 18',
        OptionSettings=[{
            'Namespace': 'aws:autoscaling:launchconfiguration',
            'OptionName': 'IamInstanceProfile',
            'Value': 'aws-elasticbeanstalk-ec2-role'
        }])

    # Wait for environment build to finish
    response = client.describe_environments(
        ApplicationName=unique,
        EnvironmentNames=[unique])['Environments'][0]
    while response['Status'].lower() != 'ready':
        time.sleep(3)
        response = client.describe_environments(
            ApplicationName=unique,
            EnvironmentNames=[unique])['Environments'][0]

    # Process and deploy
    response = client.update_environment(
        ApplicationName=unique,
        EnvironmentName=unique,
        VersionLabel='Sample')

    # Wait for environment update to finish
    response = client.describe_environments(
        ApplicationName=unique,
        EnvironmentNames=[unique])['Environments'][0]
    while response['Status'].lower() != 'ready':
        time.sleep(3)
        response = client.describe_environments(
            ApplicationName=unique,
            EnvironmentNames=[unique])['Environments'][0]

    # Return application URL
    return {'URL': f'http://{response["CNAME"]}'}


def destroy(name, credentials):
    """Destroy an AWS server"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Connect to AWS
    client = connect()

    # Get S3 bucket name
    arn = client.describe_application_versions(
            ApplicationName=unique,
            VersionLabels=['Sample']
        )['ApplicationVersions'][0]['ApplicationVersionArn']
    bucket = f'elasticbeanstalk-{arn.split(":")[3]}-{arn.split(":")[4]}'

    # Delete environment
    client.terminate_environment(
        EnvironmentName=unique,
        TerminateResources=True,
        ForceTerminate=True)

    # Delete application
    client.delete_application(ApplicationName=unique)

    # Connect to S3
    client = reseval.storage.aws.connect()

    try:

        # Get current bucket policy
        policy = json.loads(client.get_bucket_policy(Bucket=bucket)['Policy'])

        # Update bucket policy to allow deletion
        policy['Statement'] = [
            s for s in policy['Statement']
            if not (s['Action'] == 's3:DeleteBucket' and s['Effect'].lower() == 'deny')]
        client.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))

        # Connect to S3 bucket
        bucket = boto3.Session(
            aws_access_key_id=os.environ['AWSAccessKeyId'],
            aws_secret_access_key=os.environ['AWSSecretKey']
        ).resource('s3').Bucket(bucket)

        # Delete contents
        bucket.objects.all().delete()

        # Delete bucket
        bucket.delete()

    except Exception:

        # Bucket was already deleted when environment was deleted
        pass


###############################################################################
# Utilities
###############################################################################


def configure(name, configuration):
    """Add configuration variables to server"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Connect to AWS
    client = connect()

    # Update environment variables
    client.update_environment(
        ApplicationName=unique,
        EnvironmentName=unique,
        OptionSettings=[{
                'Namespace': 'aws:elasticbeanstalk:application:environment',
                'OptionName': key,
                'Value': value
            } for key, value in configuration.items()])

    # Wait for environment update to finish
    response = client.describe_environments(
        ApplicationName=unique,
        EnvironmentNames=[unique])['Environments'][0]
    while response['Status'].lower() != 'ready':
        time.sleep(3)
        response = client.describe_environments(
            ApplicationName=unique,
            EnvironmentNames=[unique])['Environments'][0]


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
