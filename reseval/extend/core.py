import re

import reseval


def extend(
    name: str,
    participants: int,
    local: bool = False,
    production: bool = False):
    """Extend a subjective evaluation

    Args:
        name: The name of the evaluation to extend
        participants: The number of new participants to add to the evaluation
        local: Run subjective evaluation locally
        production: Deploy the subjective evaluation to crowdsource
            participants
    """
    if not (reseval.EVALUATION_DIRECTORY / name).exists():
        raise ValueError(f'Cannot extend non-existant evaluation {name}')

    if production and local:
        raise ValueError('Cannot deploy production build locally')

    # We can only restart evaluations that have been run in the same mode
    prod_file = reseval.EVALUATION_DIRECTORY / name / '.prod'
    if not production and prod_file.exists():
        raise ValueError(
            f'Cannot extend production evaluation {name} '
            'in non-production mode')
    local_file = reseval.EVALUATION_DIRECTORY / name / '.local'
    if not local and local_file.exists():
        raise ValueError(
            f'Cannot extend local evaluation {name} '
            'in non-local mode')

    # Extend crowdsourcing task
    reseval.crowdsource.extend(name, participants)

    # Get saved configuration
    config_file = reseval.EVALUATION_DIRECTORY / name / 'config.yaml'
    with open(config_file, encoding='utf-8') as file:
        lines = file.readlines()

    # Replace number of participants
    for i in range(len(lines)):
        if lines[i].startswith('participants: '):
            previous = re.findall(r'\d+', lines[i])[0]
            current = int(previous) + participants
            lines[i] = re.sub(r'\d+', str(current), lines[i])

    # Save new configuration
    with open(config_file, 'w', encoding='utf-8') as file:
        for line in lines:
            file.write(line)
