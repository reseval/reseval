import re

import reseval


###############################################################################
# Heroku ClearDB database management
###############################################################################


def create(name):
    """Create a MySQL database on Heroku"""
    # Get the heroku application
    app = reseval.app.heroku.get(name)

    # Add the ClearDB MySQL database add-on
    app.install_addon(plan_id_or_name='cleardb:ignite', config={})

    # Retrieve the ClearDB URL
    url = app.config()['CLEARDB_DATABASE_URL']

    # Parse URL to obtain credentials
    user, password, host, unique = re.split('[/@?:]', url[8:])[:4]
    credentials = {
        'MYSQL_DBNAME': unique,
        'MYSQL_HOST': host,
        'MYSQL_USER': user,
        'MYSQL_PASS': password}

    return credentials


def destroy(name):
    """Destroy a MySQL database on Heroku"""
    reseval.app.heroku.destroy(name)
