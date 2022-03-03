import contextlib
import os

import reseval


###############################################################################
# Run subjective evaluation pipeline
###############################################################################


def run(config, directory, local=False, production=False, interval=120):
    """Perform subjective evaluation"""
    # Setup evaluation
    name = reseval.create(config, directory, local, production, detach=True)

    # Monitor evaluation until completion
    try:

        # Monitor progress
        reseval.monitor(name, interval)

        # Pay participants
        reseval.pay(name)

        # Get results
        reseval.results(name, reseval.EVALUATION_DIRECTORY / name)

    except (Exception, KeyboardInterrupt) as exception:

        # Make sure credentials get deleted for non-production deployment
        if not production:
            reseval.destroy(name, force=True, all=True)
        raise exception

    # Cleanup database, server, and storage
    if production:
        reseval.destroy(name)
    else:
        reseval.destroy(name, force=True, all=True)


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
