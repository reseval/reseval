import contextlib
import os
import typing
from pathlib import Path

import reseval


###############################################################################
# Run subjective evaluation pipeline
###############################################################################


def run(
    config: str,
    directory: typing.Union[str, bytes, os.PathLike],
    results_directory: typing.Union[str, bytes, os.PathLike] = Path(),
    local: bool = False,
    production: bool = False,
    interval: int = 120) -> dict:
    """Perform subjective evaluation

    Args:
        config: The configuration file
        directory: The directory containing the files to evaluate
        results_directory: The directory to save results
        local: Run subjective evaluation locally
        production: Deploy the subjective evaluation to crowdsource
            participants
        interval: The time between monitoring updates in seconds

    Returns:
        dict: Evaluation results
    """
    # Setup evaluation
    name = reseval.create(config, directory, local, production, detach=True)

    try:

        # Monitor evaluation until completion
        reseval.monitor([name], interval, exit_on_finish=True)

    except (Exception, KeyboardInterrupt) as exception:

        # Perform clean-up only if evaluation is local
        if local:
            print(exception)
        else:
            raise exception

    # Pay participants
    reseval.pay(name)

    # Get results
    results = reseval.results(name, results_directory)

    # Cleanup database, server, storage, and crowdsource task
    reseval.destroy(name, force=True)

    return results


###############################################################################
# Utilities
###############################################################################


@contextlib.contextmanager
def chdir(directory):
    """Change working directory"""
    curr_dir = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(curr_dir)


def is_local(name):
    """Returns true if the evaluation is hosted locally"""
    return (reseval.EVALUATION_DIRECTORY / name / '.local').exists()
