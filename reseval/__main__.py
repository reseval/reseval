import argparse
from pathlib import Path

import reseval


###############################################################################
# Entry point
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Run a subjective evaluation')
    parser.add_argument('config', type=Path, help='The configuration file')
    parser.add_argument(
        'directory',
        type=Path,
        help='The directory containing the files to evaluate')
    parser.add_argument(
        '--results_directory',
        type=Path,
        default=Path(),
        help='The directory to save results to')
    parser.add_argument(
        '--local',
        action='store_true',
        help='Run subjective evaluation locally')
    parser.add_argument(
        '--production',
        action='store_true',
        help='Deploy the subjective evaluation to crowdsource participants')
    parser.add_argument(
        '--interval',
        type=int,
        default=120,
        help='The time between monitoring updates in seconds')
    return parser.parse_args()


reseval.run(**vars(parse_args()))
