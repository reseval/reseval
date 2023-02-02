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

    # Create unique name for bucket
    bucket = reseval.random.string(24)

    # Create bucket
    client.create_bucket(Bucket=bucket)

    # Load read-only policy as JSON string
    with open(reseval.ASSETS_DIR / 'policy.json') as file:
        policy = json.load(file)
        policy['Statement'][0]['Resource'][0] = \
            policy['Statement'][0]['Resource'][0].format(bucket)
        policy = json.dumps(policy)

    # Set bucket policy to public read-only
    client.put_bucket_policy(Bucket=bucket, Policy=policy)

    # Load CORS policy as JSON
    with open(reseval.ASSETS_DIR / 'cors.json') as file:
        cors = {'CORSRules': json.load(file)}

    # Set bucket CORS to allow reads
    client.put_bucket_cors(Bucket=bucket, CORSConfiguration=cors)

    # Save bucket name as storage credential
    credentials_file = (
        reseval.EVALUATION_DIRECTORY /
        name /
        'credentials' /
        'storage.json')
    credentials_file.parent.mkdir(exist_ok=True, parents=True)
    with open(credentials_file, 'w') as file:
        json.dump({'bucket': bucket}, file)

    # Update client json
    with open(reseval.CLIENT_CONFIGURATION_FILE) as file:
        config = json.load(file)
    with open(reseval.CLIENT_CONFIGURATION_FILE, 'w') as file:
        json.dump(config | {'bucket': bucket}, file, indent=4)

    # Upload evaluation files
    upload(name, directory)

    # Maybe upload listening test files
    if 'listening_test' in config:
        bucket = reseval.load.credentials_by_name(name, 'storage')['bucket']
        directory = reseval.LISTENING_TEST_DIRECTORY
        files = [item for item in directory.rglob('*') if not item.is_dir()]
        for file in files:
            destination = str('listening_test/' + file.name).replace('\\', '/')
            client.upload_file(
                str(file).replace('\\', '/'),
                bucket,
                destination)


def destroy(name):
    """Delete an AWS S3 bucket"""
    # Load API keys as environment variables
    reseval.load.api_keys()

    # Get bucket to delete
    try:
        bucket_name = \
            reseval.load.credentials_by_name(name, 'storage')['bucket']
    except FileNotFoundError:
        return

    # Connect to AWS
    bucket = boto3.Session(
        aws_access_key_id=os.environ['AWSAccessKeyId'],
        aws_secret_access_key=os.environ['AWSSecretKey']
    ).resource('s3').Bucket(bucket_name)

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
    bucket = reseval.load.credentials_by_name(name, 'storage')['bucket']

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
                bucket,
                destination)

    else:

        # Upload file
        file = file_or_directory
        destination = file.name
        client.upload_file(str(file), bucket, file.name)

    # Return URL
    return f'https://{bucket}.s3.amazonaws.com/{destination}'


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
