import os

import heroku3

import reseval


def configure(name, key, value):
    """Add an environment variable to a Heroku application"""
    # Get Heroku application
    app = get(name)

    # Set environment variable
    app.config()[key] = value


def connect():
    """Connect to Heroku"""
    reseval.load.api_keys()
    return heroku3.from_key(os.environ['HerokuAccessKey'])


def create(name):
    """Create a Heroku web application"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Create Heroku app
    connect().create_app(name=unique)


def destroy(name):
    """Destroy a Heroku app"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    try:

        # Destroy app
        get(unique).delete()

    except (FileNotFoundError, KeyError):

        # Handle app not existing
        pass

    # Delete credentials file
    (
        reseval.EVALUATION_DIRECTORY /
        name /
        'credentials' /
        'app.json'
    ).unlink(missing_ok=True)


def get(name):
    """Retrieve a Heroku application"""
    # Load application credentials
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Get Heroku application
    return connect().apps()[unique]
