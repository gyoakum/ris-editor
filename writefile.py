import argparse
import sys

from parse_error import ParseError
from text_parser import parse_helpfile


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
