import json
import os
import typing
from pathlib import Path

import reseval


###############################################################################
# Get subjective evaluation results
###############################################################################


def results(
    name: str,
    directory: typing.Union[str, bytes, os.PathLike] = Path()) -> dict:
    """Get the results of a subjective evaluation

    Args:
        name: The name of the subjective evaluation to retrieve results for
        directory: The directory to save results

    Returns:
        dict: Evaluation results
    """
    # Download and save crowdsource results
    crowdsource = reseval.crowdsource.assignments(name)
    crowdsource_file = directory / name / 'crowdsource' / 'crowdsource.json'
    crowdsource_file.parent.mkdir(exist_ok=True, parents=True)
    with open(crowdsource_file, 'w') as file:
        json.dump(crowdsource, file, indent=4, default=str)

    # Download database tables
    reseval.database.download(
        name,
        reseval.EVALUATION_DIRECTORY / name / 'tables')
    if directory is not None:
        reseval.database.download(name, directory / name / 'tables')

    # Load responses
    config = reseval.load.config_by_name(name)
    conditions = reseval.load.conditions(name)
    responses = reseval.load.responses(name)

    # No responses yet
    if len(responses) == 0:
        results = {'samples': 0, 'conditions': {}}

        # Save results
        with open(directory / name / 'results.json', 'w') as file:
            json.dump(results, file, indent=4)

        return results

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
    with open(directory / name / 'results.json', 'w') as file:
        json.dump(analysis | {'stems': stem_scores}, file, indent=4)

    return analysis
