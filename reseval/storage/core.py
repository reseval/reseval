import reseval


###############################################################################
# Evaluation file storage
###############################################################################


def create(config, directory, local=False):
    """Create file storage and upload files"""
    print('Creating storage...')

    # Make sure client public storage doesn't have old evaluation files
    reseval.storage.client.destroy(config)

    # Create and upload
    module(config, local).create(config, directory)


def destroy(name):
    """Destroy file storage"""
    local = reseval.is_local(name)
    config = reseval.load.config_by_name(name)
    module(config, local).destroy(config['name'])


def upload(name, file_or_directory):
    """Upload a file or directory to storage"""
    local = reseval.is_local(name)
    config = reseval.load.config_by_name(name)
    return module(config, local).upload(name, file_or_directory)


###############################################################################
# Utilities
###############################################################################


def module(config, local=False):
    """Get the storage module to use"""
    if local:
        return reseval.storage.client
    storage = config['storage']
    if storage == 'aws':
        return reseval.storage.aws
    raise ValueError(f'Storage method {storage} is not recognized')
