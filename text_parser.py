import re

from parse_error import ParseError
from help_record import HelpRecord


MAX_LINE_LENGTH = 40


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