import argparse
from pathlib import Path

import reseval


###############################################################################
# Entry point for extending a subjective evaluation
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Extend a subjective evaluation')
    parser.add_argument('name', help='The name of the evaluation to extend')
    parser.add_argument(
        'participants',
        type=int,
        help='The number of new participants to add to the evaluation')
    parser.add_argument(
        '--local',
        action='store_true',
        help='Run subjective evaluation locally')
    parser.add_argument(
        '--production',
        action='store_true',
        help='Deploy the subjective evaluation to crowdsource participants')
    return parser.parse_args()


reseval.extend(**vars(parse_args()))
