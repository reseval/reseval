import json
import os
import typing

import reseval


###############################################################################
# Get subjective evaluation results
###############################################################################


def results(name: str, directory: typing.Union[str, bytes, os.PathLike]):
    """Get the results of a subjective evaluation

    Args:
        name: The name of the subjective evaluation to retrieve results for
        directory: The directory to save results

    Returns:
        results: dict
            The evaluation results. Keys are ['samples', 'conditions'].
                samples: int
                    The number of evaluation samples received
                conditions: dict
                    The pairwise results between conditions
    """
    # Download database tables
    reseval.database.download(
        name,
        reseval.EVALUATION_DIRECTORY / name / 'tables')

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
    responses_by_stem = {}
    for response in responses:
        stem = response['Stem']
        if stem in responses_by_stem:
            responses_by_stem[stem].append(response['Response'])
        else:
            responses_by_stem[stem] = [response['Response']]

    # Get test
    test = reseval.test.get(config)

    # Analyze results
    analysis, stem_scores = test.analyze(
        conditions,
        responses_by_stem,
        config['random_seed'])

    # Save results
    with open(directory / 'results.json', 'w') as file:
        json.dump(analysis, file, indent=4)
    with open(directory / 'stemresults.json', 'w') as file:
        json.dump(stem_scores, file, indent=4, sort_keys=True)

    return analysis
