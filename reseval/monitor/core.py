import time

import rich
import rich.progress

import reseval


###############################################################################
# Monitor subjective evaluations
###############################################################################


def monitor(name=None, interval=120):
    """Monitor subjective evaluations"""
    # List evaluations
    names = reseval.EVALUATION_DIRECTORY.glob('*') if name is None else [name]

    # Get total samples for each evaluation
    configs = [reseval.load.config_by_name(name) for name in names]
    totals = [
        cfg['participants'] * cfg['samples_per_participant']
        for cfg in configs]

    # Setup monitoring display
    analyses = [reseval.analyze(name) for name in names]

    # Render display and monitor
    content = displays(names, totals, analyses)
    with rich.progress.Live(content, refresh_per_second=.2) as live:

        # Monitor evaluations
        while True:

            # Iterate over evaluations
            for index, (name, total) in enumerate(zip(names, totals)):

                # Get current progress
                count = reseval.crowdsource.progress(name)

                # Update display if we have new results
                if count != analyses[index]['samples']:

                    # Get current statistics
                    analysis = reseval.analyze(name)
                    analyses[index] = analysis

                    # Update display
                    live.update(displays(names, totals, analyses))

            # If we're monitoring a single evaluation and it is done, exit
            if (len(names) == 1 and
                analyses[0]['samples'] == total and
                not reseval.crowdsource.active(names[0])):
                break

            # Wait a while
            time.sleep(interval)


def display(name, total, analysis):
    """Format one evaluation for display"""
    # Format a table of statistics
    table = rich.progress.Table(title=name)
    table.add_column('total')
    table.add_column('samples')
    keys = analysis['conditions'].keys()
    values = [
        format_stats(value) for value in analysis['conditions'].values()]
    for key in keys:
        table.add_column(key)
    table.add_row(str(total), str(analysis['samples']), *values)

    # Create progress bar
    bar = rich.progress.Progress(
        rich.progress.BarColumn(),
        rich.progress.TextColumn(
            '[progress.percentage]{task.percentage:>3.0f}%'))

    # Add task to progress bar
    bar.add_task(name, total=total, completed=analysis['samples'])

    return table, bar


def displays(names, totals, analyses):
    """Format multiple evaluations for display"""
    displays = rich.progress.Table.grid()
    for name, total, analysis in zip(names, totals, analyses):

        # Get stats and renderables
        table, bar = display(name, total, analysis)

        # Add table and progress bar to display
        displays.add_row(
            rich.panel.Panel.fit(table, padding=(2, 2)),
            rich.panel.Panel.fit(bar, padding=(2, 2)))

    return displays


def format_stats(stats):
    """Format statistics for printing to a table"""
    result = ''
    for key, value in stats.items():
        result += f'{key} - {value}\n'
    return result[:-1]
