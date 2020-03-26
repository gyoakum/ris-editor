#!/bin/env python3

import argparse;


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
    return colors[color] + string + reset


def get_record_count(help_file):
    '''Read the number of records in the file'''
    count_bytes = help_file.read(4)
    return int.from_bytes(count_bytes, byteorder='little')


def header_size(count = 1):
    '''Return the byte size of some number of headers'''
    return 12 * count


def get_header_tables(help_file, count):
    '''Read in the header tables for the help file and return them'''
    HEADER_START = 4
    HEADER_SIZE = header_size(1)
    headers = []
    for i in range(count):
        code = help_file.read(6).decode().rstrip('\0')
        offset = int.from_bytes(help_file.read(4), byteorder='little')
        size = int.from_bytes(help_file.read(2), byteorder='little')
        headers.append((code, offset, size))
    return headers


def get_records(help_file, headers):
    '''Extract the record entries for the given headers'''
    records = []
    for index, header in enumerate(headers):
        code, offset, size = header
        help_file.seek(offset)
        # text = help_file.read(size).decode().replace('\x19', '\u25A1')
        text = help_file.read(size).decode().replace('\x19', ';')
        records.append({
            'code': code,
            'index': index,
            'text': text
        })
    return records


def write_record_text(text, colorize=False, number_lines=False):
    lines = text.split('\n')
    line_number = 0
    max_lines = -1
    for line in lines:
        if line.startswith((';', '%', '.')):
            if line.startswith('%'):
                max_lines = int(line[1:3]) + 1
            print(line)
        else:
            line_number += 1
            if line_number <= max_lines or max_lines < 0:
                color = 'green'
            else:
                color = 'red'
            if number_lines:
                prefix = '{:02}'.format(line_number)
                if colorize:
                    prefix = colorify(prefix, color)
                print('{} {}'.format(prefix, line))
            else:
                print(line)


def find_record(records, code=None):
    if code:
        return next((x for x in records if x['code'] == code), None)
    return None


def main(args):
    """Output the file in a readable manner"""
    filename = args.filename
    with open(filename, 'rb') as f:
        # Read the file
        count = get_record_count(f)
        headers = get_header_tables(f, count)
        records = get_records(f, headers)
        # print("There are {0} record(s)".format(count))
        # print(headers)
        if args.headers_only:
            print(headers)
            return
        elif args.header:
            record = find_record(records, code=args.header)
            if record:
                write_record_text(record['text'],
                        colorize=args.color,
                        number_lines=args.lines)
            return
        for record in records:
            print(';={}'.format(record['code']))
            write_record_text(record['text'],
                    colorize=args.color,
                    number_lines=args.lines)


if __name__ == '__main__':
    # print('Hello world!')
    parser = argparse.ArgumentParser(description='Process a help file')
    parser.add_argument('filename', nargs='?', default='help.cdr',
            help='Path to the help file (default ./help.cdr)')
    parser.add_argument('-c', '--color', action='store_true',
            help='Enable ANSI console colors')
    parser.add_argument('-l', '--lines', action='store_true',
            help='Print line numbers alongside record text')
    parser.add_argument('--headers-only', action='store_true',
            help='Print only header data')
    parser.add_argument('--header',
            help='Select a specific header to view')
    args = parser.parse_args()
    main(args)
