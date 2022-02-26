import argparse

import reseval


###############################################################################
# Analyze the results of a subjective evaluation
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Analyze the results of a subjective evaluation')
    parser.add_argument(
        'name',
        help='The name of the subjective evaluation to analyze')
    return parser.parse_args()


reseval.analyze(**vars(parse_args()))
