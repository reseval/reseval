from pathlib import Path


###############################################################################
# Credentials
###############################################################################


# Environment variable file
ENVIRONMENT_FILE = Path(__file__).parent.parent / '.env'

# API keys file
KEYS_FILE = Path(__file__).parent.parent / '.keys'


###############################################################################
# Directories
###############################################################################


# Location to save Python module assets
ASSETS_DIR = Path(__file__).parent / 'assets'

# Location that the client will load JSON files that we save
CLIENT_JSON_DIRECTORY = ASSETS_DIR / 'client' / 'src' / 'json'

# Location that the client expects to find an assignment JSON file
CLIENT_ASSIGNMENT_FILE = CLIENT_JSON_DIRECTORY / 'assignments.json'

# Location that the client expects to find a configuration JSON file
CLIENT_CONFIGURATION_FILE = CLIENT_JSON_DIRECTORY / 'config.json'

# Location that the client serves files from if we are not using cloud storage
CLIENT_PUBLIC_DIRECTORY = ASSETS_DIR / 'client' / 'public' / 'evaluation-files'

# Location to save results
EVALUATION_DIRECTORY = Path(__file__).parent.parent / 'evaluations'


###############################################################################
# Server
###############################################################################


# URL used for local deployment
LOCALHOST_URL = 'http://localhost:3001/'
