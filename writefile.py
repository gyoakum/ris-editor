import argparse
import re
import sys

from parse_error import ParseError
from help_record import HelpRecord


MAX_LINE_LENGTH = 40


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


def check_line(line):
    '''Validate the line in the help file'''
    if line.startswith(';='):
        match = re.search(r'^;=\s*\w{1,6}\s*$', line)
        return match.group(1) if match else None
    elif line.startswith('%'):
        match = re.search(r'^%(\d{2}):(\d)$', line)
        return int(match.group(1)), int(match.group(2)) if match else None
    elif line.startswith('.'):
        match = re.search(r'^\.(\d{3})$', line)
        if not match or int(match.group(1)) > 255 :
            return None
        else:
            return match.group(1)
    elif line.startswith(';'):
        if re.search(r'Longest Line:\s*;$', line):
            return line[:-1] + '\x19'
        return line
    else:
        if len(line.encode()) > MAX_LINE_LENGTH:
            return None
        return line


def parse_helpfile(help_file):
    '''Read a plaintext help file and create a list of records'''
    records = []
    current_record = None
    # Put inside a loop
    for line_number, line in enumerate(help_file):
        # print('{:0>3} {}'.format(line_number, line.rstrip()))
        if line.startswith(';='):
            code = line[2:].strip()
            # Enforce maximum code size
            if len(code.encode()) > 6:
                raise ParseError('Record code exceeds maximum length of 6 bytes',
                        line=line,
                        line_number=line_number)
            # start new record
            if current_record:
                records.append(current_record)
            current_record = HelpRecord(code)
        elif line.startswith('%'):
            match = check_line(line.rstrip())
            if match:
                current_record.set_options(*match)
            else:
                raise ParseError('Unable to parse % expression',
                        line=line,
                        line_number=line_number)
        elif line.startswith('.'):
            match = check_line(line.rstrip())
            if match:
                current_record.add_color(match)
            else:
                raise ParseError('Invalid color specifier',
                        line=line,
                        line_number=line_number)
        elif line.startswith(';'):
            match = check_line(line.rstrip())
            current_record.add_comment(match)
        else:
            match = check_line(line.rstrip('\r\n'))
            if match is not None:
                try:
                    current_record.add_line(match)
                except ValueError:
                    raise ParseError('Line exceeds length specifier',
                            line=line,
                            line_number=line_number)
            else:
                raise ParseError('Line exceeds maximum length',
                        line=line,
                        line_number=line_number)
    if current_record:
        records.append(current_record)
    return records


def main(source, output='output.cdr'):
    '''Read in the text version of a help file and produce a binary file'''
    records = []
    with open(source) as f:
        try:
            records = parse_helpfile(f)
        except ParseError as err:
            print(err, file=sys.stderr)
            if err.line_number and err.line:
                print('in line {} "{}"'.format(err.line_number, err.line),
                        file=sys.stderr)
            elif err.line_number:
                print('in line {}'.format(err.line_number),
                        file=sys.stderr)
            elif err.line:
                print('in "{}"'.format(err.line),
                        file=sys.stderr)
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
    args = parser.parse_args()
    # print(args)
    main(**vars(args))
