import http.client
import json
import os
import tarfile
import tempfile
import time
from pathlib import Path

import reseval


###############################################################################
# Heroku server management
###############################################################################


def create(name, detach=True):
    """Create a Heroku server"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Connect to Heroku
    connection = http.client.HTTPSConnection('api.heroku.com')

    # Maybe install client
    client_directory = reseval.CACHE / 'client'
    if not (client_directory / 'node_modules').exists():
        with reseval.chdir(client_directory):
            reseval.npm.install().wait()

    # Build client
    with reseval.chdir(reseval.CACHE / 'client'):
        reseval.npm.build().wait()

    # Create a tarball of all files needed by the Heroku server
    with tempfile.TemporaryDirectory() as directory:
        tarball = Path(directory) / 'reseval.tar.gz'
        files = [
            'client/build',
            'server',
            'package-lock.json',
            'package.json',
            'Procfile',
            'server.ts',
            'tsconfig.json']
        with tarfile.open(tarball, 'w:gz') as tar:
            for file in files:
                tar.add(reseval.CACHE / file)

        # Upload tarball and get a URL
        tarball_url = reseval.storage.upload(name, tarball)

        # Server configuration
        data = {
            'source_blob': {'url': tarball_url},
            'buildpacks': [{
                'url': 'https://github.com/heroku/heroku-buildpack-nodejs',
                'name': 'heroku/nodejs'}]}
        headers = {
            'Accept': 'application/vnd.heroku+json; version=3',
            'Authorization': f'Bearer {os.environ["HerokuAccessKey"]}'}

        # Create server
        connection.request(
            'POST',
            f'/apps/{unique}/builds',
            json.dumps(data),
            headers=headers)

        # Get response from server
        response = json.loads(connection.getresponse().read().decode())

        # if app doesn't exist, raise error
        if response['id'] == 'not_found':
            raise ValueError(f'app name: {unique} does not exist')

    # Close the connection
    connection.close()

    # Wait until server is setup
    while status(name) == 'pending':
        time.sleep(3)

    if status(name) == 'failure':
        raise ValueError('Heroku server failed to start')

    # Return application URL
    return {'URL': f'http://{name}.herokuapp.com/'}


def destroy(name, credentials):
    """Destroy a Heroku server"""
    reseval.app.heroku.destroy(name)


###############################################################################
# Utilities
###############################################################################


def status(name):
    """Get current build status. One of ['succeeded', 'failed', 'pending']"""
    # Get unique identifier
    unique = reseval.load.credentials_by_name(name, 'unique')['unique']

    # Connect to Heroku
    connection = http.client.HTTPSConnection('api.heroku.com')

    # Send request
    reseval.load.api_keys()
    headers = {
        'Accept': 'application/vnd.heroku+json; version=3',
        'Authorization': f'Bearer {os.environ["HerokuAccessKey"]}'}
    connection.request('GET', f'/apps/{unique}/builds', headers=headers)

    # Get response
    data = json.loads(connection.getresponse().read().decode())

    # Close connection
    connection.close()

    # Get most recent build status from response
    status = list(map(lambda x: x['status'], data))
    return status[-1]
