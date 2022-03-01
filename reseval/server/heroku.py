import http.client
import json
import os
import subprocess
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

    with reseval.chdir(reseval.CACHE / 'client'):
        subprocess.call('npm run build', shell=True)

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
        name = reseval.load.credentials_by_name(config['name'], 'app')['name']
        connection.request(
            'POST',
            f'/apps/{name}/builds',
            json.dumps(data),
            headers=headers)

        # Get response from server
        response = json.loads(connection.getresponse().read().decode())

        # if app doesn't exist, raise error
        if response['id'] == 'not_found':
            raise ValueError(f'app name: {config["name"]} does not exist')

    # Close the connection
    connection.close()

    # Wait until server is setup
    while status(config['name']) == 'pending':
        time.sleep(3)

    if status(config['name']) == 'failure':
        raise ValueError('Heroku server failed to start')

    # Return application URL
    return {'URL': f'http://{name}.herokuapp.com/'}


def status(name):
    """Get current build status. One of ['succeeded', 'failed', 'pending']"""
    # Connect to Heroku
    connection = http.client.HTTPSConnection('api.heroku.com')

    # Send request
    reseval.load.api_keys()
    headers = {
        'Accept': 'application/vnd.heroku+json; version=3',
        'Authorization': f'Bearer {os.environ["HerokuAccessKey"]}'}
    unique_name = reseval.load.credentials_by_name(name, 'app')['name']
    connection.request('GET', f'/apps/{unique_name}/builds', headers=headers)

    # Get response
    data = json.loads(connection.getresponse().read().decode())

    # Close connection
    connection.close()

    # Get most recent build status from response
    status = list(map(lambda x: x['status'], data))
    return status[-1]


def destroy(config, credentials):
    """Destroy a Heroku server"""
    reseval.app.heroku.destroy(config)
