import reseval


def resume(
    name,
    directory,
    local=False,
    production=False,
    monitor=False,
    interval=120,
    detach=False):
    """Restart an evaluation that didn't finish"""
    if not (reseval.EVALUATION_DIRECTORY / name).exists():
        raise ValueError(f'Cannot resume non-existant evaluation {name}')

    if production and local:
        raise ValueError('Cannot deploy production build locally')

    # We can only restart evaluations that have been run in the same mode
    prod_file = reseval.EVALUATION_DIRECTORY / name / '.prod'
    if production and not prod_file.exists():
        raise ValueError(
            f'Cannot restart production evaluation {name} '
            'in non-production mode')
    local_file = reseval.EVALUATION_DIRECTORY / name / '.local'
    if local and not local_file.exists():
        raise ValueError(
            f'Cannot restart local evaluation {name} '
            'in non-local mode')

    # Get config
    config_file = reseval.EVALUATION_DIRECTORY / name / 'config.yaml'

    if monitor:

        # Start evaluation and monitor
        reseval.run(config_file, directory, local, production, interval)

    else:

        # Start evaluation
        reseval.create(config_file, directory, local, production, detach)
