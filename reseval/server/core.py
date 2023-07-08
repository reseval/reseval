import json

import reseval


###############################################################################
# Server management
###############################################################################


def create(config, local=False, detach=False):
    """Create a server"""
    print('Creating server...')

    # Create server
    name = config['name']
    credentials = module(config, local).create(name, detach=detach)

    # Save server credentials
    file = reseval.EVALUATION_DIRECTORY / name / 'credentials' / 'server.json'
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

    try:

        # Load credentials
        credentials = reseval.load.credentials_by_name(name, 'server')

    except FileNotFoundError:

        # We assume the server does not exist if we don't have credentials
        return

    # Destroy server
    module(config, local).destroy(name, credentials)

    # Cleanup credentials
    (
        reseval.EVALUATION_DIRECTORY /
        name /
        'credentials' /
        'server.json'
    ).unlink(missing_ok=True)


###############################################################################
# Utilities
###############################################################################


def module(config, local=False):
    """Get the crowdsourcing module to use"""
    if local:
        return reseval.server.local
    server = config['server']
    if server == 'aws':
        return reseval.server.aws
    if server == 'heroku':
        return reseval.server.heroku
    raise ValueError(f'Server hosting service {server} not recognized')
