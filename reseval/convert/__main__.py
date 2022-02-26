import argparse
from pathlib import Path

import reseval


###############################################################################
# File conversion
###############################################################################


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Perform file compression recursively on a directory')
    parser.add_argument(
        'input_directory',
        type=Path,
        help='The directory of files to compress')
    parser.add_argument(
        'output_directory',
        type=Path,
        help='The location to save compressed files')


reseval.convert(**vars(parse_args()))
