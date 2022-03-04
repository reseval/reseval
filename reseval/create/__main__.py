import argparse
from pathlib import Path

import reseval


###############################################################################
# Entry point
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Create a subjective evaluation')
    parser.add_argument('config', type=Path, help='The configuration file')
    parser.add_argument(
        'directory',
        type=Path,
        help='The directory containing the files to evaluate')
    parser.add_argument(
        '--local',
        action='store_true',
        help='Run subjective evaluation locally')
    parser.add_argument(
        '--production',
        action='store_true',
        help='Deploy the subjective evaluation to crowdsource participants')
    return parser.parse_args()


reseval.create(**vars(parse_args()))
