import csv
import errno
import json
import os

import dotenv
import yaml

import reseval


###############################################################################
# File loading
###############################################################################


def api_keys():
    """Load cached API keys as environment variables"""
    with open(reseval.KEYS_FILE) as file:
        for line in file.readlines():
            key, value = line.rstrip().split('=', 1)
            os.environ[key] = value


def config_by_name(name):
    """Load configuration of an existing evaluation"""
    return config_from_file(reseval.EVALUATION_DIRECTORY / name / 'config.yaml')


def config_from_file(file):
    """Load configuration from file"""
    with open(file, encoding='utf-8') as file:
        return yaml.full_load(file)


def credentials_by_name(name, group):
    """Load credentials by evaluation name"""
    file = (
        reseval.EVALUATION_DIRECTORY /
        name /
        'credentials' /
        f'{group}.json')
    return credentials_from_file(file)


def credentials_from_file(file):
    """Load credentials corresponding to an evaluation from file"""
    with open(file) as file:
        return json.load(file)


def environment_variables_by_name(name):
    """Load environment variables corresponding to an evaluation"""
    file = reseval.EVALUATION_DIRECTORY / name / 'credentials' / '.env'

    # Raise if the file does not exist
    if not file.exists():
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)

    # Load as environment variables
    dotenv.load_dotenv(file, override=True)


###############################################################################
# Database table loading
###############################################################################


def conditions(name):
    """Load the table of conditions used in a subjective evaluation"""
    return load_table(name, 'conditions')


def participants(name):
    """Load the table of participants from a subjective evaluation"""
    return load_table(name, 'participants')


def responses(config):
    """Load the table of responses from a subjective evaluation"""
    return load_table(config, 'responses')


###############################################################################
# Utilities
###############################################################################


def load_table(name, table):
    """Load a database table that has been downloaded to local storage"""
    file = (
        reseval.EVALUATION_DIRECTORY /
        name /
        'tables' /
        f'{table}.csv')
    with open(file) as file:
        return [row for row in csv.DictReader(file)]
