import re

import reseval


###############################################################################
# Heroku ClearDB database management
###############################################################################


def create(config):
    """Create a MySQL database on Heroku"""
    # Get the heroku application
    app = reseval.app.heroku.list()[config['name']]

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
    reseval.app.heroku.destroy(config)
