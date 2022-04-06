import argparse
import glob
import io
import multiprocessing as mp
import os
from pathlib import Path

from PIL import Image


###############################################################################
# Convert image to jpeg
###############################################################################


def from_file_to_file(input_file, output_file=None):
    """Convert image file to jpeg"""
    # Default output filename is same as input but with JPEG extension
    if output_file is None:
        output_file = input_file.with_suffix('.jpg')

    # Open image file
    image = Image.open(input_file)

    # Create raw byte buffer
    buffer = io.BytesIO()

    # Perform compression to 25% of the original file size
    image.save(buffer, 'JPEG', quality=25)

    # Write the buffer to a file
    with open(output_file, 'w') as file:
        file.write(buffer.contents())


def from_files_to_files(input_files, output_files=None):
    """Convert audio files to mp3"""
    # Convert to paths
    input_files = [Path(file) for file in input_files]

    # Default output filename is same as input but with MP3 extension
    if output_files is None:
        output_files = [file.with_suffix('.jpg') for file in input_files]

    # Multiprocess conversion
    with mp.Pool() as pool:
        pool.starmap(from_file_to_file, zip(input_files, output_files))

    # for input_file, output_file in zip(input_files, output_files):
    #     from_file_to_file(input_file, output_file)


###############################################################################
# Entry point
###############################################################################


def expand_files(files):
    """Expands a wildcard to a list of paths for Windows compatibility"""
    # Split at whitespace
    files = files.split()

    # Handle wildcard expansion
    if len(files) == 1 and '*' in files[0]:
        files = glob.glob(files[0])

    # Convert to Path objects
    return files


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Convert images to JPEG')

    # Handle wildcards across platforms
    if os.name == 'nt':
        parser.add_argument(
            '--input_files',
            type=expand_files,
            help='The image files to convert to jpeg')
    else:
        parser.add_argument(
            '--input_files',
            nargs='+',
            help='The image files to convert to jpeg')

    parser.add_argument(
        '--output_files',
        type=Path,
        nargs='+',
        help='The corresponding output files. ' +
             'Uses same filename with jpg extension by default')
    return parser.parse_args()


if __name__ == '__main__':
    from_files_to_files(**vars(parse_args()))
