import math
import scipy.stats


###############################################################################
# Statistical tests
###############################################################################


def binomial(counts):
    """Performs a two-sided Binomial t-test"""
    result = scipy.stats.binomtest(counts[0], sum(counts))
    return {
        'Sample mean': result.proportion_estimate,
        'p-value': result.pvalue}


def student_ttest(x, y, random_seed=0):
    """Performs a two-sided Student t-test"""
    result = scipy.stats.ttest_ind(x, y, random_state=random_seed)
    return {
        'Test statistic': result.statistic,
        'p-value': result.pvalue}


def mannwhitney(x, y):
    """Performs a two-sided Mann-Whitney test"""
    # Handle no data
    if len(x) == 0 or len(y) == 0:
        return {'Test statistic': math.nan, 'p-value': math.nan}

    # Perform test
    result = scipy.stats.mannwhitneyu(x, y)

    return {
        'Test statistic': result.statistic,
        'p-value': result.pvalue}


def welchs_ttest(x, y, random_seed=0):
    """Performs a two-sided Welch's t-test"""
    result = scipy.stats.ttest_ind(
        x,
        y,
        equal_var=False,
        random_state=random_seed)
    return {
        'Test statistic': result.statistic,
        'p-value': result.pvalue}


def wilcoxon(x, y):
    """Performs a two-sided Wilcoxon signed-rank test"""
    # Handle no data
    if len(x) == 0:
        return

    # Perform test
    result = scipy.stats.wilcoxon(x, y)

    return {
        'Test statistic': result.statistic,
        'p-value': result.pvalue}
