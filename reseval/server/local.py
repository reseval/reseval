import json
import psutil
import subprocess
import webbrowser

import requests
from requests.adapters import HTTPAdapter, Retry

import reseval


###############################################################################
# Local server management
###############################################################################


def create(config, detach=False):
    """Deploy a local server"""
    # Launch server process
    with reseval.chdir(reseval.CACHE):
        # shell=True is not considered best practice for two reasons:
        #   1) It assumes the binary is the program you expect it to be. In
        #      this case, npm.
        #   2) If parameterized, it can run malicious code. For example,
        #      f'npm run {user_input}' where
        #      user_input = 'nonexistant_arg; rm -rf /'.
        # In our use case, we've asked users to install npm and we do not
        # parameterize the command. The alternative is to set shell=False and
        # require the user to provide the path to the npm executable.
        process = subprocess.Popen('npm run dev', shell=True)

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
        config['name'] /
        'credentials' /
        'server.json')
    file.parent.mkdir(exist_ok=True, parents=True)
    with open(file, 'w') as file:
        json.dump(credentials, file, indent=4, sort_keys=True)

    # Maybe wait for process to finish
    if detach:
        process.wait()

    return credentials


def destroy(config, credentials):
    """Shutdown a local server"""
    try:
        parent = psutil.Process(credentials['PID'])
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass
