import reseval


###############################################################################
# Pay participants
###############################################################################


def pay(name: str):
    """Pay participants of a subjective evaluation

    Args:
        name: The name of the evaluation to pay for
    """
    reseval.crowdsource.pay(name)
