import json

import reseval


###############################################################################
# Server management
###############################################################################


def create(config, local=False):
    """Create a server"""
    # Create server
    credentials = module(config, local).create(config)

    # Save server credentials
    file = (
        reseval.EVALUATION_DIRECTORY /
        config['name'] /
        'credentials' /
        'server.json')
    file.parent.mkdir(exist_ok=True, parents=True)
    with open(file, 'w') as file:
        json.dump(credentials, file, indent=4, sort_keys=True)

    # Return the application URL
    return credentials['URL']


def destroy(name):
    """Destroy a server"""
    local = reseval.is_local(name)

    # Load config
    config = reseval.load.config_by_name(name)

    # Load credentials
    credentials = reseval.load.credentials_by_name(name, 'server')

    # Destroy server
    module(config, local).destroy(config, credentials)

    # Cleanup credentials
    (reseval.EVALUATION_DIRECTORY / name / 'credentials' / 'server.json').unlink()


def status(name):
    """Get the status of the server"""
    local = reseval.is_local(name)
    config = reseval.load.config_by_name(name)
    credentials = reseval.load.credentials_by_name(name, 'server')
    module(config, local).status(config, credentials)


###############################################################################
# Utilities
###############################################################################


def module(config, local=False):
    """Get the crowdsourcing module to use"""
    if local:
        return reseval.server.local
    server = config['server']
    if server == 'heroku':
        return reseval.server.heroku
    raise ValueError(f'Server hosting service {server} not recognized')
