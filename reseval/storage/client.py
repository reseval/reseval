from genericpath import exists
import shutil, random, os
from pathlib import Path

import reseval


###############################################################################
# Client file storage management
###############################################################################


def create(config, directory):
    """Add evaluation files to client storage"""
    for path in directory.iterdir():
        upload(config['name'], path)

    # Add listening test files to client storage
    if 'if_listening_test' in config and config['if_listening_test']:
        upload(config['name'], Path('reseval/assets/listening_test_file'))


def destroy(config):
    """Remove all evaluation files in client public directory"""
    try:
        for path in reseval.CLIENT_PUBLIC_DIRECTORY.iterdir():
            if path.name != '.gitkeep':
                try:
                    shutil.rmtree(path)
                except NotADirectoryError:
                    path.unlink()
    except FileNotFoundError:
        pass


def upload(name, file_or_directory):
    """Upload a file or directory to client storage"""
    destination = reseval.CLIENT_PUBLIC_DIRECTORY / file_or_directory.name
    reseval.CLIENT_PUBLIC_DIRECTORY.mkdir(exist_ok=True, parents=True)

    # Upload directory
    if file_or_directory.is_dir():
        shutil.copytree(file_or_directory, destination)

    # Upload file
    else:
        shutil.copyfile(file_or_directory, destination)

    # Return URL
    return f'/evaluation-files/{file_or_directory}'
