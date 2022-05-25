import matplotlib
import matplotlib.pyplot as plt
import numpy as np


###############################################################################
# Statistical plots
###############################################################################


def barh(results, file):
    """Create a barh plot"""
    # TODO
    pass


def violin(results, file):
    """Create a violin plot"""
    # Set font size
    matplotlib.rcParams.update({'font.size': 18})

    # Organize data by condition
    data = {}
    for _, values in results.items():
        for condition, scores in values.items():
            if condition not in data:
                data[condition] = scores
            else:
                data[condition].extend(scores)
    keys = np.array(list(data.keys()))
    values = np.array([sorted(value) for value in data.values()])

    # Order data by average value
    means = np.mean(values, axis=1)
    indices = np.argsort(means)
    means, keys, values = means[indices], list(keys[indices]), values[indices]

    # Create violin plot
    figure, ax = plt.subplots(1, 1, squeeze=True, figsize=(16, 6))
    ax.violinplot(
        values.T,
        showmeans=False,
        showmedians=False,
        showextrema=False)

    # Get locations of start and ends of violins
    _, medians, _ = np.percentile(
        values,
        [25, 50, 75],
        axis=1)

    # Style axes
    inds = np.arange(1, len(medians) + 1)
    ax.scatter(inds, means, marker='o', color='black', s=80, zorder=3)
    ax.scatter(inds, medians, marker='o', color='white', s=80, zorder=3)

    # Style axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    for y in [0, 20, 40, 60, 80, 100]:
        ax.hlines(
            y=y,
            xmin=0,
            xmax=5.3,
            linewidth=1,
            color='#666666',
            alpha=.3)

    # Add labels
    ax.set_xticks(np.arange(1, len(keys) + 1), labels=keys)
    ax.set_xlim(0.25, len(keys) + 0.75)

    # Save figure
    figure.savefig(file, bbox_inches='tight', pad_inches=0)


###############################################################################
# Utilities
###############################################################################


def adjacent_values(vals, q1, q3):
    upper_adjacent_value = q3 + (q3 - q1) * 1.5
    upper_adjacent_value = np.clip(upper_adjacent_value, q3, vals[-1])
    lower_adjacent_value = q1 - (q3 - q1) * 1.5
    lower_adjacent_value = np.clip(lower_adjacent_value, vals[0], q1)
    return lower_adjacent_value, upper_adjacent_value
