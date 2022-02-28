import json
from msilib.schema import File

import reseval


###############################################################################
# Crowdsourcing interface
###############################################################################


def active(name):
    """Returns True if the evaluation is still running"""
    # Get config
    config = reseval.load.config_by_name(name)

    # Local dev is active until we have enough participants and responses
    if reseval.is_local(name):
        try:
            reseval.database.download(
                name,
                reseval.EVALUATION_DIRECTORY / name / 'tables',
                ['responses'])
            responses = reseval.load.responses(name)
            participants = len(set(
                response['Participant'] for response in responses))
            samples = \
                config['participants'] * config['samples_per_participant']
            return (
                len(responses) < samples or
                participants < config['participants'])
        except FileNotFoundError:
            return True

    # Get credentials
    try:
        credentials = reseval.load.credentials_by_name(name, 'crowdsource')
    except FileNotFoundError:
        return False

    # Check if the evaluation is active
    module(config).active(config, credentials)


def create(config, url, local=False, production=False):
    """Create a subjective evaluation"""
    # Skip if performing local development
    if local:
        return

    print('Creating crowdsource task...')

    # Create crowdsource task
    credentials = module(config).create(config, url, production)

    # Save crowdsource credentials
    file = (
        reseval.EVALUATION_DIRECTORY /
        config['name'] /
        'credentials' /
        'crowdsource.json')
    file.parent.mkdir(exist_ok=True, parents=True)
    with open(file, 'w') as file:
        json.dump(credentials, file, indent=4, sort_keys=True)


def destroy(name):
    """Delete a subjective evaluation"""
    # Skip if performing local development
    if reseval.is_local(name):
        return

    # Get config
    config = reseval.load.config_by_name(name)

    # Get credentials
    credentials = reseval.load.credentials_by_name(name, 'crowdsource')

    # Destroy crowdsource task
    module(config).destroy(credentials)


def extend(name, participants):
    """Extend a subjectve evaluation"""
    # Skip if performing local development
    if reseval.is_local(name):
        return

    # Get config
    config = reseval.load.config_by_name(name)

    # Get credentials
    credentials = reseval.load.credentials_by_name(name, 'crowdsource')

    # Extend task
    module(config).extend(credentials, participants,name)


def paid(name):
    """Check if all participants have been paid"""
    # Skip if performing local development
    if reseval.is_local(name):
        return True

    # Get config
    config = reseval.load.config_by_name(name)

    try:

        # Get credentials
        credentials = reseval.load.credentials_by_name(name, 'crowdsource')

    except FileNotFoundError:

        # We assume that the evaluation was never started or already finished
        # if we do not have the credentials
        return True

    # Check if participants have been paid
    module(config).paid(credentials)


def pay(name):
    """Pay participants"""
    # Skip if performing local development
    if reseval.is_local(name):
        return

    # Get config
    config = reseval.load.config_by_name(name)

    # Get credentials
    credentials = reseval.load.credentials_by_name(name, 'crowdsource')

    # Pay participants
    module(config).pay(config, credentials)


def progress(name):
    """Retrieve the number of participants who have taken the evaluation"""
    # Skip if performing local development
    if reseval.is_local(name):
        return

    # Get config
    config = reseval.load.config_by_name(name)

    # Get credentials
    credentials = reseval.load.credentials_by_name(name, 'crowdsource')

    # Check current progress
    return module(config).progress(credentials)


def resume(name):
    """Resume a production evaluation"""
    # Get config
    config = reseval.load.config_by_name(name)

    # Get credentials
    credentials = reseval.load.credentials_by_name(name, 'crowdsource')

    # Stop evaluation
    module(config).resume(config, credentials)


def stop(name):
    """Stop an active evaluation"""
    # Skip if performing local development
    if reseval.is_local(name):
        return

    # Get config
    config = reseval.load.config_by_name(name)

    # Get credentials
    credentials = reseval.load.credentials_by_name(name, 'crowdsource')

    # Stop evaluation
    module(config).stop(credentials)


###############################################################################
# Utilities
###############################################################################


def module(config):
    """Get the crowdsourcing module to use"""
    platform = config['crowdsource']['platform']
    if platform == 'mturk':
        return reseval.crowdsource.mturk
    raise ValueError(f'Crowdsource platform {platform} not recognized')
