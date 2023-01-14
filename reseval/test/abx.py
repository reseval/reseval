import reseval
from .base import Base


###############################################################################
# ABX test
###############################################################################


class ABX(Base):

    @classmethod
    def analyze(cls, conditions, responses, random_seed=0):
        """Perform statistical analysis on evaluation results"""
        conditions = [cond for cond in conditions if cond != 'reference']
        return reseval.test.AB.analyze(conditions, responses, random_seed)

    @classmethod
    def plot(cls, results, file):
        """Create a plot of the results and save to disk"""
        reseval.plot.barh(results, file)
