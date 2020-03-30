class Error(Exception):
    pass

class ParseError(Error):
    '''Indicates an invalid or improper line during parsing'''

    def __init__(self, message, line=None, line_number=None):
        if message:
            self.message = message
        else:
            self.message = None
        self.line = line
        self.line_number = line_number

    def __str__(self):
        if self.message:
            return self.message
        else:
            return 'An error occurred during parsing'

class ValidationError(Error):
    pass

class LineLengthError(Error):

    def __init__(self, message, max_length, line_length):
        self.message = message
        self.max_length = max_length
        self.line_length = line_length
