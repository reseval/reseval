import json
import os
import string

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


def create(config):
    """Create a Heroku web application"""
    # Create a globally unique name to prevent collision
    name = (
        reseval.random.string(1, string.ascii_lowercase) +
        reseval.random.string(23))

    # Create Heroku app
    connect().create_app(name=name)

    # Save name as application credentials
    credentials_file = (
        reseval.EVALUATION_DIRECTORY /
        config['name'] /
        'credentials' /
        'app.json')
    credentials_file.parent.mkdir(exist_ok=True, parents=True)
    with open(credentials_file, 'w') as file:
        json.dump({'name': name}, file)


def destroy(config):
    """Destroy a Heroku app"""
    try:

        # Destroy app
        get(config['name']).delete()

    except (FileNotFoundError, KeyError):

        # Handle app not existing
        pass

    # Delete credentials file
    (
        reseval.EVALUATION_DIRECTORY /
        config['name'] /
        'credentials' /
        'app.json'
    ).unlink(missing_ok=True)


def get(name):
    """Retrieve a Heroku application"""
    # Load application credentials
    credentials = reseval.load.credentials_by_name(name, 'app')

    # Get Heroku application
    return connect().apps()[credentials['name']]
