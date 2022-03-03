import argparse

import reseval


###############################################################################
# Entry point for paying participants
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Pay participants of a subjective evaluation')
    parser.add_argument('name', help='The name of the evaluation to pay for')
    return parser.parse_args()


reseval.pay(**vars(parse_args()))
