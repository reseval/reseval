import json
import os

import boto3

import reseval


###############################################################################
# AWS S3 file storage
###############################################################################


def create(config, directory):
    """Create an AWS S3 bucket for file storage"""
    name = config['name']

    # Connect to S3
    client = connect()

    # Create bucket
    client.create_bucket(Bucket=name)

    # Load read-only policy as JSON string
    with open(reseval.ASSETS_DIR / 'policy.json') as file:
        policy = json.load(file)
        policy['Statement'][0]['Resource'][0] = \
            policy['Statement'][0]['Resource'][0].format(name)
        policy = json.dumps(policy)

    # Set bucket policy to public read-only
    client.put_bucket_policy(Bucket=name, Policy=policy)

    # Upload files
    upload(name, directory)


def destroy(name):
    """Delete an AWS S3 bucket"""
    # Connect to S3
    client = connect()

    # Get bucket to delete
    bucket = client.Bucket(name)

    # Delete contents
    bucket.objects.all().delete()

    # Delte bucket
    bucket.delete()


def upload(name, file_or_directory):
    """Upload directory to AWS S3 bucket"""
    # Connect to S3
    client = connect()

    # Upload directory
    if file_or_directory.is_dir():
        directory = file_or_directory
        for file in [item for item in directory.rglob('*') if not item.is_dir()]:
            client.upload_file(
                str(file).replace('\\', '/'),
                name,
                str(file.relative_to(directory)).replace('\\', '/'))

    # Upload file
    else:
        client.upload_file(str(file_or_directory), name, '')

    # Return URL
    return (
        f'http://{name}.s3-website-us-east-1.amazonaws.com/' +
        str(file_or_directory).replace('\\', '/'))


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
        aws_secret_access_key=os.environ['AWSSecretKey'],
    ).client('s3')
