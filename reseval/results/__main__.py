import argparse
from pathlib import Path

import reseval


###############################################################################
# Get the results of a subjective evaluation
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Get the results of a subjective evaluation')
    parser.add_argument(
        'name',
        help='The name of the subjective evaluation to retrieve results for')
    parser.add_argument(
        '--directory',
        type=Path,
        default=Path(),
        help='The directory to save results')
    return parser.parse_args()


reseval.results(**vars(parse_args()))
