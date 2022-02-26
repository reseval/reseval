import json

import reseval


###############################################################################
# Analyze subjective evaluation results
###############################################################################


def analyze(name):
    """Download and analyze the results of a subjective evaluation"""
    # Download database tables
    reseval.database.download(name)

    # Load responses
    config = reseval.load.config_by_name(name)
    conditions = reseval.load.conditions(name)
    responses = reseval.load.responses(name)

    # No responses yet
    if len(responses) == 0:
        return { 'samples': 0, 'conditions': {} }

    # Get condition names
    conditions = [condition['Condition'] for condition in conditions]

    # Group results by file stems
    results = {}
    for response in responses:
        stem = response['Stem']
        if stem in results:
            results[stem].append(response['Response'])
        else:
            results[stem] = [response['Response']]

    # Get test
    test = reseval.test.get(config)

    # Analyze results
    analysis, stem_scores = test.analyze(
        conditions,
        results,
        config['random_seed'])

    # Save results
    directory = reseval.EVALUATION_DIRECTORY / name
    with open(directory / 'results.json', 'w') as file:
        json.dump(analysis, file, indent=4)
    with open(directory / 'stemresults.json', 'w') as file:
        json.dump(stem_scores, file, indent=4, sort_keys=True)

    return analysis
