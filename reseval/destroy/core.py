import reseval


###############################################################################
# Cleanup subjective evaluation compute resources
###############################################################################


def destroy(name, force=False):
    """Destroys compute resources corresponding to a subjective evaluation"""
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

    # Destroy cloud storage
    # try:
    reseval.storage.destroy(name)
    # except Exception:
        # pass

    # Destroy database
    # try:
    reseval.database.destroy(name)
    # except Exception:
        # pass

    # Destroy server
    # try:
    reseval.server.destroy(name)
    # except Exception:
        # pass
