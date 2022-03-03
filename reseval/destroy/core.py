import reseval


###############################################################################
# Cleanup subjective evaluation compute resources
###############################################################################


def destroy(name: str, force: bool = False):
    """Destroys an evaluation's storage, database, server, and crowdsource task

    Args:
        name: The name of the evaluation to destroy
        force: Destroy evaluation resources even if it is still running. Pays
            all participants who have taken the evaluation.
    """
    # Cleanup crowdsourcing
    active = reseval.crowdsource.active(name)
    paid = reseval.crowdsource.paid(name)
    analyzed = (reseval.EVALUATION_DIRECTORY / name / 'results.json').exists()
    if active or not paid or not analyzed:

        if not force:
            tag = (
                ('active ' if active else '') +
                ('unpaid ' if not paid else '') +
                ('unanalyzed ' if not analyzed else ''))
            raise ValueError(
                f'Not destroying {tag}subjective evaluation {name}')

        else:

            # Stop the evaluation
            if active:
                reseval.crowdsource.stop(name)

            # Pay participants
            if not paid:
                reseval.crowdsource.pay(name)

    # Maybe destroy crowdsource task
    reseval.crowdsource.destroy(name)

    # Destroy server
    reseval.server.destroy(name)

    # Destroy database
    reseval.database.destroy(name)

    # Destroy storage
    reseval.storage.destroy(name)
