import boto3


###############################################################################
# Constants
###############################################################################


# Public read-only policy for AWS S3 bucket
BUCKET_POLICY = '{' \
    '"Id":"Policy1644520445235",' \
    '"Version":"2012-10-17",' \
    '"Statement":[{' \
        '"Sid":"Stmt1644520441991",' \
        '"Action":["s3:GetObject"],' \
        '"Effect":"Allow",' \
        '"Resource":"arn:aws:s3:::{}/*",' \
        '"Principal":"*"' \
    '}]' \
'}'


###############################################################################
# AWS S3 file storage
###############################################################################


def create(config, directory):
    """Create an AWS S3 bucket for file storage"""
    name = config['name']

    # Connect to S3
    client = boto3.client('s3')

    # Create bucket
    client.create_bucket(Bucket=name)

    # Set bucket policy to public read-only
    client.put_bucket_policy(Bucket=name, Policy=BUCKET_POLICY.format(name))

    # Upload files
    upload(name, directory)


def destroy(name):
    """Delete an AWS S3 bucket"""
    # Connect to S3
    client = boto3.resource('s3')

    # Get bucket to delete
    bucket = client.Bucket(name)

    # Delete contents
    bucket.objects.all().delete()

    # Delte bucket
    bucket.delete()


def upload(name, file_or_directory):
    """Upload directory to AWS S3 bucket"""
    # Connect to S3
    client = boto3.client('s3')

    # Upload directory
    if file_or_directory.is_dir():
        directory = file_or_directory
        for file in [item for item in directory.rglob('*') if item.is_dir()]:
            client.upload_file(file, name, file.relative_to(directory))

    # Upload file
    else:
        client.upload_file(str(file_or_directory), name, '')

    # Return URL
    return (
        f'http://{name}.s3-website-us-east-1.amazonaws.com/' +
        file_or_directory)
