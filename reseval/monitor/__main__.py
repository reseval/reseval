import argparse

import reseval


###############################################################################
# Entry point for monitoring subjective evaluations
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Monitor subjective evaluations')
    parser.add_argument(
        '--names',
        nargs='+',
        help='The names of the evaluations to monitor. ' +
             'If not provided, monitors all evaluations.')
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='The time between monitoring updates in seconds')
    return parser.parse_args()


reseval.monitor(**vars(parse_args()))
