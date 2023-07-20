import shutil
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
    # Evaluation doesn't exist
    if not (reseval.EVALUATION_DIRECTORY / name).exists():
        return

    # Is the evaluation currently active?
    try:
        active = reseval.crowdsource.active(name)
    except Exception:
        if force:
            active = False

    paid = reseval.crowdsource.paid(name)
    if active or not paid:

        if not force:
            tag = (
                ('active ' if active else '') +
                ('unpaid ' if not paid else ''))
            raise ValueError(
                f'Not destroying {tag}subjective evaluation {name}')

        else:

            # Pay participants
            if not paid:
                reseval.crowdsource.pay(name)

    # Maybe destroy crowdsource task
    reseval.crowdsource.destroy(name)

    # Destroy database
    reseval.database.destroy(name)

    # Destroy server
    reseval.server.destroy(name)

    # Destroy storage
    reseval.storage.destroy(name)

    # Clean-up cache
    shutil.rmtree(reseval.EVALUATION_DIRECTORY / name)
