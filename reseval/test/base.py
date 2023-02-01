import os
import random
from abc import ABC, abstractmethod

import reseval


###############################################################################
# Abstract base test class
###############################################################################


class Base(ABC):

    def __init__(self, config, directory):
        self.directory = directory
        self.random_seed = config['random_seed']
        self.participants = config['participants']
        self.samples_per_participant = config['samples_per_participant']

        # Get all files in directory relative to the directory
        self.files = [
            file.relative_to(directory)
            for file in directory.rglob('*') if file.is_file()]

        # Get the set of conditions
        self.conditions = sorted([
            path.name for path in directory.iterdir() if path.is_dir()])

    @classmethod
    @abstractmethod
    def analyze(cls, conditions, responses, random_seed=0):
        """Perform statistical analysis on evaluation results"""
        pass

    def assign(self, random_seed=0):
        """Randomly assign files to each participant"""
        # Seed random number generation
        random.seed(random_seed)

        # Get shuffled files
        files = [
            stem.replace("\\", "/") + extension
            for stem, extension in self.stems_and_extensions()]
        random.shuffle(files)

        # Assign stems to participants
        index = 0
        samples = self.samples_per_participant
        assignments, residual = [], []

        # We generate more assignments than the expected number of participants
        # in case participants leave during the test or we extend the test
        while len(assignments) < 10 * self.participants:

            # Shuffle and reset index whenever we reach the end
            while index + samples - len(residual) >= len(files):
                residual.extend(files[index:])
                random.shuffle(files)
                index = 0

            # Add assignment
            end = index + samples - len(residual)
            assignments.append(residual + files[index:end])
            index = end

            # Reset residual
            residual = []

        return assignments

    @classmethod
    def plot(cls, results, file):
        """Create a plot of the results and save to disk"""
        pass

    def response_type(self):
        """Retrieve the MySQL datatype of a participant response"""
        # By default, the response type is the name of the winning condition.
        max_length = max([len(condition) for condition in self.conditions])
        return f'varchar({max_length})'

    def stems(self):
        """Retrieve the file stems to be uploaded to the database"""
        return [stem for stem, _ in self.stems_and_extensions()]

    def stems_and_extensions(self):
        """Retrieve file stems and extensions to be updated to the database"""
        if self.conditions:
            cond = sorted([
                file for file in self.files
                if file.parts[0] == self.conditions[0]])
            return [os.path.splitext('/'.join(file.parts[1:])) for file in cond]
        return [(file.stem, file.suffix) for file in self.files]

    def validate(self):
        """Perform validation on the directory of files to evaluate"""
        # Use first condition as reference
        common = sorted([
            file for file in self.files
            if file.parts[0] == self.conditions[0]])

        # All subsequent conditions must match
        for condition in self.conditions[1:]:
            files = sorted([
                file for file in self.files if file.parts[0] == condition])

            # Check lengths
            if len(files) != len(common):
                raise reseval.ValidationError()

            # Check file matches
            for a, b in zip(files, common):
                if a.parts[1:].join('/') != b.parts[1:].join('/'):
                    raise reseval.ValidationError()
