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


def create(config):
    """Create a Heroku server"""
    # Connect to Heroku
    connection = http.client.HTTPSConnection('api.heroku.com')

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
        tarball_url = reseval.storage.upload(config['name'], tarball)

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
            f'/apps/{config["name"]}/builds',
            json.dumps(data),
            headers=headers)

        # Get response from server
        response = connection.getresponse()

        # if app doesn't exist, raise error
        if json.loads(response.read().decode())['id'] == 'not_found':
            raise ValueError(f'app name: {config["name"]} does not exist')

    # Wait until server is setup
    # TODO - Should we use retries here as well?
    while status(config['name']) == 'pending':
        time.sleep(5)

    if status(config['name']) == 'failure':
        raise ValueError('Heroku server failed to start')

    # TODO - return credentials (just the URL)
    return {'URL': ''}


def status(name):
    """Get current build status. One of ['succeeded', 'failed', 'pending']"""
    # Connect to Heroku
    connection = http.client.HTTPSConnection('api.heroku.com')

    # Send request
    headers = {
        'Accept': 'application/vnd.heroku+json; version=3',
        'Authorization': f'Bearer {os.environ["HerokuAccessKey"]}'}
    connection.request('GET', f'/apps/{name}/builds', headers=headers)

    # Get response
    data = json.loads(connection.getresponse().read().decode())

    # Get most recent build status from response
    status = list(map(lambda x: x['status'], data))
    return status[-1]


def destroy(config, credentials):
    """Destroy a Heroku server"""
    reseval.app.heroku.destroy(config)
