import re

import reseval


def extend(
    name,
    directory,
    participants,
    local=False,
    production=False,
    monitor=False,
    interval=120,
    detach=False):
    """Extend a subjective evaluation"""
    # Extend crowdsourcing task
    reseval.crowdsource.extend(name, participants)

    # Get saved configuration
    config_file = reseval.EVALUATION_DIRECTORY / name / 'config.yaml'
    with open(config_file) as file:
        lines = file.readlines()

    # Replace number of participants
    for i in range(len(lines)):
        if lines[i].startswith('participants: '):
            previous = re.findall(r'\d+', lines[i])[0]
            current = int(previous) + participants
            lines[i] = re.sub(r'\d+', str(current), lines[i])

    # Save new configuration
    with open(config_file, 'w') as file:
        for line in lines:
            file.write(line)

    # Start evaluation
    reseval.resume(
        name,
        directory,
        local,
        production,
        monitor,
        interval,
        detach)
