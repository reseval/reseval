import os
import re
import typing

import reseval


def extend(
    name: str,
    directory: typing.Union[str, bytes, os.PathLike],
    participants: int,
    local: bool = False,
    production: bool = False,
    monitor: bool = False,
    interval: int = 120,
    detach: bool = False):
    """Extend a subjective evaluation

    Args:
        name: The name of the evaluation to extend
        directory: The directory containing the files to evaluate
        participants: The number of new participants to add to the evaluation
        local: Run subjective evaluation locally
        production: Deploy the subjective evaluation to crowdsource
            participants
        monitor: Whether to monitor the evaluation
        interval: The time between monitoring updates in seconds
        detach: If running locally, detaches the server process
    """
    # Extend crowdsourcing task
    # TODO - Extend is probably broken, as it assumes it will find a HIT with
    #        the same HIT ID. But we can't reuse the previous task when the
    #        survey XML points to the previous server's URL. So we have to
    #        create a new task instead. This may also mean that we should
    #        eliminate the "resume" API.
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
