import json
import os

import boto3

import reseval


###############################################################################
# Constants
###############################################################################


# Cross-origin resource sharing
CORS = [
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": [],
        "MaxAgeSeconds": 3600
    }
]

# Public read policy
POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicRead",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject",
                "s3:GetObjectVersion"
            ],
            "Resource": "arn:aws:s3:::{}/*"
        }
    ]
}


###############################################################################
# AWS S3 file storage
###############################################################################


def create(config, directory):
    """Create an AWS S3 bucket for file storage"""
    name = config['name']

    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique' )['unique']

    # Connect to S3
    client = connect()

    # Create bucket
    client.create_bucket(Bucket=unique, ObjectOwnership='ObjectWriter')

    # Set bucket policy to public read-only
    client.put_public_access_block(
        Bucket=unique,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': False,
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        })
    client.put_bucket_acl(ACL='public-read', Bucket=unique)

    # Set bucket CORS to allow reads
    client.put_bucket_cors(
        Bucket=unique,
        CORSConfiguration={'CORSRules': CORS})

    # Set bucket policy to allow reads
    policy = POLICY.copy()
    policy['Statement'][0]['Resource'] = \
        policy['Statement'][0]['Resource'].format(unique)
    client.put_bucket_policy(Bucket=unique, Policy=json.dumps(policy))

    # Update client json
    with open(reseval.CLIENT_CONFIGURATION_FILE) as file:
        config = json.load(file)
    with open(reseval.CLIENT_CONFIGURATION_FILE, 'w') as file:
        json.dump(config | {'bucket': unique}, file, indent=4)

    # Upload evaluation files
    upload(name, directory)

    # Maybe upload listening test files
    if 'listening_test' in config:
        directory = reseval.LISTENING_TEST_DIRECTORY
        files = [item for item in directory.rglob('*') if not item.is_dir()]
        for file in files:
            destination = str('listening_test/' + file.name).replace('\\', '/')
            client.upload_file(
                str(file).replace('\\', '/'),
                unique,
                destination)


def destroy(name):
    """Delete an AWS S3 bucket"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Load API keys as environment variables
    reseval.load.api_keys()

    # Connect to AWS
    bucket = boto3.Session(
        aws_access_key_id=os.environ['AWSAccessKeyId'],
        aws_secret_access_key=os.environ['AWSSecretKey']
    ).resource('s3').Bucket(unique)

    try:

        # Delete contents
        bucket.objects.all().delete()

        # Delete bucket
        bucket.delete()

    except Exception:

        # Bucket has already been deleted
        pass

    (
        reseval.EVALUATION_DIRECTORY /
        name /
        'credentials' /
        'storage.json'
    ).unlink(missing_ok=True)


def upload(name, file_or_directory):
    """Upload directory to AWS S3 bucket"""
    # Get bucket name
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Connect to S3
    client = connect()

    # Upload directory
    if file_or_directory.is_dir():
        directory = file_or_directory
        files = [item for item in directory.rglob('*') if not item.is_dir()]
        for file in files:
            destination = str(file.relative_to(directory)).replace('\\', '/')
            client.upload_file(
                str(file).replace('\\', '/'),
                unique,
                destination)

    else:

        # Upload file
        file = file_or_directory
        destination = file.name
        client.upload_file(str(file), unique, file.name)

    # Return URL
    return f'https://{unique}.s3.amazonaws.com/{destination}'


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
    ).client('s3')
