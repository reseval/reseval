import subprocess
import json
import shutil

import reseval


###############################################################################
# Create a subjective evaluation
###############################################################################


def create(config, directory, local=False, production=False):
    """Setup a subjective evaluation"""
    # Copy client and server to cache
    for path in reseval.ASSETS_DIR.rglob('*'):
        if path.is_dir():
            continue
        destination = reseval.CACHE / path.relative_to(reseval.ASSETS_DIR)
        destination.parent.mkdir(exist_ok=True, parents=True)
        shutil.copy(path, destination)

    # Maybe install server
    if local and not (reseval.CACHE / 'node_modules').exists():
        with reseval.chdir(reseval.CACHE):
            subprocess.call('npm install', shell=True)

    # Maybe install client
    client_directory = reseval.CACHE / 'client'
    if local and not (client_directory / 'node_modules').exists():
        with reseval.chdir(client_directory):
            subprocess.call('npm install', shell=True)

    if local and production:
        raise ValueError('Cannot deploy production build locally')

    # Load configuration file
    cfg = reseval.load.config_from_file(config)
    name = cfg['name']

    try:
        if local:

            # Get number of participants from database
            reseval.database.download(
                name,
                reseval.EVALUATION_DIRECTORY / name / 'tables',
                ['participants'])
            participants = len(reseval.load.participants(name))

        else:

            # Get number of participants from crowdsource platform
            participants = reseval.crowdsource.progress(name)

        # Don't create subjective evaluation that has already finished
        if participants >= cfg['participants']:
            raise ValueError(
                f'Not creating subjective evaluation {name}, which has already '
                 'finished. If you want to extend an evaluation, use '
                 'reseval.extend.')

    except FileNotFoundError:
        pass

    # Don't overwrite production data
    if not production:
        prod_file = reseval.EVALUATION_DIRECTORY / name / '.prod'
        if prod_file.exists():
            raise ValueError(
                f'Not overwriting results of evaluation {name}',
                 'which has been run in production')

    # Save configuration as json for the frontend to access
    with open(reseval.CLIENT_CONFIGURATION_FILE, 'w') as file:
        json.dump(cfg | {'local': local}, file, indent=4)

    # Create test
    test = reseval.test.get(cfg)(cfg, directory)

    # Create and save assignments
    with open(reseval.CLIENT_ASSIGNMENT_FILE, 'w') as file:
        json.dump(test.assign(cfg['random_seed']), file, indent=4)

    # Copy configuration file
    file = reseval.EVALUATION_DIRECTORY / name / 'config.yaml'
    file.parent.mkdir(exist_ok=True, parents=True)
    try:
        shutil.copyfile(config, file)
    except shutil.SameFileError:
        pass

    # Indicate if we're running local development
    local_file = reseval.EVALUATION_DIRECTORY / name / '.local'
    if local:
        local_file.touch()
    elif local_file.exists():
        local_file.unlink()

    # Create file storage and upload
    credentials_directory = reseval.EVALUATION_DIRECTORY / name / 'credentials'
    if not (credentials_directory / 'storage.json').exists():
        reseval.storage.create(cfg, directory, local)

    # If heroku is used for either the database or server, setup the app here
    if (not local and
        (cfg['server'] == 'heroku' or cfg['database'] == 'heroku')):
        reseval.server.heroku.create_app(cfg['name'])

    # Maybe create database
    if not (credentials_directory / 'storage.json').exists():

        try:

            # Create database
            reseval.database.create(cfg, test, local)

        except (Exception, KeyboardInterrupt) as exception:

            # Cleanup resources
            reseval.destroy(name, True)

            raise exception

    # Maybe create server
    if local or not (credentials_directory / 'server.json').exists():

        try:

            # Create server
            url = reseval.server.create(cfg, local)

        except (Exception, KeyboardInterrupt) as exception:

            # Cleanup resources
            reseval.destroy(name, True)

            raise exception
    else:

        # Retrieve URL of existing server
        credentials = reseval.load.credentials_by_name(name, 'server')
        url = credentials['URL']

    try:

        # Launch crowdsourced evaluation
        if (credentials_directory / 'crowdsource.json').exists():
            reseval.crowdsource.resume(name)
        else:
            reseval.crowdsource.create(cfg, production, url, local)

    except (Exception, KeyboardInterrupt) as exception:

        # Cleanup resources
        reseval.destroy(name, True)

        raise exception

    # Indicate that the evaluation has been run in production
    if production:
        prod_file = reseval.EVALUATION_DIRECTORY / name / '.prod'
        with open(prod_file, 'w') as file:
            pass

    # Return the evaluation name for, e.g., monitoring and analysis
    return name
