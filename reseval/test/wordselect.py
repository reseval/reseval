import numpy as np

import reseval
from .base import Base


###############################################################################
# Word selection test
###############################################################################


class WordSelect(Base):

    def __init__(self, config, directory):
        super().__init__(config, directory)

        # Filter text files
        self.files = [
            file for file in self.files
            if not file.name.endswith('-words.txt')]

    @classmethod
    def analyze(cls, conditions, responses, random_seed=0):
        """Perform statistical analysis on evaluation results"""
        # Get number of times each stem is annotated
        stem_counts = {
            stem: len(response) for stem, response in responses.items()}

        # Get total number of annotations
        results = {
            'samples': sum(stem_counts.values()),
            'scores': cls.parse(responses) }

        return results, stem_counts

    @classmethod
    def parse(cls, responses):
        """Parse responses to produce per-word emphasis scores"""
        results = {}
        for stem, scores in responses.items():
            scores = np.array([
                [float(character) for character in score] for score in scores])
            results[stem] = scores.mean(axis=0).tolist()
        return results

    def response_type(self):
        """Retrieve the MySQL datatype of a participant response"""
        # For WordSelect, we store an array of booleans indicating whether each
        # word was selected. We assume a maximum of 255 words.
        return 'varchar(255)'

    def validate(self):
        """Perform validation on the directory of files to evaluate"""
        super().validate()

        # Iterate over files
        for stem, _ in self.stems_and_extensions():

            # Ensure corresponding text file is present
            if not (self.directory / f'{stem}-words.txt').exists():
                raise reseval.ValidationError()
