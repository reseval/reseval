import os

import heroku3


def configure(name, key, value):
    """Add an environment variable to a Heroku application"""
    # Get Heroku application
    app = list()[name]

    # Set environment variable
    app.config()[key] = value


def connect():
    """Connect to Heroku"""
    return heroku3.from_key(os.environ['HerokuAccessKey'])


def create(config):
    """Create a Heroku web application"""
    # TODO - name must be globally unique. Create credentials management for app.
    connect().create_app(name=config['name'])


def destroy(config):
    """Destroy a Heroku app"""
    try:

        # Destroy app
        list()[config['name']].delete()

    except KeyError:

        # Handle app not existing
        pass


def list():
    """List the applications currently active on Heroku"""
    return connect().apps()
