import dotenv

import reseval


###############################################################################
# Credential management
###############################################################################


def credentials(
    aws_api_key=None,
    aws_api_secret_key=None,
    heroku_api_key=None,
    mysql_local_user=None,
    mysql_local_password=None):
    """Add or update credentials"""
    # Update credentials for local development
    local_credentials(mysql_local_user, mysql_local_password)

    # Update API keys for remote development
    remote_credentials(aws_api_key, aws_api_secret_key, heroku_api_key)


###############################################################################
# Utilities
###############################################################################


def local_credentials(mysql_local_user=None, mysql_local_password=None):
    """Update database credentials for local development"""
    try:

        # Load existing credentials
        creds = dotenv.dotenv_values(reseval.ENVIRONMENT_FILE)

    except FileNotFoundError:

        # No credentials found
        creds = {}

    # Local development assumes localhost
    creds['MYSQL_HOST'] = 'localhost'

    # Update credentials
    if mysql_local_user is not None:
        creds['MYSQL_USER'] = mysql_local_user
    if mysql_local_password is not None:
        creds['MYSQL_PASS'] = mysql_local_password

    # Write to environment file
    reseval.ENVIRONMENT_FILE.parent.mkdir(exist_ok=True, parents=True)
    with open(reseval.ENVIRONMENT_FILE, 'w') as file:
        for key, value in creds.items():
            file.write(f'{key}={value}\n')


def remote_credentials(
    aws_api_key=None,
    aws_api_secret_key=None,
    heroku_api_key=None):
    """Update API keys for remote development"""
    if reseval.KEYS_FILE.exists():

        # Load existing credentials
        with open(reseval.KEYS_FILE) as file:
            lines = [line.rstrip() for line in file]
        keys = dict([line.split('=') for line in lines])

    else:

        # No credentials found
        keys = {}

    # Add credentials
    if aws_api_key is not None:
        keys['AWSAccessKeyId'] = aws_api_key
    if aws_api_secret_key is not None:
        keys['AWSSecretKey'] = aws_api_secret_key
    if heroku_api_key is not None:
        keys['HerokuAccessKey'] = heroku_api_key

    # Save credentials
    with open(reseval.KEYS_FILE, 'w') as file:
        for key, value in keys.items():
            file.write(f'{key}={value}\n')
