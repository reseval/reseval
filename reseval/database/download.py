import argparse
from pathlib import Path

import reseval


###############################################################################
# Entry point for downloading the database tables of a subjective evaluation
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Download the database tables of a subjective evaluation')
    parser.add_argument('name', help='The name of the evaluation')
    parser.add_argument(
        'directory',
        default=Path(),
        help='The directory to populate with the database contents')
    parser.add_argument(
        '--tables',
        default=reseval.database.TABLES,
        help='The tables to download')
    return parser.parse_args()


reseval.database.download(**vars(parse_args()))
