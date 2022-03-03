import argparse

import reseval


###############################################################################
# Entry point for destroying subjective evaluation compute resources
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Clean-up database, server, and storage resources')
    parser.add_argument('name', help='The name of the evaluation to destroy')
    parser.add_argument(
        '--force',
        action='store_true',
        help='Destroy evaluation resources even if it is still running. ' +
             'Pays all participants who have taken the evaluation.')
    return parser.parse_args()


reseval.destroy(**vars(parse_args()))
