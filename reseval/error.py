class ValidationError(Exception):

    def __init__():
        super().__init__(
            'Validation check failed. Please check that the directory ' +
            'structure of the evaluation files is correct for the type ' +
            'of test you are running.')
