import reseval
from .base import Base


###############################################################################
# AB test
###############################################################################


class AB(Base):

    @classmethod
    def analyze(cls, conditions, responses, random_seed=0):
        """Perform statistical analysis on evaluation results"""
        # Get counts of responses for each condition and for each stem
        condition_counts, stem_counts = cls.counts(conditions, responses)

        # Two-sided Binomial test
        results = {
            'binomial': reseval.stats.binomial(
                [condition_counts[condition] for condition in conditions])}

        # Format results
        results = {
            'samples': sum(condition_counts.values()),
            'conditions': {f'{conditions[0]}-{conditions[1]}': results}}

        return results, stem_counts

    @classmethod
    def counts(cls, conditions, responses):
        """Get counts from participant responses"""
        condition_counts = {cond: 0 for cond in conditions}
        stem_counts = {
            stem: {cond: 0 for cond in conditions} for stem in responses}
        for stem, results in responses.items():
            for result in results:
                condition_counts[result] += 1
                stem_counts[stem][result] += 1
        return condition_counts, stem_counts

    @classmethod
    def plot(cls, results, file):
        """Create a plot of the results and save to disk"""
        reseval.plot.barh(results, file)
