import reseval


###############################################################################
# Run subjective evaluation pipeline
###############################################################################


def run(config, directory, local=False, production=False, interval=120):
    """Perform subjective evaluation"""
    # Setup evaluation
    name = reseval.create(config, directory, local, production)

    # Monitor evaluation until completion
    try:

        # Monitor progress
        reseval.monitor(name, interval)

        # Pay participants
        reseval.pay(name)

        # Download and analyze results
        reseval.analyze(name)

    except (Exception, KeyboardInterrupt) as exception:

        # Make sure credentials get deleted for local development
        if local:
            reseval.destroy(name, True)
        raise exception

    # Cleanup database, server, and storage
    reseval.destroy(name)


###############################################################################
# Utilities
###############################################################################


def is_local(name):
    """Returns true if the evaluation is hosted locally"""
    return (reseval.EVALUATION_DIRECTORY / name / '.local').exists()
