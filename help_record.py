import re

from errors import LineLengthError

class HelpRecord:
    """An entry specifying dialog text for raceintospace"""

    def __init__(self, code):
        self.code = code
        self.max_lines = 0
        self.line_count = 0
        self.max_line_length = None
        self.text = []

    def __str__(self):
        return '\r\n'.join(self.text)

    def size(self):
        ''' The size of the header in bytes'''
        return len(str(self).encode())

    def set_options(self, line_count, mode):
        self.max_lines = line_count
        if line_count < 0 or line_count > 99:
            raise ValueError('Line count must be a two-digit value')
        if mode not in range(0, 10):
            raise ValueError('Mode must be a single digit value')
        self.text.append('%{:0>2}:{}'.format(line_count, mode))

    def add_line(self, line):
        if self.max_line_length and len(line) > self.max_line_length:
            raise LineLengthError('Line longer than specified maximum',
                    max_length = self.max_line_length,
                    line_length = len(line))
        # elif self.max_lines <= self.line_count:
        self.text.append(line)
        self.line_count += 1

    def add_comment(self, comment):
        # Check for longest line
        if len(self.text) > 0 and re.search('Longest Line:', self.text[-1]):
            self.max_line_length = len(comment)
        self.text.append(comment)

    def add_color(self, color):
        for line in reversed(self.text):
            if line.startswith(('%', ';')):
                continue
            if line.startswith('.'):
                raise ValueError('Normal line required between color changes')
            else:
                break
        self.text.append('.{}'.format(color))
