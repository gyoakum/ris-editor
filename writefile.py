import argparse
import sys

from errors import ParseError
from text_parser import parse_helpfile


def colorify(string, color):
    '''Add ANSI escape codes to color console output'''
    colors = {
        'black': '\u001b[30m',
        'red': '\u001b[31m',
        'green': '\u001b[32m',
        'yellow': '\u001b[33m',
        'blue': '\u001b[34m',
        'magenta': '\u001b[35m',
        'cyan': '\u001b[36m',
        'white': '\u001b[37m'
    }
    reset = '\u001b[0m'
    if color not in colors:
        raise ValueError('{} not a recognized color'.format(color))
    return colors[color] + str(string) + reset


class Logger:

    def __init__(self, color=True):
        self.color = color

    def print_line(self, line=None, line_number=0):
        """Print the line number and line content"""
        if line is not None and line_number:
            if self.color:
                print('{} {}'.format(
                    colorify(line_number, 'magenta'),
                    line.rstrip('\r\n')),
                    file=sys.stderr)
            else:
                print('  in line {} "{}"'.format(line_number,
                    line.rstrip('\r\n')),
                    file=sys.stderr)
        elif line_number:
            print('  in line {}'.format(line_number),
                    file=sys.stderr)
        elif line is not None:
            print('  in "{}"'.format(line.rstrip('\r\n')),
                    file=sys.stderr)

    def error(self, message, line=None, line_number=0):
        """Print an error message"""
        print('{}: {}'.format(
            colorify('Error', 'red') if self.color else 'Error',
            message),
            file=sys.stderr)
        self.print_line(line=line, line_number=line_number)

    def warn(self, message, line=None, line_number=0):
        """Print the warning message"""
        print('{}: {}'.format(
            colorify('Warning', 'yellow') if self.color else 'Warning',
            message),
            file=sys.stderr)
        self.print_line(line=line, line_number=line_number)


def create_headers(records, offset = 4):
    '''Create an array of header entry tuples for looking up the records'''
    # Each header tuple is 12 bytes, and the first record begins after the
    # end of the headers
    offset += 12 * len(records)
    headers = []
    for record in records:
        code = record.code.encode().ljust(6, b'\0')
        size = record.size().to_bytes(2, byteorder='little')
        header = code + offset.to_bytes(4, byteorder='little') + size
        headers.append(header)
        offset += record.size()
    return headers


def write_file(help_file, records):
    '''Compose and write a lookup file with headers for the help entries'''
    headers = create_headers(records)
    # The first four bytes of the file are the number of help entries
    help_file.write(len(records).to_bytes(4, byteorder='little'))
    help_file.write(b''.join(headers))
    for record in records:
        record_bytes = str(record).encode()
        help_file.write(record_bytes)


def main(source, output='output.cdr',
        no_color=False, no_trailing=False):
    '''Read in the text version of a help file and produce a binary file'''
    records = []
    color = False if no_color else sys.stderr.isatty()
    allow_trailing = not no_trailing
    logger = Logger(color=color)
    with open(source) as f:
        try:
            records = parse_helpfile(f, warn=logger.warn,
                    allow_trailing=allow_trailing)
        except ParseError as err:
            logger.error(err.message,
                    line=err.line,
                    line_number=err.line_number)
            return
    if output:
        with open(output, 'wb') as out_file:
            write_file(out_file, records)
    else:
        for record in records:
            print(';={}'.format(record.code))
            print(record)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Save a help file')
    parser.add_argument('source',
            help='Input file to convert into a cdr')
    parser.add_argument('-o', '--output', default='output.cdr',
            help='Output destination')
    parser.add_argument('--no-color', default=False, action='store_true',
            help='Disable color output')
    parser.add_argument('--no-trailing',
            default=False,
            action='store_true',
            help='Forbid trailing lines after those allocated'),
    args = parser.parse_args()
    main(**vars(args))
