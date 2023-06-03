import json
import psutil
import webbrowser

import requests
from requests.adapters import HTTPAdapter, Retry

import reseval


###############################################################################
# Local server management
###############################################################################


def create(name, detach=False):
    """Deploy a local server"""
    # Maybe install server
    if not (reseval.CACHE / 'node_modules').exists():
        with reseval.chdir(reseval.CACHE):
            reseval.npm.install().wait()

    # Maybe install client
    client_directory = reseval.CACHE / 'client'
    if not (client_directory / 'node_modules').exists():
        with reseval.chdir(client_directory):
            reseval.npm.install().wait()

    # Launch server process
    with reseval.chdir(reseval.CACHE):
        process = reseval.npm.start()

    # Ping server until we get a response
    session = requests.Session()
    retries = Retry(total=11,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.get(reseval.LOCALHOST_URL)

    # Open web browser to evaluation
    webbrowser.open(reseval.LOCALHOST_URL)

    # Save server credentials
    credentials = {'URL': reseval.LOCALHOST_URL, 'PID': process.pid}
    file = (
        reseval.EVALUATION_DIRECTORY /
        name /
        'credentials' /
        'server.json')
    file.parent.mkdir(exist_ok=True, parents=True)
    with open(file, 'w') as file:
        json.dump(credentials, file, indent=4, sort_keys=True)

    # Maybe wait for process to finish
    if not detach:
        process.wait()

    return credentials


def destroy(name, credentials):
    """Shutdown a local server"""
    try:
        parent = psutil.Process(credentials['PID'])
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass
