import argparse

import reseval


###############################################################################
# Entry point for adding or updating credentials
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Stop a subjective evaluation without ' +
                    'destroying resources')
    parser.add_argument('--aws_api_key', help='The public API key for AWS')
    parser.add_argument(
        '--aws_api_secret_key',
        help='The private API key for AWS')
    parser.add_argument('--heroku_api_key', help='The API key for Heroku')
    parser.add_argument(
        '--mysql_local_user',
        help='The username of the local MySQL database')
    parser.add_argument(
        '--mysql_local_password',
        help='The corresponding password of the local MySQL database')
    return parser.parse_args()


reseval.credentials(**vars(parse_args()))
