import argparse

import reseval


###############################################################################
# Entry point for dropping a database
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Drop a database from an evaluation')
    parser.add_argument('name', help='The name of the evaluation')
    return parser.parse_args()


reseval.database.destroy(**vars(parse_args()))
