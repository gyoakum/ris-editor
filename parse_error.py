class ParseError(Exception):
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
