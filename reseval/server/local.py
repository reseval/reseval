import contextlib
import http.client
import os
import time

import psutil
import subprocess
import webbrowser

from pathlib import Path

import requests
from requests.adapters import HTTPAdapter, Retry

import reseval


###############################################################################
# Local server management
###############################################################################


def create(config):
    """Deploy a local server"""
    # Launch server process
    with chdir(reseval.ASSETS_DIR):
        # shell=True is not considered best practice for two reasons:
        #   1) It assumes the binary is the program you expect it to be. In
        #      this case, npm.
        #   2) If parameterized, it can run malicious code. For example,
        #      f'npm run {user_input}' where user_input = 'bad_arg; rm -rf /'.
        # In our use case, we've asked users to install npm and we do not
        # parameterize the command.
        process = subprocess.Popen('npm run dev', shell=True)

    # Ping server until we get a response
    session = requests.Session()
    retries = Retry(total=9,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.get(reseval.LOCALHOST_URL)

    # Open web browser to evaluation
    webbrowser.open(reseval.LOCALHOST_URL)

    # Return localhost URL and process ID
    return {'URL': reseval.LOCALHOST_URL, 'PID': process.pid}


def destroy(config, credentials):
    """Shutdown a local server"""
    parent = psutil.Process(credentials['PID'])
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()


###############################################################################
# Utilities
###############################################################################


@contextlib.contextmanager
def chdir(directory):
    """Change working directory"""
    curr_dir = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(curr_dir)
