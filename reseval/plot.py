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


def violin(results, file, yticks):
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
    values = np.array(
        [np.array(sorted(value), dtype=int) for value in data.values()])

    # Order data by average value
    means = np.nan_to_num([value.mean() for value in values])

    # TEMPORARY
    # print([(key, mean) for key, mean in zip(keys, means)])

    # Get medians
    _, medians, _ = np.percentile(
        values,
        [25, 50, 75],
        axis=values.ndim - 1)

    indices = np.argsort(means)
    means, keys, values, medians = (
        means[indices],
        list(keys[indices]),
        values[indices],
        medians[indices])

    # No data
    if not all(len(value) for value in values):
        return

    # Create violin plot
    figure, ax = plt.subplots(1, 1, squeeze=True, figsize=(16, 6))
    ax.violinplot(
        values.T,
        showmeans=False,
        showmedians=False,
        showextrema=False)

    # Add mean and median markers
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
    for y in yticks:
        ax.hlines(
            y=y,
            xmin=0,
            xmax=len(keys) + .3,
            linewidth=1,
            color='#666666',
            alpha=.3)

    # TEMPORARY
    # label_map = {
    #     'bitcrush': 'Low anchor',
    #     'bottleneck': 'ASR bottleneck',
    #     'w2v2fc': 'Charsiu',
    #     'mel': 'Mels',
    #     'encodec': 'EnCodec',
    #     'w2v2fb': 'Wav2vec 2.0',
    #     'original': 'Original',
    # }

    # Add labels
    ax.set_xticks(
        np.arange(1, len(keys) + 1),
        # labels=[label_map[key] for key in keys],
        labels=keys,
        fontsize=16)
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
