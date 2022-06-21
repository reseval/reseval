import itertools

import reseval
from .base import Base


###############################################################################
# MOS test
###############################################################################


class MOS(Base):

    @classmethod
    def analyze(cls, conditions, responses, random_seed=0):
        """Perform statistical analysis on evaluation results"""
        # Get MOS ratings
        condition_scores, stem_scores = cls.scores(conditions, responses)

        # Iterate over unique pairs of conditions
        samples = sum(len(scores) for scores in condition_scores.values())
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
            results['mannwhitney'] = reseval.stats.mannwhitney(
                condition_scores[condition_a],
                condition_scores[condition_b])

            all_results['conditions'][f'{condition_a}-{condition_b}'] = results

        return all_results, stem_scores

    @classmethod
    def plot(self, results, file):
        """Create a plot of the results and save to disk"""
        reseval.plot.violin(results, file, range(0, 6))

    def response_type(self):
        """Retrieve the MySQL datatype of a participant response"""
        # For MOS, we store the condition of the file presented to the
        # participant as well as the score given to the file by the participant
        # (an integer 1-5 inclusive). The format is "<condition>-<score>".
        max_length = max([len(condition) for condition in self.conditions])
        return f'varchar({max_length + 2})'

    @classmethod
    def scores(cls, conditions, responses):
        """Get scores from participant responses"""
        condition_scores = {cond: [] for cond in conditions}
        stem_scores = {
            stem: {cond: [] for cond in conditions} for stem in responses}
        for stem, results in responses.items():
            for result in results:
                parts = result.split('-')
                condition, score = '-'.join(parts[:-1]), int(parts[-1])
                condition_scores[condition].append(score)
                stem_scores[stem][condition].append(score)
        return condition_scores, stem_scores
