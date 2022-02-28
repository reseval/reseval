import os
import re

import heroku3


###############################################################################
# Heroku ClearDB database management
###############################################################################


def create(config):
    """Create a MySQL database on Heroku"""
    # Get the heroku application
    app = list_apps()[config['name']]

    # Add the ClearDB MySQL database add-on
    app.install_addon(plan_id_or_name='cleardb:ignite', config={})

    # Retrieve the ClearDB URL
    url = app.config()['CLEARDB_DATABASE_URL']

    # Parse URL to obtain credentials
    user, password, host, name = re.split('[/@?:]', url[8:])[:4]

    # Return database credentials for new database
    return {
        'MYSQL_DBNAME': name,
        'MYSQL_HOST': host,
        'MYSQL_USER': user,
        'MYSQL_PASS': password}


def destroy(config, credentials):
    """Destroy a MySQL database on Heroku"""
    try:

        # Destroy app
        list_apps()[config['name']].delete()

    except KeyError:

        # Handle app not existing
        pass


###############################################################################
# Utilities
###############################################################################


def connect():
    """Connect to Heroku"""
    return heroku3.from_key(os.environ['HerokuAccessKey'])


def list_apps():
    """List the applications currently active on Heroku"""
    return connect().apps()
