import itertools

import reseval
from .base import Base


###############################################################################
# MUSHRA test
###############################################################################


class MUSHRA(Base):

    @classmethod
    def analyze(cls, conditions, responses, random_seed=0):
        """Perform statistical analysis on evaluation results"""
        # Get MUSHRA ratings
        condition_scores, stem_scores = cls.scores(conditions, responses)

        # Iterate over unique pairs of conditions
        samples = len(condition_scores[conditions[0]])
        all_results = {'samples': samples, 'conditions': {}}
        for condition_a, condition_b in itertools.combinations(conditions, 2):
            results = {}

            # Two-sided t-test assuming equal variance
            results['student_ttest'] = reseval.stats.student_ttest(
                condition_scores[condition_a],
                condition_scores[condition_b],
                random_seed)

            # Two-sided t-test assuming unequal variance
            results['welchs_ttest'] = reseval.stats.welchs_ttest(
                condition_scores[condition_a],
                condition_scores[condition_b],
                random_seed)

            # Two-sided Wilcoxon test with no distribution assumptions
            results['wilcoxon'] = reseval.stats.wilcoxon(
                condition_scores[condition_a],
                condition_scores[condition_b])

            all_results['conditions'][f'{condition_a}-{condition_b}'] = results

        return all_results, stem_scores

    @classmethod
    def plot(cls, results, file):
        """Create a plot of the results and save to disk"""
        reseval.plot.violin(results, file, range(0, 101, 20))

    def response_type(self):
        """Retrieve the MySQL datatype of a participant response"""
        # For the MUSHRA test, the response is a string of concatenated
        # three-digit numbers, where each number is a value between 000 and
        # 100, inclusive. For example, if your MUSHRA test has four conditions
        # and the conditions, in alphabetical order, are given scores 67, 72,
        # 95, and 23, respectively, the response will be "067072095023".
        return f'varchar({3 * len(self.conditions)})'

    @classmethod
    def scores(cls, conditions, responses):
        """Get scores from participant responses"""
        condition_scores = {cond: [] for cond in conditions}
        stem_scores = {
            stem: {cond: [] for cond in conditions} for stem in responses}
        for stem, results in responses.items():
            for result in results:
                scores = [
                    int(result[i:i + 3]) for i in range(0, len(result), 3)]
                for condition, score in zip(sorted(conditions), scores):
                    condition_scores[condition].append(score)
                    stem_scores[stem][condition].append(score)
        return condition_scores, stem_scores
