from pathlib import Path

import appdirs


###############################################################################
# Cache
###############################################################################


# Application data directory. This is a persistant cross-platform cache
# directory. We use this to store a copy of the client and server code, as
# well as the following locally generated files.
# - .env - The local database credentials used for local development
# - .keys - The API keys
# - client/build - The optimized front-end code for deployment
# - client/node_modules - The installed front-end packages
# - client/src/json/assignments.json - The pre-generated assignments of
#     evaluators to files to evaluate
# - client/src/json/config.json - The configuration file including any
#     additions made by reseval.create, such as whether we are running local
#     development
# - evaluations - A directory containing the credentials, database output, and
#     results of every evaluation. Credentials are deleted when the
#     corresponding resource is destroyed.
# - node_modules - The installed server packages used for local development
CACHE = Path(appdirs.user_cache_dir('reseval', 'reseval'))


###############################################################################
# Credentials
###############################################################################


# Environment variable file
ENVIRONMENT_FILE = CACHE / '.env'

# API keys file
KEYS_FILE = CACHE / '.keys'


###############################################################################
# Directories
###############################################################################


# Location of Python package data
ASSETS_DIR = Path(__file__).parent / 'assets'

# Location that the client will load JSON files that we save
CLIENT_JSON_DIRECTORY = CACHE / 'client' / 'src' / 'json'

# Location that the client expects to find an assignment JSON file
CLIENT_ASSIGNMENT_FILE = CLIENT_JSON_DIRECTORY / 'assignments.json'

# Location that the client expects to find a JSON file of condition assignments
CLIENT_CONDITION_FILE = CLIENT_JSON_DIRECTORY / 'conditions.json'

# Location that the client expects to find a configuration JSON file
CLIENT_CONFIGURATION_FILE = CLIENT_JSON_DIRECTORY / 'config.json'

# Location that the client serves files from if we are not using cloud storage
CLIENT_PUBLIC_DIRECTORY = (
    CACHE /
    'client' /
    'public' /
    'evaluation-files')

# Location to save results
EVALUATION_DIRECTORY = CACHE / 'evaluations'

# Location of listening test audio files
LISTENING_TEST_DIRECTORY = ASSETS_DIR / 'listening_test'


###############################################################################
# Server
###############################################################################


# URL used for local deployment
LOCALHOST_URL = 'http://localhost:3001/'
