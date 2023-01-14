import reseval


###############################################################################
# Test selection
###############################################################################


def get(config):
    """Get a test class"""
    test = config['test']

    if test == 'ab':
        return reseval.test.AB
    elif test == 'abx':
        return reseval.test.ABX
    elif test == 'mos':
        return reseval.test.MOS
    elif test == 'mushra':
        return reseval.test.MUSHRA
    elif test == 'wordselect':
        return reseval.test.WordSelect
    raise ValueError(f'Test {test} is not defined')
