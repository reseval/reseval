import argparse
from pathlib import Path

import reseval


###############################################################################
# Entry point for restarting an evaluation that was destroyed before finishing
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Restart an evaluation that didn\'t finish')
    parser.add_argument('name', help='The name of the evaluation to start')
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
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='Whether to monitor the evaluation')
    parser.add_argument(
        '--interval',
        type=int,
        default=120,
        help='The time between monitoring updates in seconds')
    return parser.parse_args()


reseval.resume(**vars(parse_args()))
